import setuptools
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setuptools.setup(
   name='fundamental',
   version='0.1.1.15',
   author='Steven Wang',
   author_email='steven.wang0619@gmail.com',
   description='Data frame downloader for fundamental financial',
   long_description=long_description,
   url='https://github.com/steven2K19/fundamental',
   packages=setuptools.find_packages(),
   install_requires=['numpy', 'pandas','yfinance','datetime', 'lxml',
                     'pandas_market_calendars'],
   classifiers=[
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License"
              ],
)