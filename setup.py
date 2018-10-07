#!/usr/bin/env python3
#
# This file is part of xmpp-test (https://github.com/mathiasertl/xmpp-test).
#
# xmpp-test is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# xmpp-test is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with xmpp-test.  If not, see
# <http://www.gnu.org/licenses/>.

import subprocess
import sys

from setuptools import Command
from setuptools import setup
from setuptools import find_packages

long_description = ""

install_requires = [
    'aiodns==1.1.1',
    'slixmpp==1.4.0',
    'tabulate==0.8.2',
]


class BaseCommand(Command):
    user_options = [
        ('suite=', None, 'Testsuite to run', )
    ]

    def initialize_options(self):
        self.suite = ''

    def finalize_options(self):
        pass

    def run_tests(self):
        pass


class TestCommand(BaseCommand):
    description = 'Run the test-suite for django-ca.'

    def run(self):
        self.run_tests()


class CoverageCommand(BaseCommand):
    description = 'Generate test-coverage for django-ca.'

    def run(self):
        pass


class QualityCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('isort --check-only --diff -rc xmpp_test/ setup.py')
        status = subprocess.call(['isort', '--check-only', '--diff', '-rc',
                                  'xmpp_test/', 'setup.py'])
        if status != 0:
            sys.exit(status)

        print('flake8 xmpp_test/ setup.py')
        status = subprocess.call(['flake8', 'xmpp_test/', 'setup.py'])
        if status != 0:
            sys.exit(status)


setup(
    name='xmpp-test',
    version='0.1.0',
    description='A XMPP test framework',
    long_description=long_description,
    author='Mathias Ertl',
    author_email='mati@er.tl',
    url='https://github.com/mathiasertl/xmpp-test',
    packages=find_packages(),
    install_requires=install_requires,
    cmdclass={
        'coverage': CoverageCommand,
        'test': TestCommand,
        'code_quality': QualityCommand,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Security :: Cryptography',
        'Topic :: Security',
    ],
)
