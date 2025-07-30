import re
import time
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from difflib import SequenceMatcher
from contextlib import contextmanager
from difflib import get_close_matches
from sqlalchemy import create_engine, text
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy connectable*")

# mengambil data dari PostgreSQL
def get_data_from_postgres():
    conn = psycopg2.connect(
        dbname="replikasipdj-bigdata",
        user="postgres",
        password="2lNyRKW3oc9kan8n",
        host="103.183.92.158",
        port="5432"
    )

    schemas = input("Masukkan nama Schemas: ").strip()
    tables = input("Masukkan nama Tables: ").strip()

    cursor = conn.cursor()
    query = f"SELECT * FROM {schemas}.{tables};"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    df = pd.DataFrame(rows, columns=columns)

    # kapitalisasi, hapus spasi berlebih, ubah underscore ke spasi
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip().str.upper().str.replace('_', ' ', regex=False)

    if 'kode_provinsi' not in df.columns:
        df['kode_provinsi'] = '35'
    if 'nama_provinsi' not in df.columns:
        df['nama_provinsi'] = 'JAWA TIMUR'

    return df, schemas, tables

# mengubah format kolom periode_update
def periode_update(periode_str):
    month_mapping = {
        'JANUARI': '01', 'FEBRUARI': '02', 'MARET': '03', 'APRIL': '04',
        'MEI': '05', 'JUNI': '06', 'JULI': '07', 'AGUSTUS': '08',
        'SEPTEMBER': '09', 'OKTOBER': '10', 'NOVEMBER': '11', 'DESEMBER': '12'
    }

    triwulan_mapping = {'I': 'Q1', 'II': 'Q2', 'III': 'Q3', 'IV': 'Q4'}
    caturwulan_mapping = {'I': 'C1', 'II': 'C2', 'III': 'C3'}
    semester_mapping = {'I': 'S1', 'II': 'S2'}

    if not isinstance(periode_str, str):
        return periode_str

    periode_str = periode_str.strip().upper()

    # hapus tanggal
    if periode_str and periode_str.split()[0].isdigit():
        parts = periode_str.split(maxsplit=1)
        if len(parts) > 1:
            periode_str = parts[1]

    parts = periode_str.strip().split()

    if len(parts) == 2:
        if parts[0] == 'TAHUN':
            return parts[1]
        elif parts[0] in month_mapping:
            bulan = month_mapping[parts[0]]
            return f"{parts[1]}-{bulan}"
    elif len(parts) == 3:
        tipe = parts[0]
        nomor = parts[1]
        tahun = parts[2]

        if tipe == 'SEMESTER' and nomor in semester_mapping:
            return f"{tahun}-{semester_mapping[nomor]}"
        elif tipe == 'TRIWULAN' and nomor in triwulan_mapping:
            return f"{tahun}-{triwulan_mapping[nomor]}"
        elif tipe == 'CATURWULAN' and nomor in caturwulan_mapping:
            return f"{tahun}-{caturwulan_mapping[nomor]}"

    return periode_str

# mendeteksi tingkat wilayah berdasarkan kolom
def jenis_wilayah(df):
    def similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    def get_similarity_scores(cols):
        target = ['nama_provinsi', 'nama_kabupaten', 'nama_kecamatan', 'desa_kelurahan']
        return {
            key: max(((col, similarity(key, col)) for col in cols), key=lambda x: x[1])
            for key in target
        }

    # deteksi eksplisit kolom
    kolom = [col.lower() for col in df.columns]
    kelurahan = any(k in kolom for k in ['nama_kelurahan/desa', 'nama_kelurahan', 'nama_desa', 'kelurahan', 'desa'])
    kecamatan = any(k in kolom for k in ['nama_kecamatan', 'kecamatan'])
    kabupaten = any(k in kolom for k in ['nama_kabupaten', 'kabupaten', 'kabupaten_kota'])
    provinsi = any(k in kolom for k in ['nama_provinsi', 'provinsi'])

    if provinsi and not (kabupaten or kecamatan or kelurahan):
        return 'data_provinsi'
    elif kelurahan:
        return 'data_kelurahan'
    elif kecamatan:
        return 'data_kecamatan'
    elif kabupaten:
        return 'data_kabupaten'

    # similarity jika struktur tidak dikenali
    scores = get_similarity_scores(df.columns.tolist())
    np, nk, nc, nd = scores['nama_provinsi'][1], scores['nama_kabupaten'][1], scores['nama_kecamatan'][1], scores['desa_kelurahan'][1]

    if np > 0.75 and nk <= 0.75 and nc <= 0.75 and nd <= 0.75:
        return 'data_provinsi'
    elif np > 0.75 and nk > 0.75 and nc <= 0.75 and nd <= 0.75:
        return 'data_kabupaten'
    elif np > 0.75 and nk > 0.75 and nc > 0.75 and nd <= 0.75:
        return 'data_kecamatan'
    elif np > 0.75 and nk > 0.75 and nc > 0.75 and nd > 0.75:
        return 'data_kelurahan'
    else:
        return 'data_unknown'

def jenis_data(df):
    while True:
        jenis = input(
            "Pilih jenis data (transaksi/agregat). Ketik (t) untuk transaksi, ketik (a) untuk agregat, atau (t/a): ").strip().lower()

        if jenis in ['t', '0']:
            jenis_text = 'transaksi'
            df = transaksi(df)
            break
        elif jenis in ['a', '1']:
            jenis_text = 'agregat'
            df = agregat(df)
            break
        else:
            print("Jenis data tidak dikenali. Ketik (t) untuk transaksi, (a) untuk agregat, atau (t/a)")

    return df, jenis_text

def kabupaten(df):
        # koneksi ke database PostgreSQL
        conn_b = psycopg2.connect(
            dbname="result_cleansing",
            user="postgres",
            password="2lNyRKW3oc9kan8n",
            host="103.183.92.158",
            port="5432"
        )

        # data master kabupaten
        schemas_b = "masterdata"
        tables_b = "masterkabupaten"
        cursor_b = conn_b.cursor()
        query_b = f"SELECT * FROM {schemas_b}.{tables_b};"
        cursor_b.execute(query_b)
        rows_b = cursor_b.fetchall()
        columns = [desc[0] for desc in cursor_b.description]
        cursor_b.close()
        conn_b.close()

        data_kabupaten = pd.DataFrame(rows_b, columns=columns)

        # rename kolom jika menggunakan nama 'kab_kota'
        if 'kab_kota' in df.columns and 'kabupaten_kota' not in df.columns:
            df = df.rename(columns={'kab_kota': 'kabupaten_kota'})

        if 'kabupaten_kota' in df.columns:
            # pastikan string dan normalisasi huruf besar
            df['kabupaten_kota'] = df['kabupaten_kota'].astype(str).str.strip().str.upper()

            # normalisasi berbagai format 'kabupaten'
            df['kabupaten_kota'] = df['kabupaten_kota'].str.replace(r'^KAB[\./\s\-]*', 'KABUPATEN ', regex=True)
            df['kabupaten_kota'] = df['kabupaten_kota'].str.replace(r'^KOTA[\./\s\-]*', 'KOTA ', regex=True)

            # jika belum diawali 'KOTA ' atau 'KABUPATEN ', tambahkan awalan 'KABUPATEN '
            df['kabupaten_kota'] = df['kabupaten_kota'].apply(
                lambda x: 'KABUPATEN ' + x if not x.startswith('KOTA ') and not x.startswith('KABUPATEN ') else x)

            # join ke master kabupaten
            df = df.merge(
                data_kabupaten[['kode_kabupaten_kota', 'nama_kabupaten_kota']],
                left_on='kabupaten_kota',
                right_on='nama_kabupaten_kota',
                how='left'
            )

            # drop kolom kabupaten_kota
            df = df.drop(columns=['kabupaten_kota'])

        return df

def kecamatan(df):
    # koneksi ke database PostgreSQL
    conn_c = psycopg2.connect(
        dbname="result_cleansing",
        user="postgres",
        password="2lNyRKW3oc9kan8n",
        host="103.183.92.158",
        port="5432"
    )

    # data master kabupaten
    schemas_c = "masterdata"
    tables_c = "masterkecamatan"
    cursor_c = conn_c.cursor()
    query_c = f"SELECT * FROM {schemas_c}.{tables_c};"
    cursor_c.execute(query_c)
    rows_c = cursor_c.fetchall()
    columns = [desc[0] for desc in cursor_c.description]
    cursor_c.close()
    conn_c.close()

    data_kecamatan = pd.DataFrame(rows_c, columns=columns)

    # normalisasi
    df["kecamatan"] = df["kecamatan"].str.replace(r"(?i)\bkecamatan\b", "", regex=True).str.strip()

    # join ke master desa
    df = df.merge(data_kecamatan[['bps_kode_kecamatan', 'bps_nama_kecamatan', 'kode_kabupaten_kota', 'nama_kabupaten_kota']],
              left_on='kecamatan',
              right_on='bps_nama_kecamatan',
              how='left')

    # drop kolom kecamatan
    df = df.drop(columns=['kecamatan'])

    return df

def kelurahan(df, status, col, special_case=None, preference='kemendagri'):
    # koneksi master desa
    def conn_d():
        conn_d = psycopg2.connect(
            dbname="result_cleansing",
            user="postgres",
            password="2lNyRKW3oc9kan8n",
            host="103.183.92.158",
            port="5432"
        )
        cursor_d = conn_d.cursor()
        query = "SELECT * FROM masterdata.masterdesa;"
        cursor_d.execute(query)
        rows_d = cursor_d.fetchall()
        columns_d = [desc[0] for desc in cursor_d.description]
        cursor_d.close()
        conn_d.close()
        return pd.DataFrame(rows_d, columns=columns_d)

    # preprocessing lokasi
    def prepare_location_columns(df, kelurahan_col, kecamatan_col, kabupaten_col, prefix=''):
        df = df.copy()
        df = df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)
        df[f'kabupaten_{prefix}'] = df[kabupaten_col].str.replace("KAB.", "KABUPATEN", regex=False).apply(lambda x: f"KABUPATEN {x}" if " " not in x else x)
        for colname, newname in zip([kelurahan_col, kecamatan_col], [f'kelurahan_{prefix}', f'kecamatan_{prefix}']):
            df[newname] = (df[colname]
                .str.replace(" ", "", regex=False)
                .str.replace(r'[^\w\s]', '', regex=True)
                .str.replace(r'[\'\"\`]', '', regex=True)
                .str.replace(r'[\n\r\t]', '', regex=True)
                .str.strip())
        df[f'lokasi_{prefix}_desa'] = df[[f'kelurahan_{prefix}', f'kecamatan_{prefix}', f'kabupaten_{prefix}']].fillna('').agg(', '.join, axis=1)
        return df

    # TF-IDF Matching
    def match_locations_tfidf(df_target, df_reference, col_target, col_reference, output_col, score_col, preference):
        texts_target = df_target[col_target].fillna('').tolist()
        texts_reference = df_reference[col_reference].fillna('').tolist()
        all_text = texts_target + texts_reference
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_text)
        tfidf_target = tfidf_matrix[:len(texts_target)]
        tfidf_ref = tfidf_matrix[len(texts_target):]
        cosine_sim = cosine_similarity(tfidf_target, tfidf_ref)
        best_matches = cosine_sim.argmax(axis=1)
        match_scores = cosine_sim.max(axis=1)
        df_target[f'kelurahan_{preference}'] = [df_reference.iloc[i][f'kelurahan_{preference}'] for i in best_matches]
        df_target[f'kecamatan_{preference}'] = [df_reference.iloc[i][f'kecamatan_{preference}'] for i in best_matches]
        df_target['kabupaten_master'] = [df_reference.iloc[i]['nama_kabupaten_kota'] for i in best_matches]
        df_target[output_col] = [texts_reference[i] for i in best_matches]
        df_target[score_col] = match_scores
        return df_target

    # fix berdasarkan special case
    def fix_inconsistent_case(df, tfidf_threshold=0.99):
        matched = df[df['tfidf_score'] > tfidf_threshold][[special_case, f'lokasi_edit_desa', f'lokasi_{preference}_desa']]
        mapping = matched.drop_duplicates(special_case).set_index(special_case).to_dict(orient='index')
        def fix(row):
            if row[special_case] in mapping and row['tfidf_score'] < tfidf_threshold:
                row[f'lokasi_edit_desa'] = mapping[row[special_case]][f'lokasi_edit_desa']
                row[f'lokasi_{preference}_desa'] = mapping[row[special_case]][f'lokasi_{preference}_desa']
                row['tfidf_score'] = tfidf_threshold
            return row
        return df.apply(fix, axis=1)

    # koreksi kecamatan/kelurahan
    def correct_kecamatan_kelurahan(kabupaten, kecamatan, kelurahan, master_df, preference, cutoff=0.6):
        df_kec = master_df[(master_df['nama_kabupaten_kota'].str.upper() == kabupaten.upper()) &
                           (master_df[f'kelurahan_{preference}'].str.upper() == kelurahan.upper())]
        kecamatan_baru = kecamatan
        if not df_kec.empty:
            match = get_close_matches(kecamatan.upper(), [k.upper() for k in df_kec[f'kecamatan_{preference}'].unique()], n=1, cutoff=cutoff)
            if match:
                kecamatan_baru = next(k for k in df_kec[f'kecamatan_{preference}'].unique() if k.upper() == match[0])
        df_kel = master_df[(master_df['nama_kabupaten_kota'].str.upper() == kabupaten.upper()) &
                           (master_df[f'kecamatan_{preference}'].str.upper() == kecamatan_baru.upper())]
        kelurahan_baru = kelurahan
        if not df_kel.empty:
            match = get_close_matches(kelurahan.upper(), [k.upper() for k in df_kel[f'kelurahan_{preference}'].unique()], n=1, cutoff=cutoff)
            if match:
                kelurahan_baru = next(k for k in df_kel[f'kelurahan_{preference}'].unique() if k.upper() == match[0])
        return kecamatan_baru, kelurahan_baru, f"{kelurahan_baru}, {kecamatan_baru}, {kabupaten}"

    # proses data desa
    masterdesa = conn_d()

    df_preprocess = prepare_location_columns(df, col['desa_kelurahan'], col['nama_kecamatan'], col['kabupaten_kota'], prefix='edit')
    masterdesa = prepare_location_columns(masterdesa, "kemendagri_nama_desa_kelurahan", "kemendagri_nama_kecamatan", "nama_kabupaten_kota", prefix=preference)

    df_preprocess = match_locations_tfidf(df_preprocess, masterdesa, f'lokasi_edit_desa', f'lokasi_{preference}_desa', f'lokasi_{preference}_desa', 'tfidf_score', preference)

    if special_case:
        df_preprocess = fix_inconsistent_case(df_preprocess)

    df_unmatch = df_preprocess[df_preprocess['tfidf_score'] < 0.99]
    df_unmatch[['kecamatan_masterdesa_fix', 'kelurahan_masterdesa_fix', 'lokasi_masterdesa_fix_desa']] = df_unmatch.apply(
        lambda x: correct_kecamatan_kelurahan(x['kabupaten_edit'], x['kecamatan_edit'], x['kelurahan_edit'], masterdesa, preference), axis=1, result_type='expand'
    )

    df_unmatch = match_locations_tfidf(df_unmatch, masterdesa, 'lokasi_masterdesa_fix_desa', f'lokasi_{preference}_desa', f'lokasi_{preference}_desa', 'tfidf_score', preference)

    df_match = df_preprocess[df_preprocess['tfidf_score'] >= 0.99]
    df_isi = pd.concat([df_match, df_unmatch[df_unmatch['tfidf_score'] >= 0.99]]).sort_values(by='id').reset_index(drop=True)

    df_isi_merge = df_isi[list(df.columns) + [f'lokasi_{preference}_desa']].merge(
        masterdesa.drop(columns=['kode_provinsi', 'nama_provinsi'], errors='ignore'),
        on=f'lokasi_{preference}_desa',
        how='left'
    )

    df_kosong = df_unmatch[df_unmatch['tfidf_score'] < 0.99].copy()
    df_kosong[col['kabupaten_kota']] = df_kosong[col['kabupaten_kota']].str.replace("KAB.", "KABUPATEN", regex=False).apply(lambda x: f"KABUPATEN {x}" if " " not in x else x)
    df_kosong.rename(columns={
        col['kabupaten_kota']: 'nama_kabupaten_kota',
        col['nama_kecamatan']: 'kemendagri_nama_kecamatan',
        col['desa_kelurahan']: 'kemendagri_nama_desa_kelurahan'
    }, inplace=True)

    df_concat = pd.concat([df_isi_merge, df_kosong], ignore_index=True).sort_values(by='id').reset_index(drop=True)
    df_concat = df_concat.fillna('0')

    kolom_buang = [
        'provinsi', 'kabupaten', 'kecamatan', 'kelurahan',
        f'lokasi_{preference}_desa', 'kabupaten_master',
        'tfidf_score', 'lokasi_edit_desa',
        'kabupaten_edit', 'kelurahan_edit', 'kecamatan_edit',
        'kecamatan_masterdesa_fix', 'kelurahan_masterdesa_fix',
        'lokasi_masterdesa_fix_desa', 'kabupaten_kemendagri',
        'kecamatan_kemendagri', 'kelurahan_kemendagri'
    ]
    df_concat = df_concat.drop(columns=[col for col in kolom_buang if col in df_concat.columns])

    return df_concat

def agregat(df):
    # membuat kolom 'periode_update' jika belum ada
    if 'periode_update' not in df.columns:
        if 'periode' in df.columns:
            df['periode_update'] = pd.to_datetime(df['periode'], errors='coerce')
        elif 'tahun' in df.columns:
            df['periode_update'] = pd.to_datetime(df['tahun'].astype(str) + '-01-01', errors='coerce')

    # membuat kolom 'tahun' jika belum ada
    if 'tahun' not in df.columns and 'periode_update' in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df['periode_update']):
            df['tahun'] = df['periode_update'].dt.year.astype(str)
        else:
            df['tahun'] = df['periode_update'].astype(str).str[:4]

    drop_cols = []

    # cek apakah seluruh isi kolom kosong atau hanya berisi '-'
    def kolom_kosong(series):
        return ~series.dropna().astype(str).str.strip().ne('-').any()

    # cek kolom 'kategori'
    if 'kategori' in df.columns:
        if kolom_kosong(df['kategori']):
            drop_cols.append('kategori')

    # cek kolom 'jumlah'
    if 'jumlah' in df.columns:
        if kolom_kosong(df['jumlah']):
            drop_cols.append('jumlah')

    # drop kolom sesuai hasil cek
    if drop_cols:
        df = df.drop(columns=drop_cols, errors='ignore')

    # drop kolom tak terpakai lainnya
    drop = ['periode', 'bulan', 'tanggal']
    df = df.drop(columns=[col for col in drop if col in df.columns], errors='ignore')

    # daftar kolom yang dilewati saat transpose
    skip_cols = [
        'id_index', 'id',
        'kode_provinsi', 'nama_provinsi',
        'kode_kabupaten_kota', 'nama_kabupaten_kota',
        'bps_kode_kecamatan', 'bps_nama_kecamatan',
        'bps_kode_desa_kelurahan', 'bps_nama_desa_kelurahan',
        'kemendagri_kode_kecamatan', 'kemendagri_nama_kecamatan',
        'kemendagri_kode_desa_kelurahan', 'kemendagri_nama_desa_kelurahan',
        'periode_update', 'satuan', 'tahun'
    ]

    other_cols = [col for col in df.columns if col not in skip_cols]

    # deteksi kolom numerik (termasuk object mayoritas numerik)
    num_cols = []
    for col in other_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            num_cols.append(col)
        else:
            try:
                ser = pd.to_numeric(df[col].fillna(0), errors='coerce')
                if ser.notna().mean() >= 0.6:
                    num_cols.append(col)
            except:
                continue

    # konversi num_cols ke numeric, isi NaN dengan 0
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # ubah float yang isinya integer utuh menjadi int
    for col in num_cols:
        if np.allclose(df[col], df[col].astype(int)):
            df[col] = df[col].astype(int)

    value_columns = [col for col in num_cols if pd.api.types.is_integer_dtype(df[col])]

    if not value_columns:
        print("⚠ Tidak ditemukan kolom integer untuk ditranspose.")
        print("Daftar kolom saat ini:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
        user_input = input("Masukkan indeks kolom yang ingin ditranspose (pisahkan dengan koma): ")
        try:
            indices = [int(i.strip()) for i in user_input.split(',')]
            value_columns = [df.columns[i] for i in indices if 0 <= i < len(df.columns) and df.columns[i] not in skip_cols]
        except Exception:
            print("❌ Input tidak valid.")
            return df

        if not value_columns:
            print("❌ Tidak ada kolom valid yang dipilih.")
            return df

    print("✅ Kolom yang akan ditranspose:", value_columns)

    id_vars = [col for col in df.columns if col not in value_columns and col not in ['kategori', 'jumlah']]

    df_melted = df.melt(
        id_vars=id_vars,
        value_vars=value_columns,
        var_name='kategori',
        value_name='jumlah'
    )

    # normalisasi object
    for col in df_melted.select_dtypes(include='object').columns:
        df_melted[col] = (
            df_melted[col]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace('_', ' ', regex=False)
            .apply(lambda x: re.sub(r'\b(\w+)\s+\1\b', r'\1-\1', x, flags=re.IGNORECASE))
        )

    # mengurutkan agar selang-seling
    df_melted['_order'] = df_melted.groupby('kategori').cumcount()
    df_melted = df_melted.sort_values('_order').drop(columns=['_order']).reset_index(drop=True)

    df_melted['jumlah'] = df_melted['jumlah'].fillna(0)

    return df_melted

def transaksi(df):    
    # cek dan buat kolom 'periode_update' jika belum ada
    if 'periode_update' not in df.columns:
        if 'periode' in df.columns:
            df['periode_update'] = pd.to_datetime(df['periode'], errors='coerce')
        elif 'tahun' in df.columns:
            df['periode_update'] = pd.to_datetime(df['tahun'].astype(str) + '-01-01', errors='coerce')

    # cek dan buat kolom 'tahun' jika belum ada
    if 'tahun' not in df.columns and 'periode_update' in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df['periode_update']):
            df['tahun'] = df['periode_update'].dt.year.astype(str)
        else:
            df['tahun'] = df['periode_update'].astype(str).str[:4]

    # daftar kolom default yang mau di-drop
    drop = ['kategori', 'jumlah', 'periode', 'bulan', 'tanggal']

    # mengecek apakah kolom bisa di-drop
    def is_column_empty(colname):
        if colname not in df.columns:
            return True  # tidak ada, anggap kosong
        return df[colname].replace('-', pd.NA).isna().all()

    # cek kolom kategori
    if 'kategori' in drop and not is_column_empty('kategori'):
        drop.remove('kategori')

    # cek kolom jumlah
    if 'jumlah' in drop and not is_column_empty('jumlah'):
        drop.remove('jumlah')

    # drop kolom yang masih ada di dataframe
    df = df.drop(columns=[col for col in drop if col in df.columns], errors='ignore')

    return df

def id_index(df):
    # buat 'id_index' dari nomor urut + id (keduanya sebagai string)
    df['id_index'] = (df.index + 1).astype(str) + df['id'].astype(str)

    # konversi kembali ke integer
    df['id_index'] = df['id_index'].astype(int)

    # pindahkan 'id_index' ke kolom pertama
    cols = ['id_index'] + [col for col in df.columns if col != 'id_index']
    df = df[cols]

    return df

def final(df):
    final_columns = [
        'id_index',
        'id',
        'kode_provinsi',
        'nama_provinsi',
        'kode_kabupaten_kota',
        'nama_kabupaten_kota',
        'bps_kode_kecamatan',
        'bps_nama_kecamatan',
        'bps_kode_desa_kelurahan',
        'bps_nama_desa_kelurahan',
        'kemendagri_kode_kecamatan',
        'kemendagri_nama_kecamatan',
        'kemendagri_kode_desa_kelurahan',
        'kemendagri_nama_desa_kelurahan',
        'kolom x',
        'periode_update',
        'kategori',
        'jumlah',
        'satuan',
        'tahun',
        'jenis_data'
    ]

    # kolom yang ada di df dan ada di final_columns
    recognized = [col for col in final_columns if col in df.columns]
    # kolom tidak dikenal yang ada di df tapi tidak ada di final_columns
    kolom_x = [col for col in df.columns if col not in final_columns]

    # isi NaN di kolom_x
    for col in kolom_x:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna('-')

    x = []
    for col in final_columns:
        if col == 'kolom x':
            x.extend(kolom_x)
        elif col in recognized:
            x.append(col)

    # jika 'kolom x' tidak ada di referensi akan sisipkan di akhir
    if 'kolom x' not in final_columns:
        x.extend(kolom_x)

    return df[x]

def preview_data(df):
    print("\nPreview akhir:", flush=True)
    print(tabulate(df.head(10), headers='keys', tablefmt='psql'), flush=True)

    while True:
        keputusan = input("\nApakah data sudah sesuai dan ingin disimpan? Ketik (y) yes/setuju, ketik (n) no/tidak setuju. (y/n): ").strip().lower()
        if keputusan in ['y', 'n']:
            break
        print("Input tidak dikenali, ketik (y) yes/setuju, ketik (n) no/tidak setuju. (y/n)", flush=True)

    return keputusan == 'y'

def simpan(df, schemas, tables, level_wilayah):
    primary_key = "id_index"
    index_col = None

    # deteksi nama kolom index berdasarkan level wilayah
    if level_wilayah == "data_kabupaten":
        index_col = "nama_kabupaten_kota"
    elif level_wilayah == "data_kecamatan":
        index_col = "bps_nama_kecamatan"
    elif level_wilayah == "data_kelurahan":
        index_col = "bps_nama_desa_kelurahan"

    # buat schema jika belum ada
    conn = psycopg2.connect(
        dbname="result_cleansing",
        user="postgres",
        password="2lNyRKW3oc9kan8n",
        host="103.183.92.158",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schemas};")
    conn.commit()
    cursor.close()
    conn.close()

    engine = create_engine(f'postgresql://postgres:2lNyRKW3oc9kan8n@103.183.92.158:5432/result_cleansing')

    # simpan data, replace jika tabel sudah ada
    df.to_sql(
        tables,
        engine,
        schema=schemas,
        if_exists='replace',
        index=False
    )

    # generate nama primary key constraint secara dinamis
    parts = tables.split('_')
    with engine.connect() as conn:
        for i in range(3, len(parts) + 1):
            candidate = '_'.join(parts[:i])
            constraint_name = f"{candidate}_pkey"
            check = conn.execute(
                text("""
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_schema = :schema AND constraint_name = :name
                """), {"schema": schemas, "name": constraint_name}
            ).fetchone()
            if not check:
                pk_constraint_name = candidate
                break
        else:
            pk_constraint_name = '_'.join(parts)

    # tambahkan PRIMARY KEY
    with engine.connect() as connection:
        try:
            connection.execute(
                text(f"""
                    ALTER TABLE {schemas}.{tables}
                    ADD CONSTRAINT {pk_constraint_name}_pkey PRIMARY KEY ({primary_key});
                """)
            )
            connection.commit()
        except Exception as e:
            print(f"⚠️ Gagal menambahkan PRIMARY KEY: {e}")

    # cek keberhasilan primary key
    with engine.connect() as connection:
        result = connection.execute(
            text(f"""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_schema = :schema
                  AND tc.table_name = :table
                  AND tc.constraint_type = 'PRIMARY KEY';
            """), {"schema": schemas, "table": tables}
        ).fetchall()

    if result:
        print(f"✅ Primary key kolom: {result[0][0]}")
    else:
        print("⚠️ Tidak ada primary key ditemukan.")

    # buat index jika ada kolom yang cocok
    if index_col:
        with engine.connect() as connection:
            connection.execute(
                text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{tables}_{index_col}
                    ON {schemas}.{tables} ({index_col});
                """)
            )
            connection.commit()
        print(f"✅ Index dibuat pada kolom: {index_col}")
    else:
        print(f"ℹ️ Tidak ada index dibuat (level wilayah: {level_wilayah})")

    print("✅ Data berhasil disimpan ke result_cleansing.")

def masterdata(schemas, tables, jenis_data):
    if jenis_data == 0:
        jenis_text = 'transaksi'
    elif jenis_data == 1:
        jenis_text = 'agregat'
    elif jenis_data in ['transaksi', 'agregat']:
        jenis_text = jenis_data
    else:
        raise ValueError(f"Jenis data tidak dikenali: {jenis_data}")
    
    tanggal = datetime.now().date()

    conn = psycopg2.connect(
        dbname="result_cleansing",
        user="postgres",
        password="2lNyRKW3oc9kan8n",
        host="103.183.92.158",
        port="5432"
    )
    cursor = conn.cursor()

    posisi = 1
    while True:
        cursor.execute("SELECT pg_try_advisory_lock(123456);")
        locked = cursor.fetchone()[0]
        if locked:
            print("🔐 Lock diperoleh (masterdata)")
            break
        else:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_locks 
                WHERE locktype = 'advisory'
                AND NOT granted
                AND objid = 123456;
            """)
            posisi = cursor.fetchone()[0] + 1
            print(f"🔒 Menunggu giliran... Antrian: {posisi} user")
            time.sleep(5)

    try:
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS masterdata;
            CREATE TABLE IF NOT EXISTS masterdata.master_jenis_data (
                id SERIAL PRIMARY KEY,
                nama_schema TEXT,
                nama_table TEXT,
                jenis_data TEXT,
                modified_date DATE
            );
        """)
        conn.commit()

        cursor.execute("""
            SELECT id FROM masterdata.master_jenis_data
            WHERE nama_schema = %s AND nama_table = %s;
        """, (schemas, tables))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE masterdata.master_jenis_data
                SET jenis_data = %s
                WHERE nama_schema = %s AND nama_table = %s;
            """, (jenis_text, schemas, tables))
            conn.commit()
            print(f"🔁 Metadata diperbarui: {schemas}, {tables}, {jenis_text}.")

            # mengurutkan setelah update
            urutkan()
        else:
            cursor.execute("""
                INSERT INTO masterdata.master_jenis_data (nama_schema, nama_table, jenis_data, modified_date)
                VALUES (%s, %s, %s, %s);
            """, (schemas, tables, jenis_text, tanggal))
            conn.commit()
            print(f"✅ Metadata baru disimpan: {schemas}, {tables}, {jenis_text}, {tanggal}.")
    finally:
        cursor.execute("SELECT pg_advisory_unlock(123456);")
        print("🔓 Lock dilepas (masterdata)")
        cursor.close()
        conn.close()

def urutkan():
    # koneksi ke database
    engine = create_engine('postgresql://postgres:2lNyRKW3oc9kan8n@103.183.92.158:5432/result_cleansing')
    conn = psycopg2.connect(
        dbname="result_cleansing",
        user="postgres",
        password="2lNyRKW3oc9kan8n",
        host="103.183.92.158",
        port="5432"
    )
    cursor = conn.cursor()

    # memastikan schema dan tabel ada
    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS masterdata;
        CREATE TABLE IF NOT EXISTS masterdata.master_jenis_data (
            id SERIAL PRIMARY KEY,
            nama_schema TEXT,
            nama_table TEXT,
            jenis_data TEXT,
            modified_date DATE
        );
    """)
    conn.commit()

    # mengambil data dari tabel
    df = pd.read_sql("SELECT * FROM masterdata.master_jenis_data;", engine)

    # mengurutkan berdasarkan kolom id
    df.sort_values(by="id", inplace=True)

    # memastikan kolom id berada di depan
    cols = ['id'] + [col for col in df.columns if col != 'id']
    df = df[cols]

    # replace
    df.to_sql("master_jenis_data", engine, schema="masterdata", if_exists="replace", index=False)

    # cek apakah kolom id sudah SERIAL
    cursor.execute("""
        SELECT column_default FROM information_schema.columns
        WHERE table_schema = 'masterdata' 
        AND table_name = 'master_jenis_data' 
        AND column_name = 'id';
    """)
    default = cursor.fetchone()[0]

    # buat sequence baru
    if default is None or 'nextval' not in default:
        cursor.execute("DROP SEQUENCE IF EXISTS masterdata.master_jenis_data_id_seq CASCADE;")
        cursor.execute("CREATE SEQUENCE masterdata.master_jenis_data_id_seq;")

        # set default SERIAL
        cursor.execute("""
            ALTER TABLE masterdata.master_jenis_data
            ALTER COLUMN id SET DEFAULT nextval('masterdata.master_jenis_data_id_seq');
        """)

        # sinkronkan nilai sequence dengan max(id)
        cursor.execute("SELECT MAX(id) FROM masterdata.master_jenis_data;")
        max_id = cursor.fetchone()[0] or 0
        cursor.execute(f"""
            ALTER SEQUENCE masterdata.master_jenis_data_id_seq RESTART WITH {max_id + 1};
        """)
        conn.commit()

    cursor.close()
    conn.close()

def update_jenis_data():
    # koneksi ke database
    try:
        conn_datasets = psycopg2.connect(
            dbname="replikasipdj",
            user="postgres",
            password="2lNyRKW3oc9kan8n",
            host="103.183.92.158",
            port="5432"
        )
        cursor = conn_datasets.cursor()

        posisi = 1
        while True:
            cursor.execute("SELECT pg_try_advisory_lock(123456);")
            locked = cursor.fetchone()[0]
            if locked:
                print("🔐 Lock diperoleh (datasets replikasipdj)")
                break
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_locks 
                    WHERE locktype = 'advisory'
                    AND NOT granted
                    AND objid = 123456;
                """)
                posisi = cursor.fetchone()[0] + 1
                print(f"🔒 Menunggu giliran... Antrian: {posisi} user")
                time.sleep(5)

        conn_master = psycopg2.connect(
            dbname="result_cleansing",
            user="postgres",
            password="2lNyRKW3oc9kan8n",
            host="103.183.92.158",
            port="5432"
        )

        # mengambil data dari masterdata
        df_master = pd.read_sql("""
            SELECT nama_schema, nama_table, jenis_data 
            FROM masterdata.master_jenis_data
        """, conn_master)

        # mengambil data dari datasets
        df_datasets = pd.read_sql("""
            SELECT "schema", "table", jenis_data 
            FROM public.datasets
        """, conn_datasets)

        # sinkronisasi
        for index, row in df_master.iterrows():
            existing = df_datasets[
                (df_datasets['schema'] == row['nama_schema']) &
                (df_datasets['table'] == row['nama_table'])
            ]
            if existing.empty:
                # insert jika belum ada
                insert_query = """
                    INSERT INTO public.datasets ("schema", "table", jenis_data)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (row['nama_schema'], row['nama_table'], row['jenis_data']))
                print(f"✅ INSERT public.datasets: {row['nama_schema']}.{row['nama_table']}")
            else:
                existing_jenis = existing.iloc[0]['jenis_data']
                if existing_jenis is None:
                    # update hanya jika jenis_data masih kosong/null
                    update_query = """
                        UPDATE public.datasets
                        SET jenis_data = %s
                        WHERE "schema" = %s AND "table" = %s
                    """
                    cursor.execute(update_query, (row['jenis_data'], row['nama_schema'], row['nama_table']))
                    print(f"✅ UPDATE public.datasets: {row['nama_schema']}.{row['nama_table']}")

        conn_datasets.commit()
    except Exception as e:
        print(f"❌ Terjadi error saat sinkronisasi datasets: {e}")
    finally:
        cursor.execute("SELECT pg_advisory_unlock(123456);")
        print("🔓 Lock dilepas (datasets replikasipdj)")
        cursor.close()
        conn_datasets.close()
        conn_master.close()

def eksekusi():
    try:
        conn = psycopg2.connect(
            dbname="result_cleansing",
            user="postgres",
            password="2lNyRKW3oc9kan8n",
            host="103.183.92.158",
            port="5432"
        )

        print("🚀 Memulai proses cleansing...")

        df, schemas, tables = get_data_from_postgres()

        if 'periode_update' in df.columns:
            df['periode_update'] = df['periode_update'].apply(periode_update)

        wilayah = jenis_wilayah(df)

        if wilayah == 'data_kabupaten':
            df = kabupaten(df)
        elif wilayah == 'data_kecamatan':
            df = kecamatan(df)
        elif wilayah == 'data_kelurahan':
            kolom = {
                'kabupaten_kota': 'kabupaten',
                'nama_kecamatan': 'kecamatan',
                'desa_kelurahan': 'kelurahan'
            }
            df = kelurahan(df, status=wilayah, col=kolom, special_case='kelurahan', preference='kemendagri')

        print(f"\n🗺️ Tingkat Wilayah: {wilayah}", flush=True)
        print(tabulate(df.head(), headers='keys', tablefmt='psql'), flush=True)

        df, jenis = jenis_data(df)
        df = id_index(df)
        df = final(df)

        if preview_data(df):
            simpan(df, schemas, tables, level_wilayah=wilayah)
            masterdata(schemas, tables, jenis)
            urutkan()
            update_jenis_data()
        else:
            print("⛔ Proses dibatalkan.")
        
        print("✅ Proses cleansing selesai")

    except Exception as e:
        print(f"❌ Terjadi error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    eksekusi()