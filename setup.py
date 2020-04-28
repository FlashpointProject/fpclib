import setuptools
import metadata

setuptools.setup(
    name=metadata.NAME,
    version=metadata.VERSION,
    author=metadata.AUTHOR,
    author_email=metadata.EMAIL,
    description=metadata.DESC,
    long_description=metadata.LONG_DESC,
    url=metadata.URL,
    packages=[metadata.NAME],
    install_requires=metadata.REQ,
    classifiers=metadata.CLASSIFIERS
)