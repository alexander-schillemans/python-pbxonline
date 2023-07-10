from setuptools import setup

# read the contents of README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'python-pbxonline',         
  packages=['pbxonline', 'pbxonline.models', 'pbxonline.constants', 'pbxonline.endpoints', 'pbxonline.cache'],
  version = '0.1.3',
  license='GPL-3.0-or-later',
  description = 'Wrapper for PBX Online API',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Alexander Schillemans',
  author_email = 'alexander.schillemans@hotmail.com',
  url = 'https://github.com/alexanderlhsglobal/python-pbxonline',
  download_url = 'https://github.com/alexanderlhsglobal/python-pbxonline/archive/refs/tags/0.1.3.tar.gz',
  keywords = ['pbxonline'],
  install_requires=[
          'requests',
          'requests_oauthlib'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3.10',
  ],
)