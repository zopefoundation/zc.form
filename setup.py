import os.path

from setuptools import find_packages
from setuptools import setup


def read(filepath):
    with open(os.path.join(*filepath.split('/'))) as f:
        return f.read()


MRU_REQUIRES = [
    'zope.annotation',
    'BTrees',
    'persistent',
    'zc.resourcelibrary',
]

TEST_REQUIRES = [
    'zope.app.appsetup',
    'zope.app.principalannotation',
    'zope.app.wsgi[testlayer] >= 3.7',
    'zope.configuration',
    'zope.container',
    'zope.testing',
    'zope.testrunner',
    'zope.traversing',
]


setup(
    name="zc.form",
    version='2.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    url='https://github.com/zopefoundation/zc.form',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.dev',
    include_package_data=True,
    description=(
        'Extra browser widgets and alternative approaches for zope.formlib.'),
    long_description='\n\n'.join([
        read('README.rst'),
        '.. contents::',
        read('CHANGES.rst'),
        read('src/zc/form/browser/combinationwidget.rst'),
        read('src/zc/form/browser/mruwidget.rst'),
    ]),
    license="ZPL 2.1",
    keywords="zope formlib form widget extra",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope :: 3',
    ],
    python_requires='>=3.7',
    install_requires=[
        'pytz',
        'setuptools',
        'zc.sourcefactory',
        'zope.browserpage',
        'zope.cachedescriptors',
        'zope.catalog',
        'zope.component >= 3.8',
        'zope.exceptions',
        'zope.formlib >= 4.0',
        'zope.index',
        'zope.interface',
        'zope.publisher',
        'zope.schema >= 3.6',
        'zope.security',
    ],
    extras_require=dict(
        mruwidget=MRU_REQUIRES,
        test=MRU_REQUIRES + TEST_REQUIRES,
        slimtest=TEST_REQUIRES,
    ),
    zip_safe=False
)
