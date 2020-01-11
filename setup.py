from setuptools import setup

setup(
   name='fundamental',
   version='0.0.1',
   description='Dataframe for stock fundamental financials',
   author='Steven Wang',
   author_email='steven.wang0619@gmail.com',
   packages=['fundamental'],  #same as name
   install_requires=['numpy', 'pandas','yfinance','datetime', 'lxml', 'ssl','pandas_market_calendars']
)
