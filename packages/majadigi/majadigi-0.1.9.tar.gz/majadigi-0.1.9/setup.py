from setuptools import setup, find_packages

setup(
    name='majadigi',
    version='0.1.9',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'psycopg2-binary',
        'sqlalchemy',
        'tabulate',
        'scikit-learn'
    ],
    author='Wawu Tri Ambodo',
    author_email='wawutri1706@gmail.com',
    description='Library untuk cleansing dan transformasi data wilayah Jatim',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/UWWAWWU/Library-Majadigi',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)