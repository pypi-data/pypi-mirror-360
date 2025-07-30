from setuptools import setup, find_packages
from hecplus.__init__ import __version__

setup(
    name='hecplus',
    version=__version__,
    author='Prashana Bajracharya',
    author_email='pajracharya713@gmail.com',
    description='Helper functions for working with Hydrologic Engineering Center (HEC) softwares',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # author=httpimport.__author__,
    # license='MIT',
    # url=httpimport.__github__,
    # py_modules=['dsplus'],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        # 'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        # 'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Hydrology',
    ],
    python_requires='>=3.10',
    install_requires=[
        'dsplus',
        'pandas',
        'h5py',
    ],
    keywords=[
        'hec',
        'hecras',
        'hechms'],
)
