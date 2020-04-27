import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fpclib",
    version="1.1.0",
    author="mathgeniuszach",
    author_email="huntingmanzach@gmail.com",
    description="A powerful library for curating games for Flashpoint.",
    long_description=long_description,
    url="https://github.com/xMGZx/fpclib",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'pillow',
        'ruamel.yaml'
    ],
    python_requires='>=3.6'
)