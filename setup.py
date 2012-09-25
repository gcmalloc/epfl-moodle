from setuptools import setup
setup(name='epfl-menu',
      version = '0.0.1',
      description = 'A simple interface to moodle',
      author = 'gcmalloc',
      url = 'http://github.com/gcmalloc/epfl-moodle',
      py_modules = ['epfl.moodle'],
      install_requires=['BeautifulSoup4', 'requests'],
      scripts = ['bin/moodle'])
