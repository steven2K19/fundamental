from setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()


setuptools.setup(
   name='fundamental',
   version='0.0.1',
   description='Dataframe for stock fundamental financials',
   author='Steven Wang',
   author_email='steven.wang0619@gmail.com',
   packages=['fundamental'],  #same as name
   install_requires=['numpy', 'pandas','yfinance','datetime', 'lxml', 'ssl','pandas_market_calendars']
)
