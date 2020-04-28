import setuptools
import metadata

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name=metadata.NAME,
    version=metadata.VERSION,
    author=metadata.AUTHOR,
    author_email=metadata.EMAIL,
    description=metadata.DESC,
    long_description=long_description,
    url=metadata.URL,
    packages=[metadata.NAME],
    install_requires=metadata.REQ
)