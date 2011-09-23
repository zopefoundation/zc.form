from setuptools import setup, find_packages
import os.path


def read(filepath):
    return file(os.path.join(*filepath.split('/'))).read()


setup(
    name="zc.form",
    version="0.1.3",
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    long_description='\n\n'.join([
        read('src/zc/form/README.txt'),
        read('CHANGES.txt'),
        '.. contents::',
        read('src/zc/form/TODO.txt'),
        read('src/zc/form/browser/combinationwidget.txt'),
        read('src/zc/form/browser/mruwidget.txt'),
        read('src/zc/form/browser/exceptionviews.txt')]),
    license="ZPL 2.1",
    install_requires=[
        'pytz',
        'setuptools',
        'zc.resourcelibrary',
        'zc.sourcefactory',
        'ZODB3',
        'zope.annotation',
        'zope.app.principalannotation',
        'zope.catalog',
        'zope.app.pagetemplate',
        'zope.cachedescriptors',
        'zope.component',
        'zope.exceptions',
        'zope.formlib >= 4.0',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.publisher',
        'zope.schema >= 3.6',
        # extras
        'zope.app.security',
        'zope.app.appsetup',
        'zope.app.securitypolicy',
        'zope.app.testing',
        'zope.configuration',
        'zope.testing',
        'zope.traversing',
        'zope.app.component',
        ],
    zip_safe=False
    )
