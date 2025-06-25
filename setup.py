from setuptools import setup, find_packages

setup(
    name="sifen",
    version="0.2.0",
    packages=find_packages(include=['sifen', 'sifen.*']),
    include_package_data=True,
    install_requires=[
        'lxml>=4.6.0',
        'pyOpenSSL>=20.0.0',
        'python-dotenv>=1.0.0'
    ],
    package_data={
        'sifen': ['schemas/*.xsd', 'certs/dev/*.pem'],
    },
)