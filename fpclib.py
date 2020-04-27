from collections.abc import Iterable
from collections import OrderedDict
from bs4 import BeautifulSoup
from PIL import Image
from ruamel import yaml
from io import BytesIO
import requests
import hashlib
import codecs
import os
import re
import uuid
import pickle
import traceback
import stat
import shutil

INVALID_CHARS = re.compile(r'[/<>:\"\\\|\?\*\x00-\x1F]')
"""A compiled pattern that matches invalid charaters to be in a folder name.

:code:`re.compile(r'[/<>:\\"\\\\\\|\\?\\*\\x00-\\x1F]')`
"""
INVALID_CHARS_NO_SLASH = re.compile(r'[<>:\"\|\?\*\x00-\x1F]')
"""A compiled pattern that matches invalid charaters to be in a folder name except forward and back-slashes.

:code:`re.compile(r'[<>:\\"\\|\\?\\*\\x00-\\x1F]')`
"""
DATE = re.compile(r'^\d{4}(\-\d{2}){0,2}$')
"""A compiled pattern that matches properly formatted dates.

:code:`re.compile(r'^\\d{4}(\\-\\d{2}){0,2}$')`
"""
PORT = re.compile(r':\d+')
"""A compiled pattern that matches port numbers of urls with the prefixed colon.

:code:`re.compile(r':\\d+')`
"""
WAYBACK_LINK = re.compile(r'^[^/\\\.]*(:|/+)web.archive.org/web/(\d+|\*)([a-zA-Z]+_)*/')
"""A compiled pattern that matches the "web.archive.org/web/.../" part of web archive links.

:code:`re.compile(r'^[^/\\\\\\.]*(:|/+)web.archive.org/web/(\\d+|\\*)([a-zA-Z]+_)*/')`
"""
PROTOCOL = re.compile(r'^[^/\\\.]*(:|/+)')
"""A compiled pattern that matches the protocol (e.g., "http://", "//", or even "/") part of a url.

:code:`re.compile(r'^[^/\\\\\\.]*(:|/+)')`
"""
PROPER_PROTOCOL = re.compile(r'^[a-zA-Z]+://[^/]')
"""A compiled pattern that matches properly formatted protocols.

:code:`re.compile(r'^[a-zA-Z]+://[^/]')`
"""
EXTENSION = re.compile(r'\.[^/\\]+$')
"""A compiled pattern that matches file extensions.

:code:`re.compile(r'\.[^/\\]+$')`
"""
UUID = re.compile(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}')
"""A compiled pattern that matches uuids.

:code:`re.compile(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}')`
"""

SECURE_PLAYER = 'FPSoftware\\FlashpointSecurePlayer.exe'
"""Application path for Flashpoint Secure Player."""
JAVA = 'FPSoftware\\startJava.bat'
"""Application path for Java."""
UNITY = 'FPSoftware\\startUnity.bat'
"""Application path for Unity."""
BASILISK = 'FPSoftware\\Basilisk-Portable\\Basilisk-Portable.exe'
"""Application path for Basilisk."""
FLASH_PLAYERS = {
    0: 'FPSoftware\\Flash\\flashplayer_32_sa.exe',
    32: 'FPSoftware\\Flash\\flashplayer_32_sa.exe',
    29: 'FPSoftware\\Flash\\flashplayer29_0r0_171_win_sa.exe',
    28: 'FPSoftware\\Flash\\flashplayer28_0r0_161_win_sa.exe',
    27: 'FPSoftware\\Flash\\flashplayer27_0r0_187_win_sa.exe',
    19: 'FPSoftware\\Flash\\flashplayer19_0r0_245_sa.exe',
    14: 'FPSoftware\\Flash\\flashplayer14_0r0_179_win_sa.exe',
    11: 'FPSoftware\\Flash\\flashplayer11_9r900_152_win_sa_debug.exe',
    10: 'FPSoftware\\Flash\\flashplayer_10_3r183_90_win_sa.exe',
    9: 'FPSoftware\\Flash\\flashplayer9r277_win_sa.exe',
    -9: 'FPSoftware\\Flash\\9r16\\SAFlashPlayer.exe',
    -8: 'FPSoftware\\Flash\\8r22\\SAFlashPlayer.exe',
    7: 'FPSoftware\\Flash\\flashplayer29_0r0_171_win_sa.exe',
    -7: 'FPSoftware\\Flash\\7r14\\SAFlashPlayer.exe',
    -6.21: 'FPSoftware\\Flash\\6r21\\SAFlashPlayer.exe',
    -6.4: 'FPSoftware\\Flash\\6r4\\SAFlashPlayer.exe',
    -5: 'FPSoftware\\Flash\\5r30\\FlashPla.exe',
    -4.7: 'FPSoftware\\Flash\\4r7\\FlashPla.exe',
    -4.4: 'FPSoftware\\Flash\\4r4\\FlashPla.exe',
    -3: 'FPSoftware\\Flash\\3r8\\SwFlsh32.exe',
    -2: 'FPSoftware\\Flash\\2r11\\SwFlsh32.exe'
}
"""A table of all application paths for all flash players, mapped to version numbers. Allowed values are listed in the table below. Notice that negative values indicate that the specific player is in a folder, and 0 indicates the default version.

======= ===============================================================
Version Application Path
======= ===============================================================
0       FPSoftware\\\\Flash\\\\flashplayer_32_sa.exe
32      FPSoftware\\\\Flash\\\\flashplayer_32_sa.exe
29      FPSoftware\\\\Flash\\\\flashplayer29_0r0_171_win_sa.exe
28      FPSoftware\\\\Flash\\\\flashplayer28_0r0_161_win_sa.exe
27      FPSoftware\\\\Flash\\\\flashplayer27_0r0_187_win_sa.exe
19      FPSoftware\\\\Flash\\\\flashplayer19_0r0_245_sa.exe
14      FPSoftware\\\\Flash\\\\flashplayer14_0r0_179_win_sa.exe
11      FPSoftware\\\\Flash\\\\flashplayer11_9r900_152_win_sa_debug.exe
10      FPSoftware\\\\Flash\\\\flashplayer_10_3r183_90_win_sa.exe
9       FPSoftware\\\\Flash\\\\flashplayer9r277_win_sa.exe
-9      FPSoftware\\\\Flash\\\\9r16\\\\SAFlashPlayer.exe
-8      FPSoftware\\\\Flash\\\\8r22\\\\SAFlashPlayer.exe
7       FPSoftware\\\\Flash\\\\flashplayer29_0r0_171_win_sa.exe
-7      FPSoftware\\\\Flash\\\\7r14\\\\SAFlashPlayer.exe
-6.21   FPSoftware\\\\Flash\\\\6r21\\\\SAFlashPlayer.exe
-6.4    FPSoftware\\\\Flash\\\\6r4\\\\SAFlashPlayer.exe
-5      FPSoftware\\\\Flash\\\\5r30\\\\FlashPla.exe
-4.7    FPSoftware\\\\Flash\\\\4r7\\\\FlashPla.exe
-4.4    FPSoftware\\\\Flash\\\\4r4\\\\FlashPla.exe
-3      FPSoftware\\\\Flash\\\\3r8\\\\SwFlsh32.exe
-2      FPSoftware\\\\Flash\\\\2r11\\\\SwFlsh32.exe
======= ===============================================================
"""
FLASH = FLASH_PLAYERS[0]
"""A shorthand for :code:`FLASH_PLAYERS[0]`"""
SHOCKWAVE_PLAYERS = {
    0: 'FPSoftware\\Shockwave\\PJ101\\SPR.exe',
    '0': 'FPSoftware\\Shockwave\\PJ101\\SPR.exe',
    9: 'FPSoftware\\Shockwave\\PJ9\\SPR.exe',
    '9': 'FPSoftware\\Shockwave\\PJ9\\SPR.exe',
    '9D': 'FPSoftware\\Shockwave\\PJ9\\SPRD.exe',
    '9S': 'FPSoftware\\Shockwave\\PJ9\\SPRS.exe',
    '9P': 'FPSoftware\\Shockwave\\PJ9\\Projector.exe',
    12: 'FPSoftware\\Shockwave\\PJ12\\SPR.exe',
    '12': 'FPSoftware\\Shockwave\\PJ12\\SPR.exe',
    '12D': 'FPSoftware\\Shockwave\\PJ12\\SPRD.exe',
    '12S': 'FPSoftware\\Shockwave\\PJ12\\SPRS.exe',
    '12P': 'FPSoftware\\Shockwave\\PJ12\\Projector.exe',
    101: 'FPSoftware\\Shockwave\\PJ101\\SPR.exe',
    '101': 'FPSoftware\\Shockwave\\PJ101\\SPR.exe',
    '101D': 'FPSoftware\\Shockwave\\PJ101\\SPRD.exe',
    '101S': 'FPSoftware\\Shockwave\\PJ101\\SPRS.exe',
    '101P': 'FPSoftware\\Shockwave\\PJ101\\Projector.exe',
    851: 'FPSoftware\\Shockwave\\PJ851\\SPR.exe',
    '851': 'FPSoftware\\Shockwave\\PJ851\\SPR.exe',
    '851D': 'FPSoftware\\Shockwave\\PJ851\\SPRD.exe',
    '851S': 'FPSoftware\\Shockwave\\PJ851\\SPRS.exe',
    '851P': 'FPSoftware\\Shockwave\\PJ851\\Projector.exe',
    1103: 'FPSoftware\\Shockwave\\PJ1103\\SPR.exe',
    '1103': 'FPSoftware\\Shockwave\\PJ1103\\SPR.exe',
    '1103D': 'FPSoftware\\Shockwave\\PJ1103\\SPRD.exe',
    '1103S': 'FPSoftware\\Shockwave\\PJ1103\\SPRS.exe',
    '1103P': 'FPSoftware\\Shockwave\\PJ1103\\Projector.exe',
    1159: 'FPSoftware\\Shockwave\\PJ1159\\SPR.exe',
    '1159': 'FPSoftware\\Shockwave\\PJ1159\\SPR.exe',
    '1159D': 'FPSoftware\\Shockwave\\PJ1159\\SPRD.exe',
    '1159S': 'FPSoftware\\Shockwave\\PJ1159\\SPRS.exe',
    '1159P': 'FPSoftware\\Shockwave\\PJ1159\\Projector.exe',
}
"""A table of all application paths for all shockwave players, mapped to version numbers and strings. Allowed values are listed in the table below. Notice that SPRS and Projector should not typically be used for curations, and though you can use SPRD for debugging, you shouldn't submit your final curation with it. '0' or 0 indicates the default version.

============== ==================================================
Version        Application Path
============== ==================================================
0 or '0'       FPSoftware\\\\Shockwave\\\\PJ101\\\\SPR.exe
9 or '9'       FPSoftware\\\\Shockwave\\\\PJ9\\\\SPR.exe
'9D'           FPSoftware\\\\Shockwave\\\\PJ9\\\\SPRD.exe
'9S'           FPSoftware\\\\Shockwave\\\\PJ9\\\\SPRS.exe
'9P'           FPSoftware\\\\Shockwave\\\\PJ9\\\\Projector.exe
12 or '12'     FPSoftware\\\\Shockwave\\\\PJ12\\\\SPR.exe
'12D'          FPSoftware\\\\Shockwave\\\\PJ12\\\\SPRD.exe
'12S'          FPSoftware\\\\Shockwave\\\\PJ12\\\\SPRS.exe
'12P'          FPSoftware\\\\Shockwave\\\\PJ12\\\\Projector.exe
101 or '101'   FPSoftware\\\\Shockwave\\\\PJ101\\\\SPR.exe
'101D'         FPSoftware\\\\Shockwave\\\\PJ101\\\\SPRD.exe
'101S'         FPSoftware\\\\Shockwave\\\\PJ101\\\\SPRS.exe
'101P'         FPSoftware\\\\Shockwave\\\\PJ101\\\\Projector.exe
851 or '851'   FPSoftware\\\\Shockwave\\\\PJ851\\\\SPR.exe
'851D'         FPSoftware\\\\Shockwave\\\\PJ851\\\\SPRD.exe
'851S'         FPSoftware\\\\Shockwave\\\\PJ851\\\\SPRS.exe
'851P'         FPSoftware\\\\Shockwave\\\\PJ851\\\\Projector.exe
1103 or '1103' FPSoftware\\\\Shockwave\\\\PJ1103\\\\SPR.exe
'1103D'        FPSoftware\\\\Shockwave\\\\PJ1103\\\\SPRD.exe
'1103S'        FPSoftware\\\\Shockwave\\\\PJ1103\\\\SPRS.exe
'1103P'        FPSoftware\\\\Shockwave\\\\PJ1103\\\\Projector.exe
1159 or '1159' FPSoftware\\\\Shockwave\\\\PJ1159\\\\SPR.exe
'1159D'        FPSoftware\\\\Shockwave\\\\PJ1159\\\\SPRD.exe
'1159S'        FPSoftware\\\\Shockwave\\\\PJ1159\\\\SPRS.exe
'1159P'        FPSoftware\\\\Shockwave\\\\PJ1159\\\\Projector.exe
============== ==================================================
"""
SHOCKWAVE = SHOCKWAVE_PLAYERS[0]
"""A shorthand for :code:`SHOCKWAVE_PLAYERS[0]`"""



EVERYTHING = int('1111', 2)
"""A flag for :func:`Curation.save()` that says to save everything. This is equivalent to :code:`META|LOGO|SS|CONTENT`."""
META = int('1000', 2)
"""A flag for :func:`Curation.save()` that says to save meta."""
IMAGES = int('0110', 2)
"""A flag for :func:`Curation.save()` that says to save images. This is equivalent to :code:`LOGO|SS`."""
LOGO = int('0100', 2)
"""A flag for :func:`Curation.save()` that says to save the logo."""
SS = int('0010', 2)
"""A flag for :func:`Curation.save()` that says to save the screenshot."""
CONTENT = int('0001', 2)
"""A flag for :func:`Curation.save()` that says to save the content of the curation downloaded with :func:`Curation.get_files()`."""

class InvalidCharacterError(ValueError):
    """An error caused when attempting to read from or write to file name that has invalid characters in it."""
    pass
class InvalidFileError(IOError):
    """An error caused when attempting to read or write to a file that isn't a file (e.g., a directory)."""
    pass
class EmptyLocationError(ValueError):
    """An error caused when attempting to read or write to a file or create a folder with no name."""
    pass

def test():
    """Tests the library to make sure it works.
    
    This test will curate "Interactive Buddy" and download the swf file linked in the launch command into the proper place in a folder in the working directory.
    
    :raises AssertionError: If the test gives back any errors.
    """
    try:
        TestCuration().save(True)
    except KeyboardInterrupt:
        pass
    except:
        raise AssertionError('The working curation has failed. Be wary when using this program.')

def download(url, loc='', name=None):
    """Downloads the webpage or file at :code:`url` to the location :code:`loc`.
    
    :param str url: A url pointing to a file to be downloaded.
    :param str loc: A folder to download to; leave blank for the current working directory. If the folder doesn't exist, it will be created automatically.
    :param str name: If specified, the file will be saved with this name instead of an automatically generated one.
    """
    rurl = normalize(url, True, True, True)
    raw = rurl
    raw = WAYBACK_LINK.sub('', raw)
    if PROTOCOL.search(raw) is not None:
        raw = PROTOCOL.sub('', raw)
    if '?' in raw:
        raw = raw[:raw.index('?')]
    
    if name:
        file_name = name
    else:
        if raw.endswith('/') or '/' not in raw:
            file_name = 'index.html'
        else:
            file_name = raw[raw.rfind('/')+1:]
    
    with requests.get(rurl) as response:
        if loc:
            make_dir(loc)
            file_name = os.path.join(loc, file_name)
        with open(file_name, 'wb') as file:
            file.write(response.content)

def download_all(urls, loc='', preserve=False, keep_vars=False, ignore_errs=False):
    """Downloads a list of files with their website folder structure to the location :code:`loc`.
    
    For those that are familiar with cURLsDownloader, this function acts in a similar way. Invalid characters for a file/folder name will be replaced with "_", but "://" will be replaced with ".".
    
    :param [str,....] urls: A list of urls pointing to files to be downloaded.
    :param str loc: A folder to download to; leave blank for the current working directory. If the folder doesn't exist, it will be created automatically.
    :param bool preserve: If True, any files from "web.archive.org" will stay in the "web.archive.org" folder. By default, files are moved to their original domains with any port numbers removed.
    :param bool keep_vars: If True, files will be saved with all urlvars intact in their file name. This prevents files such as "http://www.example.com/game.php?id=123" and "http://www.example.com/game.php?id=321" from overwriting each other. Question marks are replaced with "_".
    :param bool ignore_errs: If True, any errors will be ignored and returned as part of a tuple including the urls that failed alongside each error.
    
    :returns: None or a list of tuples including failed urls and errors.
    """
    if loc:
        cwd = os.getcwd()
        make_dir(loc, True)
    errs = []
    try:
        for url in urls:
            try:
                rurl = normalize(url, preserve, True, True)
                raw = rurl
                url_vars = ''
                if PROTOCOL.search(raw) is not None:
                    raw = PROTOCOL.sub('', raw)
                if '?' in raw:
                    url_vars = raw[raw.index('?'):]
                    raw = raw[:raw.index('?')]
                
                if raw.endswith('/'):
                    raw += 'index.html'
                elif '/' not in raw:
                    raw += '/index.html'
                if keep_vars and url_vars:
                    raw += url_vars
                
                raw = INVALID_CHARS_NO_SLASH.sub('_', raw.replace('://', '.'))
                
                with requests.get(rurl) as response:
                    make_dir(os.path.dirname(raw))
                    with open(raw, 'wb') as file:
                        file.write(response.content)
            except Exception as e:
                if ignore_errs:
                    errs.append((url, e))
                else:
                    raise e
    finally:
        if loc:
            os.chdir(cwd)
    
    if ignore_errs:
        return errs

def download_image(url, loc='', name=None):
    """Downloads the image from :code:`url` to the location :code:`loc` as a PNG file.
    
    :param str url: A url pointing to the image to be downloaded.
    :param str loc: A folder to download to; leave blank for the current working directory. If the folder doesn't exist, it will be created automatically.
    :param str name: If specified, the file will be saved with this name instead of an automatically generated one.
    """
    rurl = normalize(url, True, True, True)
    raw = rurl
    raw = WAYBACK_LINK.sub('', raw)
    if PROTOCOL.search(raw) is not None:
        raw = PROTOCOL.sub('', raw)
    if '?' in raw:
        raw = raw[:raw.index('?')]
    
    if name:
        file_name = name
    else:
        if raw.endswith('/') or '/' not in raw:
            file_name = 'index.png'
        else:
            file_name = raw[raw.rfind('/')+1:]
            if EXTENSION.search(file_name) is not None:
                file_name = EXTENSION.sub('.png', file_name)
            else:
                file_name += '.png'
    
    with requests.get(rurl) as response:
        img = Image.open(BytesIO(response.content))
        if loc:
            make_dir(loc)
            file_name = os.path.join(loc, file_name)
    
    img.save(file_name, format='PNG')
    
def normalize(url, preserve=True, keep_vars=False, keep_prot=False):
    """Formats :code:`url` to a normalized format.
    
    This involves making it use the http protocol, fixing escaped slashes (:code:`\\/`), and removing url vars. Accepts strings starting with any protocol, no protocol, "//", or "/".
    
    :param str url: A string url to format.
    :param bool preserve: If False and the url is from "web.archive.org", the url will be formatted to it's original domain without the "web.archive.org" prefix.
    :param bool keep_vars: If True, url vars at the end of the string will stay on the string.
    :param bool keep_prot: If True, the url protocol will not be made to use the http protocol unless there is no protocol given or the protocol is formatted incorrectly.
    
    :returns: :code:`url` in a normalized format.
    """
    rurl = url.replace('\\/', '/')
    if not keep_vars and '?' in rurl:
        rurl = rurl[:rurl.find('?')]
    if not preserve:
        rurl = WAYBACK_LINK.sub('', rurl)
    if PROTOCOL.search(rurl) is not None:
        if keep_prot:
            if PROPER_PROTOCOL.search(rurl) is None:
                return PROTOCOL.sub('http://', rurl)
            else:
                return rurl
        else:
            return PROTOCOL.sub('http://', rurl)
    else:
        return 'http://' + rurl

def get_soup(url, parser='html.parser'):
    """Reads the webpage at :code:`url` and creates a BeautifulSoup object with it.
    
    :param str url: A string url of a webpage.
    :param str parser: The BeautifulSoup parser to use.
    
    :returns: A BeautifulSoup object created from :code:`url` or None if the url is blank.
    """
    if not url:
        return None
    with requests.get(normalize(url, True, True, True)) as response:
        soup = BeautifulSoup(response.text, parser)
    return soup

def read_url(url):
    """Reads the webpage or file at :code:`url` and returns its contents as a string.
    
    :param str url: A string url of a webpage or file.
    
    :returns: The contents of the webpage at :code:`url` as a string or None if the url is blank.
    """
    if not url:
        return None
    with requests.get(normalize(url, True, True, True)) as response:
        text = response.text
    return text

def read(file_name):
    """Reads the contents of the file :code:`file_name` into a string. 
    
    The returned string is in utf-8.
    
    :param str file_name: The location/name of a file in the local file system.
    
    :returns: The contents of the file :code:`file_name` as a string.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    :raises InvalidFileError: If :code:`file_name` is not a file.
    :raises FileNotFoundError: If :code:`file_name` cannot be found.
    """
    if not file_name:
        raise EmptyLocationError('Cannot read a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(file_name) is not None:
        raise InvalidCharacterError('File name "' + file_name + '" contains invalid characters.')
    if os.path.exists(file_name) and not os.path.isfile(file_name):
        raise InvalidFileError('"' + file_name + '" is not a file and cannot be read from.')
    
    with codecs.open(file_name, 'r', 'utf-8') as file:
        contents = file.read()
    return contents

def read_lines(file_name, ignore_lines=True):
    """Reads the lines of the file :code:`file_name` into a list of strings split by any new line character (:code:`\\r\\n`, :code:`\\r`, or :code:`\\n`).
    
    The returned strings are in utf-8.
    
    :param str file_name: The location/name of a file in the local file system.
    :param bool ignore_lines: By default this function disregards empty lines at the end of the file. Set this to False to disable that.
    
    :returns: A list of strings containing all of the lines in the file :code:`file_name`.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    :raises InvalidFileError: If :code:`file_name` is not a file.
    :raises FileNotFoundError: If :code:`file_name` cannot be found.
    """
    if not file_name:
        raise EmptyLocationError('Cannot read a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(file_name) is not None:
        raise InvalidCharacterError('File name "' + file_name + '" contains invalid characters.')
    if os.path.exists(file_name) and not os.path.isfile(file_name):
        raise InvalidFileError('"' + file_name + '" is not a file and cannot be read from.')
    
    with codecs.open(file_name, 'r', 'utf-8') as file:
        lines = file.read().replace('\r\n', '\n').replace('\r', '\n').split('\n')
    if ignore_lines:
        i = len(lines) - 1
        while not lines[i]:
            del lines[i]
            i -= 1
    return lines

def read_table(file_name, delimiter=',', ignore_lines=True):
    """Reads the contents of the file :code:`file_name` into a two dimensional list of strings with rows split by any new line character (:code:`\\r\\n`, :code:`\\r`, or :code:`\\n`) and columns split by :code:`delimiter`.
    
    The returned strings are in utf-8.
    
    :note: This function disregards empty lines at the end of the file.
    
    :param str file_name: The location/name of a file in the local file system.
    :param str delimiter: A string to split columns in the table by.
    :param bool ignore_lines: By default this function disregards empty lines at the end of the file. Set this to False to disable that.
    
    :returns: A two-dimensional list of strings of the content in the file :code:`file_name`.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    :raises InvalidFileError: If :code:`file_name` is not a file.
    :raises FileNotFoundError: If :code:`file_name` cannot be found.
    """
    return [line.split(delimiter) for line in read_lines(file_name, ignore_lines)]

def make_dir(folder, change=False, overwrite=False):
    """Makes a folder at :code:`folder`, along will all parent folders.
    
    It will not throw a FileExistsError if the folder already exists, but will instead return False.
    
    :param str folder: A string location to create a folder.
    :param bool change: If True, this function will set the new folder as the working directory.
    :param bool overwrite: If True, if there is a non-folder file in the same location as the folder being created, the folder will overwrite this file.
    
    :raises EmptyLocationError: If :code:`folder` is an empty string.
    :raises InvalidCharacterError: If :code:`folder` contains invalid characters.
    :raises FileExistsError: If a non-folder file exists in the location given by :code:`folder` and overwrite is not set.
    
    :returns: True on successful folder creation, False on failure.
    
    :note: Even if folder creation fails, if :code:`change` is True, the working directory will still be changed to that folder.
    """
    if not folder:
        raise EmptyLocationError('Cannot create a folder with no name.')
    if INVALID_CHARS_NO_SLASH.search(folder) is not None:
        raise InvalidCharacterError('Folder "' + folder + '" contains invalid characters.')
    
    r = True
    if os.path.exists(folder):
        if not os.path.isdir(folder):
            if overwrite:
                os.unlink(folder)
                os.makedirs(folder)
            else:
                raise FileExistsError('Cannot create the folder "' + folder + '" because a non-folder file is there. Use argument "overwrite=True" to overwrite.')
        else:
            r = False
    else:
        os.makedirs(folder)
    
    if change:
        os.chdir(folder)
    
    return r

def delete(file_name):
    """Deletes the file or folder :code:`file_name` recursively.
    
    It will not throw a FileNotFoundError if the file or folder doesn't exist, but will instead return False.
    
    :param str file_name: A string location of a file or folder to delete.
    
    :returns: True on successful deletion, False on failure.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    """
    if not file_name:
        raise EmptyLocationError('Cannot delete a file or folder with no name.')
    if INVALID_CHARS_NO_SLASH.search(file_name) is not None:
        raise InvalidCharacterError('Folder "' + file_name + '" contains invalid characters.')
    
    if os.path.exists(file_name):
        if os.path.isdir(file_name):
            shutil.rmtree(file_name)
        else:
            os.unlink(file_name)
        return True
    else:
        return False

def write(file_name, contents='', force=False):
    """Writes :code:`contents` to the file :code:`file_name` in utf-8.
    
    If the parent directory of this file doesn't exist, it will be automatically created.
    
    :param str file_name: The location/name of a file in the local file system.
    :param str|[str,....] contents: Contents to write to the file :code:`file_name`. If this is an Iterable (and not a string), each item in this will be written to the file :code:`file_name` as a separate line split by line feed (:code:`\\n`) characters.
    :param bool force: If True, if there is a non-writable file (like a directory) in the same location as the file being written to, the function will overwrite this file.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    :raises InvalidFileError: If a non-writable file exists in the location given by :code:`file_name` and :code:`force` is not set.
    """
    if not file_name:
        raise EmptyLocationError('Cannot write to a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(file_name) is not None:
        raise InvalidCharacterError('File name "' + file_name + '" contains invalid characters.')
    if os.path.exists(file_name) and not os.path.isfile(file_name):
        if force:
            if os.path.isdir(file_name):
                shutil.rmtree(file_name)
            else:
                os.unlink(file_name)
        else:
            raise InvalidFileError('"' + file_name + '" is not a file and cannot be written to. Use argument "force=True" to overwrite.')
    
    if not isinstance(contents, str) and isinstance(contents, Iterable):
        output = '\n'.join(contents)
    else:
        output = contents
        
    make_dir(os.path.dirname(file_name))
    with codecs.open(file_name, 'w', 'utf-8') as file:
        file.write(output)

def write_line(file_name, line='', force=False):
    """Append :code:`line` to the file :code:`file_name`.
    
    If the parent directory of this file doesn't exist, it will be automatically created.
    
    A line feed (:code:`\\n`) character is written after :code:`line`.
    
    :param str file_name: The location/name of a file in the local file system.
    :param str line: A line to write to the file :code:`file_name`.
    :param bool force: If True, if there is a non-writable file (like a directory) in the same location as the file being written to, the function will overwrite this file.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    :raises InvalidFileError: If a non-writable file exists in the location given by :code:`file_name` and :code:`force` is not set.
    """
    if not file_name:
        raise EmptyLocationError('Cannot write to a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(file_name) is not None:
        raise InvalidCharacterError('File name "' + file_name + '" contains invalid characters.')
    if os.path.exists(file_name) and not os.path.isfile(file_name):
        if force:
            if os.path.isdir(file_name):
                shutil.rmtree(file_name)
            else:
                os.unlink(file_name)
        else:
            raise InvalidFileError('"' + file_name + '" is not a file and cannot be written to. Use argument "force=True" to overwrite.')
    
    make_dir(os.path.dirname(file_name))
    with codecs.open(file_name, 'a', 'utf-8') as file:
        file.write(line + '\n')

def write_table(file_name, table, delimiter=',', force=False):
    """Writes the two-dimensional list :code:`table` to the file :code:`file_name`.
    
    If the parent directory of this file doesn't exist, it will be automatically created.
    
    Rows are joined by a line feed (:code:`\\n`) character, and columns are joined by :code:`delimiter`.
    
    :param str file_name: The location/name of a file in the local file system.
    :param [[str,....],....] table: A two-dimensional list of strings to format and write to the file :code:`file_name`.
    :param str delimiter: A string to join columns in the table by.
    :param bool force: If True, if there is a non-writable file (like a directory) in the same location as the file being written to, the function will overwrite this file.
    
    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    :raises InvalidFileError: If a non-writable file exists in the location given by :code:`file_name` and :code:`force` is not set.
    """
    if not file_name:
        raise EmptyLocationError('Cannot write to a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(file_name) is not None:
        raise InvalidCharacterError('File name "' + file_name + '" contains invalid characters.')
    if os.path.exists(file_name) and not os.path.isfile(file_name):
        if force:
            if os.path.isdir(file_name):
                shutil.rmtree(file_name)
            else:
                os.unlink(file_name)
        else:
            raise InvalidFileError('"' + file_name + '" is not a file and cannot be written to. Use argument "force=True" to overwrite.')
    
    make_dir(os.path.dirname(file_name))
    with codecs.open(file_name, 'w', 'utf-8') as file:
        file.write('\n'.join([delimiter.join(line) for line in table]))

def hash256(obj):
    """Serializes :code:`obj` and then returns a sha256 HASH object of it.
    
    Two objects that yield the same bytes representation will yield the same hash.
    
    :param obj: An object to hash.
    
    :returns: A sha256 HASH object of :code:`obj`.
    
    :seealso: Python's `hashlib <https://docs.python.org/3/library/hashlib.html>`_ library. The object returned is the same object created by :code:`hashlib.sha256()`.
    """
    m = hashlib.sha256()
    m.update(pickle.dumps(obj))
    return m

def hash(obj):
    """Serializes :code:`obj` and then gets a four-byte integer representation of those bytes with the first four bytes of it's sha256.
    
    This function is meant to replace the default python :code:`hash()` function because it does not rely on the object's id.
    
    :param obj: An object to hash.
    
    :returns: A four-byte integer representation of :code:`obj`.
    
    :seealso: :func:`hash256`
    """
    return int.from_bytes(hash256(obj).digest()[:4], byteorder="big", signed=True)

def clear_save():
    """Deletes the "c-info.tmp" file generated by :func:`curate()` and :func:`curate_regex()` in the current working directory.
    
    It will not throw a FileNotFoundError if it doesn't exist. Returns True on success, and False on failure.
    """
    try:
        os.unlink('c-info.tmp')
        return True
    except FileNotFoundError:
        return False

def curate(items, curation_class, use_title=False, save=False, ignore_errs=False, overwrite=False):
    """Curate games from a list of urls given by :code:`items` with a sub-class of :class:`Curation` specified by :code:`curation_class`.
    
    :param items [str|(str,dict),....]: normally a list of string urls of webpages to curate from, but if you put a tuple with 2 items in the place of any string, the first item in the tuple will be treated as the url, and the second item will be treated as a dictionary of arguments passed to an instance of :code:`curation_class` along with the url. You can mix tuples and strings.
    :param class curation_class: A sub-class of :class:`Curation` to create curations from. Note that this must be the *class* and not an object created from the class.
    :param bool use_title: If True, each curation folder will be generated with the title of the curation instead of its id.
    :param bool save: If True, progress will be constantly saved to "c-info.tmp" so that if the function errors and is ever called with the same :code:`items` variable in the same working directory again, it will resume where it left off. Note that calling this function again with a different list of :code:`items` will restart the process and the save file from any other processes.
    :param bool ignore_errs: If True, any error that a curation throws will be ignored and the curation will be skipped. Any failed items will be returned as a list of 3-length tuples at the end of the function with the item, the error, and a dictionary of additional arguments that were passed in.
    :param bool overwrite: If True, this method will mix and overwrite files in existing curation folders instead of making the folder "Curation (2)", "Curation (3)", etc.
    
    :returns: None or a list of tuples including failed urls, errors, and data passed in. The format for this is `[(str,Exception,dict),...]`
    
    :raises ValueError: If :code:`items` is empty.
    """
    if not items:
        raise ValueError('Items list is empty.')
    if save:
        sid = hash256(items).digest()
        try:
            with open('c-info.tmp', 'rb') as temp:
                new_sid = temp.read(32)
                if new_sid == sid:
                    (i, errs) = pickle.load(temp)
                else:
                    raise FileNotFoundError('Save file not found')
        except FileNotFoundError:
            i = 0
            errs = []
    else:
        i = 0
        errs = []
    
    count = len(items)
    while i < count:
        if save:
            with open('c-info.tmp', 'wb') as temp:
                temp.write(sid)
                pickle.dump((i, errs), temp)
        
        item = items[i]
        if isinstance(item, tuple):
            (item, data) = item
        else:
            data = {}
        
        if ignore_errs:
            try:
                curation_class(url=item, **data).save(use_title, overwrite)
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
            except Exception as e:
                errs.append((item, e, data))
        else:
            curation_class(url=item, **data).save(use_title, overwrite)
        
        i += 1
    
    if save:
        clear_save()
    
    if ignore_errs:
        return errs

def curate_regex(items, links, use_title=False, save=False, ignore_errs=False, overwrite=False):
    """Curate games from a list of urls given by :code:`items` with a list of :code:`links`.
    
    :see: :func:`curate()`
    
    :param [str|(str,dict),....] items: A list of urls of webpages with games to curate.
    :param [(str|re,class),....] links: A list of tuples containing a regex and a sub-class of :class:`Curation`. The function will search the url of each item for each of the regexes using :code:`re.search()`, and the first match will decide which sub-class gets used. If there are no matches, the curation would be skipped. A good example of the :code:`links` variable is something like :code:`[('newgrounds\\.com', NewgroundsCuration), ('kongregate\\.com', KongregateCuration)]`. Regexes can be strings or a :code:`re` object.
    :param bool use_title: Specifies whether or not to use the title or id of a curation for its folder.
    :param bool save: Specifies whether or not to save progress and continue where left off if the function is called with the same arguments.
    :param bool ignore_errs: Specifies whether or not to ignore errors and return them at the end of the function.
    :param bool overwrite: Whether or not to mix new curations with older folders with the same name.
    
    :returns: None or a list of tuples including failed urls, errors, and data passed in. The format for this is `[(str,Exception,dict),...]`
    
    :raises ValueError: If :code:`items` or :code:`links` is empty.
    """
    
    if not items:
        raise ValueError('Items list is empty.')
    if not links:
        raise ValueError('Regex-curation links list is empty.')
    
    for i in range(len(links)):
        link = links[i]
        if isinstance(link[0], str):
            links[i] = (re.compile(link[0]), link[1])
    
    if save:
        sid = hash256(items).digest()
        try:
            with open('c-info.tmp', 'rb') as temp:
                new_sid = temp.read(32)
                if new_sid == sid:
                    (i, errs) = pickle.load(temp)
                else:
                    raise FileNotFoundError('Save file not found')
        except FileNotFoundError:
            i = 0
            errs = []
    else:
        i = 0
        errs = []
    
    count = len(items)
    while i < count:
        if save:
            with open('c-info.tmp', 'wb') as temp:
                temp.write(sid)
                pickle.dump((i, errs), temp)
        
        item = items[i]
        if not isinstance(item, str) and isinstance(item, Iterable):
            (item, data) = item
        else:
            data = {}
        for link in links:
            if re.search(link[0], item) is not None:
                if ignore_errs:
                    try:
                        link[1](url=item, **data).save(use_title, overwrite)
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt()
                    except Exception as e:
                        errs.append((item, e, data))
                else:
                    link[1](url=item, **data).save(use_title, overwrite)
                break
        i += 1
    
    if save:
        clear_save()
    
    if ignore_errs:
        return errs

def load(curation):
    """Loads the curation in the folder :code:`curation` into :class:`Curation` object using ruamel.yaml.
    
    :param str curation: A string pointing to the location of a folder where a curation is stored.
    
    :returns: A :class:`Curation` object created with the metadata of the curation in the folder :code:`curation`.
    
    :note: The curation at :code:`curation` curation must be using the yaml curation format.
    
    :raises InvalidCharacterError: If :code:`curation` has invalid characters.
    :raises FileNotFoundError: If the folder given is not a valid curation.
    """
    data = yaml.round_trip_load(read(os.path.join(curation, 'meta.yaml')))
    c = Curation()
    c.meta = data
    
    folder = curation.replace('\\', '/')
    if '/' in folder:
        folder = folder[folder.rfind('/'):]
    if UUID.fullmatch(folder):
        c.id = folder
    
    return c

class Curation:
    """This is the base class for every kind of curation. If you want a good tutorial on how to use this class, see :doc:`The Basics </basics>`. Extend this class to redefine it's methods."""
    
    # REQ_ARGS = ['Title', 'Languages', 'Source', 'Platform', 'Application Path', 'Launch Command']
    # """Required arguments when saving."""
    # LIBRARIES = ['arcade', 'theatre']
    # """List of all Flashpoint libraries."""
    # PLAY_MODES = ['Cooperative', 'Multiplayer', 'Single Player', 'Cooperative; Multiplayer', 'Cooperative; Single Player', 'Multiplayer; Single Player', 'Cooperative; Multiplayer; Single Player']
    # """List of all Flashpoint play modes."""
    # PLATFORMS = ['3D Groove GX', '3DVIA Player', 'ActiveX', 'Authorware', 'Flash', 'GoBit', 'HTML', 'Hypercosm', 'Java', 'PopCap Plugin', 'ShiVa3D', 'Shockwave', 'Silverlight', 'Unity', 'Viscape', 'Vitalize']
    # """List of all Flashpoint platforms as of 8.0"""
    # STATUSES = ['Hacked', 'Partial', 'Playable', 'Hacked; Partial', 'Partial; Hacked']
    # """List of all Flashpoint statuses."""
    
    RESERVED_APPS = ['extras', 'message']
    """A list containing all of the reserved headings that cannot be used in additional applications. The check is case-insensitive, hence they are lowercase."""
    
    ARGS = {
        'title': 'Title',
        'name': 'Title',
        'alternateTitles': 'Alternate Titles',
        'altTitles': 'Alternate Titles',
        'alts': 'Alternate Titles',
        'library': 'Library',
        'lib': 'Library',
        'series': 'Series',
        'ser': 'Series',
        'developer': 'Developer',
        'dev': 'Developer',
        'publisher': 'Publisher',
        'pub': 'Publisher',
        'playMode': 'Play Mode',
        'mode': 'Play Mode',
        'releaseDate': 'Release Date',
        'date': 'Release Date',
        'version': 'Version',
        'ver': 'Version',
        'languages': 'Languages',
        'lang': 'Languages',
        'extreme': 'Extreme',
        'nsfw': 'Extreme',
        'tags': 'Tags',
        'genre': 'Tags',
        'source': 'Source',
        'src': 'Source',
        'url': 'Source',
        'platform': 'Platform',
        'tech': 'Platform',
        'status': 'Status',
        's': 'Status',
        'applicationPath': 'Application Path',
        'appPath': 'Application Path',
        'app': 'Application Path',
        'launchCommand': 'Launch Command',
        'launch': 'Launch Command',
        'cmd': 'Launch Command',
        'gameNotes': 'Game Notes',
        'notes': 'Game Notes',
        'originalDescription': 'Original Description',
        'description': 'Original Description',
        'desc': 'Original Description',
        'curationNotes': 'Curation Notes',
        'cnotes': 'Curation Notes'
    }
    """A dictionary containing mappings for the arguments in :func:`Curation.set_meta()` and :func:`Curation.get_meta()` to the :attr:`Curation.meta` dictonary.
        
    Here's a table of what each argument maps to:
    
    ==================== ======================================
    Meta Tag             Args
    ==================== ======================================
    Title                title, name
    Alternate Titles     alternateTitles, altTitles, alts
    Library              library, lib
    Series               series, ser
    Developer            developer, dev
    Publisher            publisher, pub
    Play Mode            playMode, mode
    Release Date         releaseDate, date
    Version              version, ver
    Languages            languages, lang
    Extreme              extreme, nsfw
    Tags                 tags, genre
    Source               source, src, url
    Platform             platform, tech
    Status               status, s
    Application Path     applicationPath, appPath, app
    Launch Command       launchCommand, launch, cmd
    Game Notes           gameNotes, notes
    Original Description originalDescription, description, desc
    Curation Notes       curationNotes, cnotes
    ==================== ======================================
    
    You can find the description of each of these tags on the `Curation Format <https://bluemaxima.org/flashpoint/datahub/Curation_Format#Metadata>`_ page on the Flashpoint wiki.
    """
    
    def __init__(self, **kwargs):
        """Accepts arguments in the same format as :func:`Curation.set_meta()`."""
        self.meta = OrderedDict([
            ('Title', None),
            ('Alternate Titles', None),
            ('Library', 'arcade'),
            ('Series', None),
            ('Developer', None),
            ('Publisher', None),
            ('Play Mode', 'Single Player'),
            ('Release Date', None),
            ('Version', None),
            ('Languages', 'en'),
            ('Extreme', 'No'),
            ('Tags', None),
            ('Source', None),
            ('Platform', 'Flash'),
            ('Status', 'Playable'),
            ('Application Path', FLASH),
            ('Launch Command', None),
            ('Game Notes', None),
            ('Original Description', None),
            ('Curation Notes', None),
            ('Additional Applications', OrderedDict())
        ])
        """An ordered dictionary containing all metadata for the game. While you can modify it directly, it is recommended that you use :func:`Curation.set_meta()` and :func:`Curation.get_meta()` instead.
        """
        self.args = {}
        """A dictionary containing all arguments passed in through :func:`Curation.set_meta()` that do not map to any metadata. You can use this to pass in extra information that you want to use in :func:`Curation.parse()` or other methods for custom classes."""
        self.set_meta(**kwargs)
        
        self.logo = None
        """A url pointing to an image to be used as the logo for this game. Any non-PNG files will be converted into PNG files when downloaded. You can modify it at will."""
        self.ss = None
        """A url pointing to an image to be used as the screenshot for this game. Any non-PNG files will be converted into PNG files when downloaded. You can modify it at will."""
        
        self.id = str(uuid.uuid4())
        """A UUID identifying this curation. By default this is the name of the folder the curation will be saved to when :func:`Curation.save()` is called. You can re-generate an id by using :func:`Curation.new_id()`."""
    
    def new_id(self):
        """Generate a new uuid for this curation. 
        
        :see: :attr:`Curation.id`
        """
        self.id = str(uuid.uuid4())
    
    def set_meta(self, **kwargs):
        """Set the metadata with :code:`kwargs`. This method does not do error checking.
        
        :param ** kwargs: A list of arguments to set the metadata with. To see what you can use for :code:`kwargs`, see :attr:`Curation.ARGS`. Any value passed in that is not in :attr:`Curation.ARGS` will still be stored and can be retrieved through :func:`Curation.get_meta()`.
        
        :note: For example, to set the title of a curation you would use :code:`curation.set_meta(title='The Title of the Game')`
        """
        for arg in kwargs:
            if arg in Curation.ARGS:
                if kwargs[arg] == '':
                    self.meta[Curation.ARGS[arg]] = None
                else:
                    self.meta[Curation.ARGS[arg]] = kwargs[arg]
            else:
                self.args[arg] = kwargs[arg]
    
    def get_meta(self, key):
        """Get the metadata/args referenced by :code:`key`. 
        
        :param str key: The name of an argument to get the value of. You can either use the keys referenced by :attr:`Curation.ARGS` or the name of the argument you passed in through :func:`Curation.set_meta()`.
        
        :returns: The meta referenced by :code:`key`, the data associated with it, or None if it hasn't been set.
        """
        try:
            if key in Curation.ARGS:
                return self.meta[key]
            else:
                return self.args[key]
        except KeyError:
            return None
    
    def add_app(self, heading, launch, path=FLASH):
        """Add an additional application. To add extras or a message, use :func:`Curation.add_ext()` and :func:`Curation.add_msg()` respectively.
        
        :param str heading: The name of the additional application.
        :param str launch: The name of the launch command for the additional application.
        :param str path: The application path for the additional application. Defaults to :data:`FLASH`.
        
        :seealso: The `Additional Applications <https://bluemaxima.org/flashpoint/datahub/Curation_Format#Appendix_II:_Additional_Applications>`_ section of the Curation Format page.
        
        :note: Trying to add an additional app with a heading that already exists will result in replacing it.
        
        :raises ValueError: If :code:`heading` is in :attr:`Curation.RESERVED_APPS`.
        """
        if heading.lower() in Curation.RESERVED_APPS:
            raise ValueError('You cannot create an additional app with the name"' + heading + '"')
        self.meta['Additional Applications'][heading] = OrderedDict([
            ('Application Path', path),
            ('Launch Command', launch)
        ])
    
    def add_ext(self, folder):
        """Add extras from folder.
        
        :param str folder: The name of the folder the extras are located in.
        
        :seealso: The `Extras <https://bluemaxima.org/flashpoint/datahub/Curation_Format#Extras>`_ section of the Curation Format page.
        
        :note: Calling this method more than once will replace the current extras."""
        self.meta['Additional Applications']['Extras'] = folder
        
    def add_msg(self, message):
        """Add message.
        
        :param str message: The message to add to this curation.
        
        :seealso: The `Messages <https://bluemaxima.org/flashpoint/datahub/Curation_Format#Messages>`_ section of the Curation Format page.
        
        :note: Calling this method more than once will replace the current message.
        """
        self.meta['Additional Applications']['Message'] = message
        
    def del_app(self, heading):
        """Delete an additional application, extras, or message.
        
        :param str heading: The name of the additional application to delete. Use "Extras" or "Message" to delete an extras or message.
        
        :raises KeyError: If the app doesn't exist.
        """
        del self.meta['Additional Applications'][heading]
    
    def get_yaml(self):
        """Use ruamel.yaml to parse :attr:`Curation.meta` into a string.
        
        :returns: A yaml string with the formatted metadata.
        """
        return yaml.round_trip_dump(self.meta)
    
    def soupify(self):
        """Get's the relevant BeautifulSoup object of this curation to pass to :func:`Curation.parse()`.
        
        This method's sole purpose is to make it possible to overwrite the process for getting the soup object for a particular url. This is useful in case certain websites have special protection preventing you from downloading pages too fast.
        
        :returns: :func:`get_soup()` with the :code:`source` part of the metadata as it's parameter.
        """
        return get_soup(self.meta['Source'])
    
    def parse(self, soup):
        """Parse for metadata with a soup object provided by :func:`Curation.soupify()`. By default this method does nothing and must be overwritten to give it functionality.
        
        :see: :func:`Curation.save()`.
        """
        pass
    
    def get_files(self):
        """Download/Create all necessary content files for this curation. By default this method downloads the file linked by all launch commands and creates all the directories necessary for them to be in. It will not throw any errors if downloading fails.
        
        :see: :func:`Curation.save()`.
        """
        apps = self.meta['Additional Applications']
        files = [apps[app]['Launch Command'] for app in apps if app.lower() not in Curation.RESERVED_APPS]
        if self.meta['Launch Command'] is not None:
            files.append(self.meta['Launch Command'])
        download_all(files, ignore_errs=True)
    
    def save_image(self, url, file_name):
        """Download the image from :code:`url` and save it to :code:`file_name` as a PNG file; this method is primarily used for downloading logos and screenshots. It may be overwriten to add custom image-downloading abilities, but by default it just calls the :func:`download_image()` function.
        
        :param str url: The url location of the image to download.
        :param str file_name: The location/name of the file to save to.
        
        :see: :func:`Curation.save()`.
        """
        download_image(url, name=file_name)
    
    def save(self, use_title=False, overwrite=False, save_items=EVERYTHING):
        """Save the curation to a folder with the name of :attr:`Curation.id`. Consecutive calls to this method will not overwrite the previous folder, but will instead save it as "Curation (2)", "Curation (3)", etc.
        
        :param str use_title: If True, the folder will be generated with the title of the curation instead of its id.
        :param bool overwrite: If True, this method will mix and overwrite files in existing curation folders instead of making the folder "Curation (2)", "Curation (3)", etc.
        :param int save_items: Flags determining what items to save as part of this curation. By default this is :data:`EVERYTHING`. If you wanted to save only the meta and logo, for example, use :code:`save_items=META|LOGO`.
        
        :see: :data:`EVERYTHING` and the surrounding constants.
        
        The process of this method is as follows:
        
        #. Create a BeautifulSoup object with :func:`Curation.soupify()`.
        #. Call method :func:`Curation.parse()` with the soup object just created.
        #. Create curation folder for the curation and set it to the working directory (the working directory will be reset in the case of any error).
        #. Create meta file with :func:`Curation.get_yaml()` and download logo and screenshot through :func:`Curation.save_image()` if they are available.
        #. Create "content" folder and set it to the working directory.
        #. Call method :func:`Curation.get_files()` to get all files necessary for the game.
        #. Reset working directory.
        
        You may overwrite any of these methods to allow for custom usability.
        """
        cwd = os.getcwd()
        try:
            self.parse(self.soupify())
            
            if use_title:
                title = self.meta['Title']
                if not title:
                    folder = 'No Title'
                else:
                    folder = INVALID_CHARS.sub('', title.strip())
            else:
                folder = self.id
            if not overwrite:
                number = 1
                name = folder
                while os.path.exists(folder):
                    number += 1
                    folder = name + ' (' + str(number) + ')' 
            
            make_dir(folder, True)
            
            if save_items & META:
                write('meta.yaml', self.get_yaml())
            
            if save_items & LOGO:
                if self.logo is not None:
                    self.save_image(self.logo, 'logo.png')
            if save_items & SS:
                if self.ss is not None:
                    self.save_image(self.ss, 'ss.png')
            
            if save_items & CONTENT:
                make_dir('content', True)
                self.get_files()
        finally:
            os.chdir(cwd)

class TestCuration(Curation):
    """An extension of :class:`Curation` that curates interactive buddy."""
    
    def parse(self, soup):
        self.set_meta(url='https://www.newgrounds.com/portal/view/218014')
        self.logo = 'https://picon.ngfiles.com/218000/flash_218014_medium.gif'
        self.ss = 'https://www.softpaz.com/screenshots/interactive-buddy-mofunzone/5.png'
        self.set_meta(title='Interactive Buddy', tags=['Simulation', 'Toy'])
        self.set_meta(dev='Shock Value', pub='Newgrounds')
        self.set_meta(ver='1.01', date='2005-02-08')
        self.set_meta(cmd='http://uploads.ungrounded.net/218000/218014_DAbuddy_latest.swf')
        self.set_meta(desc='Use various weapons to beat up on the buddy, in order to get money to buy more weapons!\n\nUpdates will come if you guys want them. Just leave reviews with suggestions for items, skins, etc.\n\nNote that the graphics (such as the background) were left simple so that the framerate would be as high as possible. Around 36 fps is optimal, but some browsers have trouble displaying Flash movies at that rate (such as Firefox, which I use, unfortunately).')
        self.add_app('wrongo', 'ah')
        self.del_app('wrongo')
        self.add_app('Kongregate v1.02', 'http://chat.kongregate.com/gamez/0003/0303/live/ib2.swf?kongregate_game_version=1363985380')

if __name__ == '__main__':
    print('Testing curation abilities.')
    test()
    print('Curation tested successfully.')
    