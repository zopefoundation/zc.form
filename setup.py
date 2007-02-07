from setuptools import setup, find_packages

setup(
    name="zc.form",
    version="0.1dev",
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requirements = ['setuptools'],
    zip_safe = False
    )
