# majadigi

Library Python untuk cleansing, transformasi, dan standarisasi data wilayah Jatim (provinsi, kabupaten, kecamatan, desa/kelurahan).

## Instalasi

```bash
pip install -e .
```

## Penggunaan

```python
from majadigi import cleansing_data

df, schemas, tables = cleansing_data.get_data_from_postgres()
```
