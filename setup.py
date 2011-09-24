from setuptools import setup, find_packages
import os.path


def read(filepath):
    return file(os.path.join(*filepath.split('/'))).read()


setup(
    name="zc.form",
    version='0.2',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    long_description='\n\n'.join([
        read('src/zc/form/README.txt'),
        '.. contents::',
        read('CHANGES.txt'),
        read('src/zc/form/TODO.txt'),
        read('src/zc/form/browser/combinationwidget.txt'),
        read('src/zc/form/browser/mruwidget.txt'),
        read('src/zc/form/browser/exceptionviews.txt')]),
    license="ZPL 2.1",
    install_requires=[
        'ZODB3',
        'pytz',
        'setuptools',
        'zc.resourcelibrary',
        'zc.sourcefactory',
        'zope.annotation',
        'zope.app.pagetemplate',
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
            'zope.app.appsetup',
            'zope.app.principalannotation',
            'zope.app.wsgi >= 3.7',
            'zope.browserpage',
            'zope.configuration',
            'zope.container',
            'zope.testing',
            'zope.traversing',
            ]),
    zip_safe=False
    )
