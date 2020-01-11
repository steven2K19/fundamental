from setuptools import setup, find_packages

setup(
   name='fundamental',
   version='0.1',
   description='Dataframe downloader for fundamental financials',
   url= 'https://github.com/steven2K19/fundamental',
   author='Steven Wang',
   author_email='steven.wang0619@gmail.com',
   license='MIT',
   packages=find_packages(),
   install_requires=['numpy', 'pandas','yfinance','datetime', 'lxml',
                     'pandas_market_calendars','pandas.tseries.offsets']
)







