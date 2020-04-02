from distutils.core import setup
import setuptools

setup(
  name = 'musicdb',
  py_modules = ['myMusicDBMap'],
  version = '0.0.1',
  description = 'A Python Wrapper for Music DB Data',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/musicdb',
  keywords = ['Discogs', 'music'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['jupyter_contrib_nbextensions'],
  dependency_links=[]
)
 
