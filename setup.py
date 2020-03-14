from setuptools import setup, find_packages
import pyslo

setup(
    name='pyslo',
    packages=find_packages(),
    # license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    version=pyslo.__version__,
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        "google-cloud-monitoring",
        "pandas"
    ],

)