from setuptools import setup, find_packages
import os.path


def read(filepath):
    with open(os.path.join(*filepath.split('/'))) as f:
        return f.read()


setup(
    name="zc.form",
    version='0.6.dev0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    url='http://pypi.python.org/pypi/zc.form',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    include_package_data=True,
    long_description='\n\n'.join([
        read('src/zc/form/README.rst'),
        '.. contents::',
        read('CHANGES.rst'),
        read('src/zc/form/browser/combinationwidget.rst'),
        read('src/zc/form/browser/mruwidget.rst'),
        read('src/zc/form/browser/exceptionviews.rst')]),
    license="ZPL 2.1",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope :: 3',
    ],
    install_requires=[
        'ZODB3',
        'pytz',
        'setuptools',
        'zc.resourcelibrary',
        'zc.sourcefactory',
        'zope.annotation',
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
        test=[
            # 'Webtest',
            'zope.app.appsetup',
            'zope.app.principalannotation',
            'zope.app.wsgi[testlayer] >= 3.7',
            'zope.configuration',
            'zope.container',
            'zope.testing',
            'zope.testrunner',
            'zope.traversing',
        ]),
    zip_safe=False
)
