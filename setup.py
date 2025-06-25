from setuptools import setup, find_packages

setup(
    name="sifen",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "lxml>=4.6.0",
        "pyOpenSSL>=20.0.0",
        "python-dotenv>=0.19.0"  # Para manejar variables de entorno
    ],
)