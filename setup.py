from setuptools import setup, find_packages
from satmatchup import __version__

setup(
    name='satmatchup',
    version=__version__,
    packages=find_packages(),
    package_data={'': ['*.so']},
    #     # If any package contains *.txt files, include them:
    #     '': ['*.txt'],
    #     'lut': ['data/lut/*.nc'],
    #     'aux': ['data/aux/*']
    # },
    include_package_data=True,

    url='https://gitlab.irstea.fr/ETL-TELQUEL/etl/tree/dev/preprocessing/trios',
    license='MIT',
    author='T. Harmel',
    author_email='tristan.harmel@ntymail.com',
    description='Utilities for matchup comparison of satellite pixel information with in-situ or ground-based measurements',
    # TODO update Dependent packages (distributions)
    install_requires=['rasterio','pandas', 'scipy', 'numpy', 'netCDF4', 'matplotlib',
                      'xarray','shapely','regionmask','cartopy','docopt', 'GDAL', 'python-dateutil'],

    entry_points={
        'console_scripts': [
            'satmatchup = main:main',

        ]}
)
