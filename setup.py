import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

try:
  README = open(os.path.join(here, 'README.rst')).read()
  CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
  README = ''
  CHANGES = ''


setup(
  name='Flask-Fanstatic',
  version='0.2.0',
  url='http://github.com/mgood/flask-fanstatic',
  license='BSD',
  author='Matt Good',
  author_email='matt@matt-good.net',
  description='Flask integration for the Fanstatic resource publishing system.',
  long_description=README + '\n\n' + CHANGES,
  zip_safe=True,
  platforms='any',
  py_modules=['flask_fanstatic'],
  install_requires=[
    'Flask>=0.8',
    'Fanstatic',
    'Werkzeug',
  ],
  classifiers=[
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
)
