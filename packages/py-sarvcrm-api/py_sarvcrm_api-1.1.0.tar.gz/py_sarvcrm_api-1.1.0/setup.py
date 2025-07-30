from setuptools import find_packages, setup

setup(
    name='py-sarvcrm-api',
    version='1.1.0',
    license="MIT",
    description='simple sarvcrm api module',
    author='Radin-System',
    author_email='technical@rsto.ir',
    url='https://github.com/Radin-System/py-sarvcrm-api',
    install_requires=[
        'requests==2.32.4',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)