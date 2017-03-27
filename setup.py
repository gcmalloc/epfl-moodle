from setuptools import setup
setup(
      name='epfl-moodle',
      version = '0.4.4',
      description = 'A simple interface to moodle',
      author = 'gcmalloc',
      url = 'http://github.com/gcmalloc/epfl-moodle',
      py_modules = ['epfl_moodle.moodle'],
      install_requires=['BeautifulSoup4', 'requests', 'keyring'],
      scripts = ['bin/moodle'])
