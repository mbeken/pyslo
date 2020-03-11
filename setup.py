from setuptools import setup, find_packages


setup(
    name='pyslo',
    packages=find_packages(),
    # license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    version='0.0.1',
    # use_scm_version = {"root": ".", "relative_to": __file__},
    # setup_requires=['setuptools_scm'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        "envparse==0.2.0",
        "future==0.17.1",
        "numpy==1.16.2",
        "pandas==0.24.2",
        "PyHive==0.6.1",
        "pymysql==0.9.3",
        "pyodbc==4.0.26",
        "python-dateutil==2.8.0",
        "pytz==2018.9",
        "sasl==0.2.1",
        "six==1.12.0",
        "SQLAlchemy==1.3.2",
        "thrift==0.11.0",
        "thrift-sasl==0.3.0",
    ],

)