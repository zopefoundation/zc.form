from setuptools import setup, find_packages

setup(
    name="zc.form",
    version="0.1.3",
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires=[
        'pytz',
        'setuptools',
        'zc.resourcelibrary',
        'zc.sourcefactory',
        'ZODB3',
        'zope.annotation',
        'zope.app.principalannotation',
        'zope.app.catalog',
        'zope.app.form',
        'zope.app.pagetemplate',
        'zope.app.zapi',
        'zope.cachedescriptors',
        'zope.component',
        'zope.exceptions',
        'zope.formlib',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.index',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        # extras
        'zope.app.security',
        'zope.app.appsetup',
        'zope.app.securitypolicy',
        'zope.app.testing',
        'zope.configuration',
        'zope.testing',
        'zope.traversing',
        'zope.app.component',
        'zope.app.zcmlfiles', # sigh
        ],
    zip_safe=False
    )
