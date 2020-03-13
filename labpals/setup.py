from labpals import app

if __name__ == '__main__':
    app.run()

# Uncomment if dependencies are a problem in new computers
from setuptools import setup

setup(
   name='app.py',
   packages=['app.py'],
   include_package_data=True,
   install_requires=[
       'flask',
   ],
)
