import sys, os, re

def get_build():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'build.txt'), 'r') as file:
            build = file.read()
        return build
    except FileNotFoundError:
        return '0'

if __name__ == '__main__':
    build = int(get_build()) + 1
    with open('build.txt', 'w') as file:
        file.write(str(build))

NAME = 'fpclib'
RELEASE = '1.4.0.' + get_build()
VERSION = re.match('\d+\.\d+', RELEASE).group(0)
AUTHOR = 'mathgeniuszach'
EMAIL = 'huntingmanzach@gmail.com'
DESC = 'A powerful library for curating games for Flashpoint.'
LONG_DESC = 'fpclib is a powerful library for curating games for Flashpoint that includes support for curating games through code along with several internet-based and io functions that make it easier to read and write to files. Check out the `github page <https://github.com/xMGZx/fpclib>`_ for more info.'
URL = 'https://github.com/xMGZx/fpclib'
REQ = [
    'requests',
    'beautifulsoup4',
    'pillow',
    'ruamel.yaml'
]
CLASSIFIERS = [
    'Programming Language :: Python :: 3'
]

if __name__ == '__main__':
    print('Building %s %s' % (NAME, RELEASE))