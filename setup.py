from __future__ import with_statement

import os.path
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from flask_configlint import __version__


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            readme = f.read()
    except IOError:
        pass
    pattern = re.compile(r'''
        (?P<colon> : \n{2,})?
        \s* \.\. [ ] code-block:: \s+ [^\n]+ \n
        [ \t]* \n
        (?P<block>
            (?: (?: (?: \t | [ ]{3}) [^\n]* | [ \t]* ) \n)+
        )
    ''', re.VERBOSE)
    return pattern.sub(
        lambda m: (':' + m.group('colon') if m.group('colon') else '') +
                  '\n'.join(' ' + l for l in m.group('block').splitlines()) +
                  '\n\n',
        readme, 0
    )


setup(
    name='Flask-ConfigLint',
    version=__version__,
    url='https://github.com/crosspop/flask-configlint',
    license='MIT License',
    author='Hong Minhee',
    author_email='dahlia' '@' 'crosspop.in',
    description='Flask configuration utilities',
    long_description=readme(),
    py_modules=['flask_configlint'],
    platforms='any',
    install_requires=['Flask >= 0.8'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
