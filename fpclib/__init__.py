from collections.abc import Iterable
from bs4 import BeautifulSoup
from PIL import Image
from ruamel import yaml
from io import BytesIO
import requests
import hashlib
import codecs
import copy
import os
import re
import uuid
import pickle
import stat
import shutil
import datetime

INVALID_CHARS = re.compile(r'(?<!^\w)[/<>:\"\\\|\?\*\x00-\x1F]')
"""A compiled pattern that matches invalid charaters to be in a folder name.

:code:`re.compile(r'(?<!^\\w)[/<>:\\"\\\\\\|\\?\\*\\x00-\\x1F]')`
"""
INVALID_CHARS_NO_SLASH = re.compile(r'(?<!^\w)[<>:\"\|\?\*\x00-\x1F]')
"""A compiled pattern that matches invalid charaters to be in a folder name except forward and back-slashes.

:code:`re.compile(r'(?<!^\\w)[<>:\\"\\|\\?\\*\\x00-\\x1F]')`
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

:code:`re.compile(r'\\.[^/\\]+$')`
"""
UUID = re.compile(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}')
"""A compiled pattern that matches uuids.

:code:`re.compile(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}')`
"""
STARTING_PARENTHESES = re.compile(r'^\s*\(.*?\)\s*')
"""A compiled pattern that matches parentheses and surrounding spaces at the beginning of a string (e.g., " (This) " in " (This) Some text with a ')'").

:code:`re.compile(r'^\\s*\\(.*?\\)\\s*')`

:since 1.3:
"""

SECURE_PLAYER = 'FPSoftware\\FlashpointSecurePlayer.exe'
"""Application path for Flashpoint Secure Player."""
JAVA = 'FPSoftware\\startJava.bat'
"""Application path for Java."""
JAVA_IN_BROWSER = 'FPSoftware\\startJavaInBrowser.bat'
"""Application path for Java in browser.

:since 1.3:
"""
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
    7: 'FPSoftware\\Flash\\flashplayer_7_sa.exe',
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
7       FPSoftware\\\\Flash\\\\flashplayer_7_sa.exe
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
UNITY = 'FPSoftware\\startUnity.bat'
"""Application path for Unity."""
ACTIVE_X = 'FPSoftware\\startActiveX.bat'
"""Application path for ActiveX.

:since 1.3:
"""
GROOVE = 'FPSoftware\\startGroove.bat'
"""Application path for 3D Groove GX.

:since 1.3:
"""
SVR = 'FPSoftware\\startSVR.bat'
"""Application path for Viscape.

:since 1.3:
"""
SHIVA3D = "FPSoftware\\startShiVa.bat"
"""Application path for ShiVa3D

:since 1.7:
"""

BROWSER_MODE = ':browser_mode:'
"""Application path for Flashpoint Browser Mode.

:since 1.7:
"""
CHROME = 'FPSoftware\\startChrome.bat'
"""Application path for Chrome.

:since 1.7:
"""
NETSCAPE = 'FPSoftware\\startNetscape.bat'
"""Application path for Netscape.

:since 1.7:
"""
FPNAVIGATOR = 'FPSoftware\\fpnavigator-portable\\FPNavigator.exe'
"""Application path for Flashpoint Navigator.

:since 1.8:
"""

APPLICATIONS = [
    SECURE_PLAYER,
    UNITY, JAVA, JAVA_IN_BROWSER,
    BASILISK, BROWSER_MODE, CHROME, NETSCAPE, FPNAVIGATOR,
    ACTIVE_X, GROOVE, SVR, SHIVA3D
]
"""A set of all valid application paths.

:since 1.3:
"""
APPLICATIONS.extend([FLASH_PLAYERS[key] for key in FLASH_PLAYERS])
APPLICATIONS.extend([SHOCKWAVE_PLAYERS[key] for key in SHOCKWAVE_PLAYERS])
APPLICATIONS = set(APPLICATIONS)

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

LANGUAGES = {'ab','aa','af','ak','sq','am','ar','an','hy','as','av','ae','ay','az','bm','ba','eu','be','bn','bh','bi','bs','br','bg','my','ca','ch','ce','ny','zh','cv','kw','co','cr','hr','cs','da','dv','nl','dz','en','eo','et','ee','fo','fj','fi','fr','ff','gl','ka','de','el','gn','gu','ht','ha','he','hz','hi','ho','hu','ia','id','ie','ga','ig','ik','io','is','it','iu','ja','jv','kl','kn','kr','ks','kk','km','ki','rw','ky','kv','kg','ko','ku','kj','la','lb','lg','li','ln','lo','lt','lu','lv','gv','mk','mg','ms','ml','mt','mi','mr','mh','mn','na','nv','nd','ne','ng','nb','nn','no','ii','nr','oc','oj','cu','om','or','os','pa','pi','fa','pl','ps','pt','qu','rm','rn','ro','ru','sa','sc','sd','se','sm','sg','sr','gd','sn','si','sk','sl','so','st','es','su','sw','ss','sv','ta','te','tg','th','ti','bo','tk','tl','tn','to','tr','ts','tt','tw','ty','ug','uk','ur','uz','ve','vi','vo','wa','cy','wo','fy','xh','yi','yo','za','zu'}
"""A set of all ISO 639-1 language codes copy and pasted from Wikipedia.

:since 1.3:
"""
LIBRARIES = {'arcade', 'theatre'}
"""Set of all Flashpoint libraries.

:since 1.3:
"""
PLAY_MODES = {'Cooperative', 'Multiplayer', 'Single Player'}
"""Set of all Flashpoint play modes. :code:`; ​` (a semi-colon followed by a space) can be used to combine them."""
# HACK: There is a zero-width-space between the space and the ending `. This is to trick sphinx into finding the end quote.
# An older version of sphinx could handle this fine, but this was a necessary hack in the newer versions.
STATUSES = {'Hacked', 'Not Working', 'Partial', 'Playable', 'Hacked; Partial', 'Partial; Hacked'}
"""Set of all valid Flashpoint statuses.

:since 1.3:
"""

MONTHS = {
    "JANUARY": "01",
    "FEBRUARY": "02",
    "MARCH": "03",
    "APRIL": "04",
    "MAY": "05",
    "JUNE": "06",
    "JULY": "07",
    "AUGUST": "08",
    "SEPTEMBER": "09",
    "OCTOBER": "10",
    "NOVEMBER": "11",
    "DECEMBER": "12",
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12",
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}
"""A dictionary mapping uppercase month names to 2 number month codes."""

DEBUG_LEVEL = 1
"""A global value that determines what debug information gets printed. This applies to the whole module, and you can modify it when you want to. Possible values:

* **0**: Don't print any debug information.
* **1**: *Default*; prints only basic information along with errors and warnings for curations. Does not care about :data:`TABULATION`.
* **2+**: Print extra information about function and method calls. The extra information that will be printed is determined by the level of :data:`TABULATION` when the information is printed; i.e., mode 2 will print only the first level of tabulation, mode 3 will print up to the second level of tabulation, etc.
* **-1**: Print all debug information.

:seealso: :func:`debug()`

:since 1.3:
"""
TABULATION = 0
"""Determines the current level of tabulation for the :func:`debug()` command. Each integer level adds 2 spaces. Several functions will use this to print nested debugging information.

:since 1.3:
"""
PLATFORMS = set()
"""A set of all valid platforms for Flashpoint to be generated with :func:`update()` through :func:`get_fpdata('Platforms', True)`. This list is empty until :func:`update()` is called.

:since 1.3:
"""
TAGS = set()
"""A set of all valid tags for Flashpoint to be generated with :func:`update()` through :func:`get_fpdata('Tags', True)`. This list is empty until :func:`update()` is called.

:since 1.3:
"""

class InvalidCharacterError(ValueError):
    """An error caused when attempting to read from or write to file name that has invalid characters in it."""
    pass
class InvalidFileError(IOError):
    """An error caused when attempting to read or write to a file that isn't a file (e.g., a directory)."""
    pass
class EmptyLocationError(ValueError):
    """An error caused when attempting to read or write to a file or create a folder with no name."""
    pass
class InvalidMetadataError(ValueError):
    """An error caused when a curation has invalid metadata.

    :since 1.3:
    """
    pass

def test():
    """Tests the library to make sure it works.

    This test will curate "Interactive Buddy" and download the swf file linked in the launch command into the proper place in a folder in the working directory, while also testing basic validation.

    :raises AssertionError: If the test gives back any errors.
    """
    print('Testing curation abilities.\n')
    global DEBUG_LEVEL, TABULATION
    temp_debug = None
    if DEBUG_LEVEL > 0:
        temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, -1
    try:
        tc = TestCuration()
        tc.save()
        delete(tc.id)

        bc = BrokenCuration()
        bc.parse(None)
        assert len(bc.get_errors()) == 13
        print('\nTesting finished successfully.')
    except KeyboardInterrupt:
        print('\nTesting interrupted.')
    except:
        raise AssertionError('The test has failed. Be wary when using this library.')
    finally:
        if temp_debug is not None:
            DEBUG_LEVEL = temp_debug

def update():
    """Initializes or updates variables that are generated from online. The only ones are :data:`PLATFORMS` and :data:`TAGS`.

    This method is only automatically called by :func:`Curation.validate()` if `rigid` is True and either :data:`PLATFORMS` or :data:`TAGS` are not set. You must call this function manually if you want to access :data:`PLATFORMS` or :data:`TAGS` before then.

    :since 1.3:
    """
    debug('Getting updated Platforms and Tags', 2, pre='[FUNC] ')
    global PLATFORMS, TAGS, TABULATION
    TABULATION += 1
    PLATFORMS = set(get_fpdata('Platforms'))
    TAGS = set(get_fpdata('Tags'))
    TABULATION -= 1

def debug(text, mode, *items, pre='[INFO] '):
    """Prints :code:`text` depending on :code:`mode` and :data:`DEBUG_LEVEL`.

    :param str text: A string of text to print.
    :param int mode: :code:`text` will only be printed in two cases: if this is 1 and :data:`DEBUG_LEVEL` > 0 - or if this is 2, :data:`DEBUG_LEVEL` is 2 or higher, and :code:`DEBUG_LEVEL - 1 > TABULATION`.
    :param * items: Any number of items to format :code:`text` with. Uses :code:`str.format()`.
    :param str pre: This is a prefix of text to print to the left of :code:`text`. This must be a key argument.

    :since 1.3:
    """
    global DEBUG_LEVEL, TABULATION
    if TABULATION < 0:
        TABULATION = 0
    if DEBUG_LEVEL < 0 or (DEBUG_LEVEL > 0 and (mode == 1 or (DEBUG_LEVEL > 1 and DEBUG_LEVEL - 1 > TABULATION))):
        tabs = '  ' * TABULATION
        full_texts = (tabs + pre + text.format(*items)).split('\n')

        full_text = full_texts[0]
        length = len(full_text)
        columns = shutil.get_terminal_size()[0] - 1
        if length <= columns:
            print(full_text)
        else:
            print(full_text[0:columns])
            tab_len = len(tabs) + len(pre)
            tabs = ' ' * tab_len
            i = columns
            length -= columns
            available = columns - tab_len
            while length + tab_len > columns:
                print(tabs + full_text[i:i+available].strip())
                i += available
                length -= available
            print(tabs + full_text[i:].strip())

        if len(full_texts) > 1:
            temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, -1
            try:
                e_pre = ' ' * len(pre)
                for full_text in full_texts[1:]:
                    debug(full_text, mode, pre=e_pre)
            finally:
                DEBUG_LEVEL = temp_debug

def download(url, loc='', name=None, spoof=False, **kwargs):
    """Downloads the webpage or file at :code:`url` to the location :code:`loc`.

    :param str url: A url pointing to a file to be downloaded.
    :param str loc: A folder to download to; leave blank for the current working directory. If the folder doesn't exist, it will be created automatically.
    :param str name: If specified, the file will be saved with this name instead of an automatically generated one.
    :param bool spoof: *Added in 1.10*: If True, sets the referrer header to the url itself. Merges with any existing headers, but does not override them.
    :param ** kwargs: *Added in 1.2*: A collection of arguments to request with. Same format as :code:`requests.get()`, but without the url parameter.
    """
    debug('Call to download "{}"', 2, url, pre='[FUNC] ')
    global TABULATION
    TABULATION += 1
    try:
        rurl = normalize(url, True, True, True)
        raw = WAYBACK_LINK.sub('', rurl)
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

        if loc:
            debug('Downloading "{}" from "{}" to "{}"', 2, file_name, rurl, loc)
        else:
            debug('Downloading "{}" from "{}"', 2, file_name, rurl)

        headers = kwargs.get("headers", {})
        if spoof and not ("referer" in headers or "Referer" in headers or "REFERER" in headers):
            headers["referer"] = rurl

        with requests.get(rurl, **kwargs, headers=headers or None) as response:
            if loc:
                make_dir(loc)
                file_name = os.path.join(loc, file_name)
            with open(file_name, 'wb') as file:
                file.write(response.content)
    finally:
        TABULATION -= 1

def download_all(urls, loc='', preserve=False, keep_vars=False, ignore_errs=False, spoof=False, **kwargs):
    """Downloads a list of files with their website folder structure to the location :code:`loc`.

    For those that are familiar with cURLsDownloader, this function acts in a similar way. Invalid characters for a file/folder name will be replaced with "_", but "://" will be replaced with ".".

    :param [str|(str,dict),....] urls: A list of urls pointing to files to be downloaded. *Since 1.2*, if a url is a tuple instead of a string, the first item in the tuple will be read as the url and the second will be read a dictionary of arguments to request with. The dictionary of arguments is in a similar format to the arguments :code:`requests.get()` uses, but without the url parameter.
    :param str loc: A folder to download to; leave blank for the current working directory. If the folder doesn't exist, it will be created automatically.
    :param bool preserve: If True, any files from "web.archive.org" will stay in the "web.archive.org" folder. By default, files are moved to their original domains with any port numbers removed.
    :param bool keep_vars: If True, files will be saved with all urlvars intact in their file name. This prevents files such as "http://www.example.com/game.php?id=123" and "http://www.example.com/game.php?id=321" from overwriting each other. Question marks are replaced with "_".
    :param bool ignore_errs: If True, any errors will be ignored and returned as part of a tuple including the urls that failed alongside each error.
    :param bool spoof: *Added in 1.10*: If True, sets the referrer header to the url itself. Merges with any existing headers, but does not override them.
    :param ** kwargs: *Added in 1.10*: A collection of arguments to request with in all arguments. Same format as :code:`requests.get()`, but without the url parameter. Overwritten by arguments provided by `urls`.

    :returns: None or a list of tuples including failed urls and errors.
    """
    debug('Call to download {} files or webpages', 2, len(urls), pre='[FUNC] ')
    global TABULATION
    TABULATION += 1
    try:
        if loc:
            cwd = os.getcwd()
            make_dir(loc, True)
    finally:
        TABULATION -= 1
    TABULATION += 1
    errs = []
    try:
        i = 0
        for item in urls:
            debug('Checking url index {}', 2, i)
            TABULATION += 1
            try:
                if isinstance(item, tuple):
                    (url, data) = item
                else:
                    url = item
                    data = {}

                rurl = normalize(url, True, True, True)
                raw = rurl if preserve else normalize(url, False, True, True)
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

                headers = data.get("headers", kwargs.get("headers", {}))
                if spoof and not ("referer" in headers or "Referer" in headers or "REFERER" in headers):
                    headers["referer"] = rurl

                debug('Downloading "{}" from "{}"', 2, raw, rurl)
                TABULATION += 1
                try:
                    with requests.get(rurl, **kwargs, **data, headers=headers or None) as response:
                        make_dir(os.path.dirname(raw))
                        with open(raw, 'wb') as file:
                            file.write(response.content)
                finally:
                    TABULATION -= 1
                TABULATION -= 1
            except Exception as e:
                TABULATION -= 1
                if ignore_errs:
                    errs.append((url, e))
                    debug('Skipping downloading "{}", error:\n  {}', 1, url, str(e), pre='[ERR]  ')
                else:
                    raise e
            i += 1
    finally:
        TABULATION -= 1
        if loc:
            os.chdir(cwd)

    if ignore_errs:
        return errs

def download_image(url, loc='', name=None, spoof=False, **kwargs):
    """Downloads the image from :code:`url` to the location :code:`loc` as a PNG file.

    :param str url: A url pointing to the image to be downloaded.
    :param str loc: A folder to download to; leave blank for the current working directory. If the folder doesn't exist, it will be created automatically.
    :param str name: If specified, the file will be saved with this name instead of an automatically generated one.
    :param bool spoof: *Added in 1.10*: If True, sets the referrer header to the url itself. Merges with any existing headers, but does not override them.
    :param ** kwargs: *Added in 1.2*: A collection of arguments to request with. Same format as :code:`requests.get()`, but without the url parameter.
    """
    debug('Call to download image "{}"', 2, url, pre='[FUNC] ')
    global TABULATION
    TABULATION += 1
    try:
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

        if loc:
            debug('Downloading image "{}" from "{}" to "{}"', 2, file_name, rurl, loc)
        else:
            debug('Downloading image "{}" from "{}"', 2, file_name, rurl)

        headers = kwargs.get("headers", {})
        if spoof and not ("referer" in headers or "Referer" in headers or "REFERER" in headers):
            headers["referer"] = rurl

        TABULATION += 1
        try:
            with requests.get(rurl, **kwargs, headers=headers) as response:
                img = Image.open(BytesIO(response.content))
                if loc:
                    make_dir(loc)
                    file_name = os.path.join(loc, file_name)
        finally:
            TABULATION -= 1

        img.save(file_name, format='PNG')
    finally:
        TABULATION -= 1

def normalize(url, preserve=True, keep_vars=False, keep_prot=False):
    """Formats :code:`url` to a normalized format.

    This involves making it use the http protocol, fixing escaped slashes (:code:`\\/`), removing url vars, and stripping it. Accepts strings starting with any protocol, no protocol, "//", or "/".

    :param str url: A string url to format.
    :param bool preserve: If False and the url is from "web.archive.org", the url will be formatted to it's original domain without the "web.archive.org" prefix.
    :param bool keep_vars: If True, url vars at the end of the string will stay on the string.
    :param bool keep_prot: If True, the url protocol will not be made to use the http protocol unless there is no protocol given or the protocol is formatted incorrectly.

    :returns: :code:`url` in a normalized format, or None if :code:`url` is None.
    """
    if url == None:
        return None

    rurl = url.replace('\\/', '/').strip()
    if not keep_vars and '?' in rurl:
        rurl = rurl[:rurl.find('?')]
    if not preserve:
        rurl = WAYBACK_LINK.sub('', rurl)
    if PROTOCOL.search(rurl) is not None:
        if keep_prot:
            if PROPER_PROTOCOL.search(rurl) is None:
                rurl = PROTOCOL.sub('http://', rurl)
        else:
            rurl = PROTOCOL.sub('http://', rurl)
    else:
        rurl = 'http://' + rurl
    if rurl != url:
        debug('Normalized url "{}" to "{}"', 2, url, rurl, pre='[FUNC] ')

    return rurl

def read_url(url, ignore_errs=True, content=False, spoof=False, **kwargs):
    """Reads the webpage or file at :code:`url` and returns its contents as a text string.

    :param str url: A string url of a webpage or file.
    :param bool ignore_errs: *Added in 1.3*: If False, instead of returning None on any errors, those errors will be raised.
    :param bool content: *Added in 1.3* If True, this function will return the contents of the webpage or file as a byte string instead of reading it as text (:code:`response.content` instead of :code:`response.text`).
    :param bool spoof: *Added in 1.10*: If True, sets the referrer header to the url itself. Merges with any existing headers, but does not override them.
    :param ** kwargs: *Added in 1.2*: A collection of arguments to request with. Same format as :code:`requests.get()`, but without the url parameter.

    :returns: The contents of the webpage at :code:`url` as a string or None if the url is blank.
    """
    debug('Call to read "{}"', 2, url, pre='[FUNC] ')
    if not url:
        return None
    global TABULATION
    TABULATION += 1
    try:
        rurl = normalize(url, True, True, True)

        headers = kwargs.get("headers", {})
        if spoof and not ("referer" in headers or "Referer" in headers or "REFERER" in headers):
            headers["referer"] = rurl

        with requests.get(rurl, **kwargs, headers=headers or None) as response:
            if content:
                contents = response.content
            else:
                contents = response.text
        return contents
    except Exception as e:
        if ignore_errs:
            return None
        raise e
    finally:
        TABULATION -= 1

def get_soup(url, parser='html.parser', ignore_errs=True, spoof=False, **kwargs):
    """Reads the webpage at :code:`url` and creates a BeautifulSoup object with it.

    :param str url: A string url of a webpage.
    :param str parser: The BeautifulSoup parser to use.
    :param bool ignore_errs: *Added in 1.3*: If False, instead of returning None on any errors, those errors will be raised.
    :param bool spoof: *Added in 1.10*: If True, sets the referrer header to the url itself. Merges with any existing headers, but does not override them.
    :param ** kwargs: *Added in 1.2*: A collection of arguments to request with. Same format as :code:`requests.get()`, but without the url parameter.

    :returns: A BeautifulSoup object created from :code:`url` or None if the url is blank or there was an error and :code:`ignore_errs` is True.
    """
    debug('Getting soup object for "{}"', 2, url, pre='[FUNC] ')
    if not url:
        return None
    global TABULATION
    TABULATION += 1
    try:
        rurl = normalize(url, True, True, True)

        headers = kwargs.get("headers", {})
        if spoof and not ("referer" in headers or "Referer" in headers or "REFERER" in headers):
            headers["referer"] = rurl

        with requests.get(rurl, **kwargs, headers=headers or None) as response:
            if response.status_code >= 400: raise ValueError("Bad response code")
            # Screw weird ascii pages
            soup = BeautifulSoup(response.content.decode("utf-8"), parser)
        return soup
    except Exception as e:
        if ignore_errs:
            return None
        raise e
    finally:
        TABULATION -= 1

def get_fpdata(page, ignore_errs=True):
    """Reads the Flashpoint online datahub at :code:`https://flashpointarchive.org/datahub/{page}` and returns a list of possible values; you can use this to get the most up-to-date tags and platforms. It will automatically check the web archive if the given wiki page is down.

    :param str page: Can be "Platforms", "Tags", or any other page on the datahub with tables in it.
    :param bool ignore_errs: If False, instead of returning None on any errors, those errors will be raised.

    :returns: A list of all Platforms, Tags, etc. depending on each page, or an empty list on failure.

    :since 1.3:
    """
    debug('Getting "{}" from Flashpoint datahub', 2, page, pre='[FUNC] ')
    global TABULATION
    TABULATION += 1
    try:
        soup = None
        url = 'https://flashpointarchive.org/datahub/' + page
        rurl = url
        timestamp = None
        for i in range(4): # Try up to 4 times
            try:
                soup = get_soup(rurl, ignore_errs=False, timeout=5)
                if soup and not soup.select_one("#cf-error-details"): break
            except (ValueError, requests.ReadTimeout):
                if timestamp: timestamp -= datetime.timedelta(days=2)
                else: timestamp = datetime.datetime.now()
                rurl = f'https://web.archive.org/web/{timestamp.year}{timestamp.month:02}{timestamp.day:02}id_/' + url
        print(rurl)
        items = []
        i = 0
        if page == "Platforms": i = 1

        for table in soup.find_all('table', class_='wikitable'):
            for row in table.find_all('tr')[1:]:
                try:
                    name = row.find_all('td')[i].text.strip()
                    if name:
                        items.append(name)
                except:
                    pass

        if page == 'Tags':
            items.extend([item.text for item in soup.find_all('span', class_='mw-headline') if item.text not in {'Themes', 'Content Warnings', 'Franchises', 'Game Engines'}])
        elif page in ["Game_Master_List", "Animation_Master_List"]:
            last = soup.find('div', class_='mw-parser-output').find_all('h2')[-1].next_sibling
            if last is not None and last.name == 'ul':
                for item in last.find_all('li'):
                    items.append(STARTING_PARENTHESES.sub('', item.text))
        return items
    except Exception as e:
        if ignore_errs:
            return []
        else:
            raise e
    finally:
        TABULATION -= 1

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
    fname = str(file_name)
    debug('Reading file "{}"', 2, fname, pre='[FUNC] ')
    if not fname:
        raise EmptyLocationError('Cannot read a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(fname) is not None:
        raise InvalidCharacterError('File name "' + fname + '" contains invalid characters.')
    if os.path.exists(fname) and not os.path.isfile(fname):
        raise InvalidFileError('"' + fname + '" is not a file and cannot be read from.')

    with codecs.open(fname, 'r', 'utf-8') as file:
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
    fname = str(file_name)
    debug('Reading file "{}" into lines', 2, fname, pre='[FUNC] ')
    if not fname:
        raise EmptyLocationError('Cannot read a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(fname) is not None:
        raise InvalidCharacterError('File name "' + fname + '" contains invalid characters.')
    if os.path.exists(fname) and not os.path.isfile(fname):
        raise InvalidFileError('"' + fname + '" is not a file and cannot be read from.')

    with codecs.open(fname, 'r', 'utf-8') as file:
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
    fname = str(file_name)
    debug('Reading file "{}" into table', 2, fname, pre='[FUNC] ')
    global DEBUG_LEVEL, TABULATION
    temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, 0
    TABULATION += 1
    try:
        output = [line.split(delimiter) for line in read_lines(fname, ignore_lines)]
    finally:
        TABULATION -= 1
        DEBUG_LEVEL = temp_debug
    return output


def read_config(config="clients.txt", paths=["."]):
    """Searches for and reads/merges any config files in `paths`

    Config files support comments (lines starting with "#"), and data lines are in key=value format. Any whitespace before and after the = will be stripped.

    If no config files can be found, this function returns an empty dictionary.

    :param str config: The name of the config file to look for and read from.
    :param [str,...] paths: A list of paths to look for config files in. Defaults to the current working directory.

    :returns: A dictionary of key=value pairs, or an empty dictionary if no config files can be found.

    :raises EmptyLocationError: If :code:`config` is an empty string.
    :raises InvalidCharacterError: If :code:`config` or :data:`CONFIG_PATH` contains invalid characters.
    :raises InvalidFileError: If any :code:`config` file is not a valid file.

    :since 1.9:
    """
    debug('Searching for config file "{}"', 2, config, pre='[FUNC] ')
    global DEBUG_LEVEL, TABULATION
    temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, 0
    TABULATION += 1
    try:
        if not config:
            raise EmptyLocationError('Cannot find a config file with no name.')
        config_data = {}
        for path in reversed(paths):
            try:
                fname = os.path.join(path, config)
                for rline in read_lines(fname):
                    line = rline.strip()
                    if not line or line[0] == "#": continue
                    try:
                        key, value = line.split("=", 1)
                        config_data[key.strip()] = value.strip()
                    except:
                        debug('Config file "{}" contains invalue ', 1, fname, pre='[WARN] ')
            except FileNotFoundError: pass
        return config_data
    finally:
        TABULATION -= 1
        DEBUG_LEVEL = temp_debug


def scan_dir(folder=None, regex=None, recursive=True):
    """Scans the directory :code:`folder` recursively and returns all files and sub-folders as two lists.

    :param str folder: A directory to scan. Defaults to the current working directory.
    :param str|re regex: If given, this function will only return files whose full paths match this regex. This has no effect on sub-folders.
    :param bool recursive: If False, this function will not scan sub-folders recursively. You might be better off using :code:`os.walk()` if you set this to False.

    :returns: files and subfolders as two lists in that order. :code:`return files, subfolders`

    :raises InvalidCharacterError: If :code:`folder` contains invalid characters.
    :raises FileExistsError: If :code:`folder` is not a folder.
    :raises FileNotFoundError: If :code:`folder` does not exist.

    :note: On Windows, backslashes (:code:`\\\\`) will be replaced by slashes (:code:`/`), and this is what regexes match against.

    :since 1.4:
    """
    if not folder:
        folder = os.getcwd()
    if os.name == "nt":
        folder = folder.replace('\\', '/')

    if recursive:
        debug('Scanning folder "{}" recursively', 2, folder, pre='[FUNC] ')
    else:
        debug('Scanning folder "{}"', 2, folder, pre='[FUNC] ')

    def scan(folder, r):
        files, folders = [], []
        for f in os.scandir(folder):
            if f.is_dir():
                folders.append(f.path)
            elif r == None or r.fullmatch(f.path):
                files.append(f.path)
        return files, folders

    if isinstance(regex, str):
        rext = re.compile(regex)
    else:
        rext = regex

    if INVALID_CHARS_NO_SLASH.search(folder) is not None:
        raise InvalidCharacterError('Folder "' + folder + '" contains invalid characters.')
    if os.path.exists(folder):
        if os.path.isdir(folder):
            files, folders = scan(folder, rext)
            if recursive:
                for f in folders:
                    nf, no = scan(f, rext)
                    files.extend(nf)
                    folders.extend(no)
            return files, folders
        else:
            raise FileExistsError('"' + folder + '" is not a folder.')
    else:
        raise FileNotFoundError('Could not find folder "' + folder + '"')


def make_dir(folder, change=False, overwrite=False):
    """Makes a folder at :code:`folder`, along will all parent folders.

    It will not raise a FileExistsError if the folder already exists, but will instead return False.

    :param str folder: A string location to create a folder.
    :param bool change: If True, this function will set the new folder as the working directory.
    :param bool overwrite: If True, if there is a non-folder file in the same location as the folder being created, the folder will overwrite this file.

    :raises EmptyLocationError: If :code:`folder` is an empty string.
    :raises InvalidCharacterError: If :code:`folder` contains invalid characters.
    :raises FileExistsError: If a non-folder file exists in the location given by :code:`folder` and overwrite is not set.

    :returns: True on successful folder creation, False on failure.

    :note: Even if folder creation fails, if :code:`change` is True, the working directory will still be changed to that folder.
    """
    sfolder = str(folder)
    if change:
        debug('Making folder at "{}" and setting it to working directory', 2, sfolder, pre='[FUNC] ')
    else:
        debug('Making folder at "{}"', 2, sfolder, pre='[FUNC] ')

    if not sfolder:
        raise EmptyLocationError('Cannot create a folder with no name.')
    if INVALID_CHARS_NO_SLASH.search(sfolder) is not None:
        raise InvalidCharacterError('Folder "' + sfolder + '" contains invalid characters.')

    r = True
    if os.path.exists(sfolder):
        if not os.path.isdir(sfolder):
            if overwrite:
                os.unlink(sfolder)
                os.makedirs(sfolder)
            else:
                raise FileExistsError('Cannot create the folder "' + sfolder + '" because a non-folder file is there. Use argument "overwrite=True" to overwrite.')
        else:
            r = False
    else:
        os.makedirs(sfolder)

    if change:
        os.chdir(sfolder)

    return r

def delete(file_name):
    """Deletes the file or folder :code:`file_name` recursively.

    It will not raise a FileNotFoundError if the file or folder doesn't exist, but will instead return False.

    :param str file_name: A string location of a file or folder to delete.

    :returns: True on successful deletion, False on failure.

    :raises EmptyLocationError: If :code:`file_name` is an empty string.
    :raises InvalidCharacterError: If :code:`file_name` contains invalid characters.
    """
    fname = str(file_name)
    debug('Deleting "{}"', 2, fname, pre='[FUNC] ')
    if not fname:
        raise EmptyLocationError('Cannot delete a file or folder with no name.')
    if INVALID_CHARS_NO_SLASH.search(fname) is not None:
        raise InvalidCharacterError('Folder "' + fname + '" contains invalid characters.')

    if os.path.exists(fname):
        if os.path.isdir(fname):
            shutil.rmtree(fname)
        else:
            os.unlink(fname)
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
    fname = str(file_name)
    debug('Writing contents to "{}"', 2, fname, pre='[FUNC] ')
    if not fname:
        raise EmptyLocationError('Cannot write to a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(fname) is not None:
        raise InvalidCharacterError('File name "' + fname + '" contains invalid characters.')
    if os.path.exists(fname) and not os.path.isfile(fname):
        if force:
            if os.path.isdir(fname):
                shutil.rmtree(fname)
            else:
                os.unlink(fname)
        else:
            raise InvalidFileError('"' + fname + '" is not a file and cannot be written to. Use argument "force=True" to overwrite.')

    if isinstance(contents, bytes):
        output = contents.decode('utf-8')
    elif not isinstance(contents, str) and isinstance(contents, Iterable):
        output = '\n'.join(contents)
    else:
        output = contents

    global TABULATION
    TABULATION += 1
    try:
        folder = os.path.dirname(fname)
        if folder:
            make_dir(folder)
        with codecs.open(fname, 'w', 'utf-8') as file:
            file.write(output)
    finally:
        TABULATION -= 1

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
    fname = str(file_name)
    debug('Writing line to "{}"', 2, fname, pre='[FUNC] ')
    if not fname:
        raise EmptyLocationError('Cannot write to a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(fname) is not None:
        raise InvalidCharacterError('File name "' + fname + '" contains invalid characters.')
    if os.path.exists(fname) and not os.path.isfile(fname):
        if force:
            if os.path.isdir(fname):
                shutil.rmtree(fname)
            else:
                os.unlink(fname)
        else:
            raise InvalidFileError('"' + fname + '" is not a file and cannot be written to. Use argument "force=True" to overwrite.')

    global TABULATION
    TABULATION += 1
    try:
        folder = os.path.dirname(fname)
        if folder:
            make_dir(folder)
        with codecs.open(fname, 'a', 'utf-8') as file:
            file.write(line + '\n')
    finally:
        TABULATION -= 1

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
    fname = str(file_name)
    debug('Writing table to "{}"', 2, fname, pre='[FUNC] ')
    if not fname:
        raise EmptyLocationError('Cannot write to a file with no name.')
    if INVALID_CHARS_NO_SLASH.search(fname) is not None:
        raise InvalidCharacterError('File name "' + fname + '" contains invalid characters.')
    if os.path.exists(fname) and not os.path.isfile(fname):
        if force:
            if os.path.isdir(fname):
                shutil.rmtree(fname)
            else:
                os.unlink(fname)
        else:
            raise InvalidFileError('"' + fname + '" is not a file and cannot be written to. Use argument "force=True" to overwrite.')

    global TABULATION
    TABULATION += 1
    try:
        folder = os.path.dirname(fname)
        if folder:
            make_dir(folder)
        with codecs.open(fname, 'w', 'utf-8') as file:
            file.write('\n'.join([delimiter.join(line) for line in table]))
    finally:
        TABULATION -= 1

def replace(files, old, new, regex=None, ignore_errs=True):
    """Replaces all instances of :code:`old` with :code:`new` in :code:`files`.

    :param [str,....]|str files: A string or list of strings pointing to files to have their contents changed.
    :param str|re old: A regex or string to replace. If this is a string, it will not be treated as a regex. Use :code:`re.compile()` to pass in a regex object.
    :param str new: A string of text to replace with.
    :param str|re regex: If given, this function will only replace in files whose full paths match this regex. It must be a real regex (i.e., you can't use "*" in place of ".*")!
    :param bool ignore_errs: If False, this function will throw an error at the end if :code:`files` had invalid files.

    :raises: A bulk ValueError if :code:`files` has any invalid files and :code:`ignore_errs` is False. Errors will be thrown at the end of the function after everything that could be replaced was replaced.

    :since 1.4:
    """
    if isinstance(files, str):
        file_names = [files]
    else:
        file_names = files

    debug('Replacing contents in {} files', 2, len(file_names), pre='[FUNC] ')

    errs = []
    global DEBUG_LEVEL, TABULATION
    temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, 0
    try:
        if isinstance(regex, str):
            rext = re.compile(regex)
        else:
            rext = regex

        for file_name in file_names:
            if rext != None and not rext.fullmatch(file_name):
                continue
            try:
                with codecs.open(file_name, 'r', 'utf-8') as file:
                    ct = file.read()
                if isinstance(old, str):
                    nct = ct.replace(old, new)
                else:
                    nct = old.sub(new, ct)
                if nct != ct:
                    with codecs.open(file_name, 'w', 'utf-8') as file:
                        file.write(nct)
            except Exception as e:
                errs.append(e)
    finally:
        DEBUG_LEVEL = temp_debug

    if errs:
        msg = '{} files had problems'.format(len(errs))
        if ignore_errs:
            TABULATION += 1
            try:
                debug(msg, 2, pre='[ERR] ')
            finally:
                TABULATION -= 1
        else:
            raise ValueError(msg)

def hash256(obj):
    """Serializes :code:`obj` and then returns a sha256 HASH object of it.

    Two objects that yield the same bytes representation will yield the same hash.

    :param obj: An object to hash.

    :returns: A sha256 HASH object of :code:`obj`.

    :seealso: Python's `hashlib <https://docs.python.org/3/library/hashlib.html>`_ library. The object returned is the same object created by :code:`hashlib.sha256()`.
    """
    debug('Hashing object', 2)
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
    debug('Quick-hashing object', 2)
    return int.from_bytes(hash256(obj).digest()[:4], byteorder="big", signed=True)

def clear_save(loc=''):
    """Deletes the "c-info.tmp" file generated by :func:`curate()` and :func:`curate_regex()` in the current working directory or :code:`loc`.

    :param str loc: *Added in 1.3*: An optional location to clear the save file in. If not set, the directory will be the current working directory.

    It will not raise a FileNotFoundError if it doesn't exist. Returns True on success, and False on failure.
    """
    if loc:
        file = os.path.join(loc, 'c-info.tmp')
        debug('Clearing curation cache in "{}"', 2, loc)
    else:
        file = 'c-info.tmp'
        debug('Clearing curation cache', 2)
    global DEBUG_LEVEL, TABULATION
    temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, 0
    TABULATION += 1
    try:
        output = delete(file)
    finally:
        TABULATION -= 1
        DEBUG_LEVEL = temp_debug
    return output

def curate(items, curation_class, use_title=False, save=False, ignore_errs=False, overwrite=False, validate=1, config=None, config_paths=["."]):
    """Curates form a list of urls given by :code:`items` with a sub-class of :class:`Curation` specified by :code:`curation_class`.

    :param items [str|(str,dict),....]: normally a list of string urls of webpages to curate from, but if you put a tuple with 2 items in the place of any string, the first item in the tuple will be treated as the url, and the second item will be treated as a dictionary of arguments passed to an instance of :code:`curation_class` along with the url. You can mix tuples and strings.
    :param class curation_class: A sub-class of :class:`Curation` to create curations from. Note that this must be the *class* and not an object created from the class.
    :param bool use_title: If True, each curation folder will be generated with the title of the curation instead of its id.
    :param bool save: If True, progress will be constantly saved to "c-info.tmp" so that if the function errors and is ever called with the same :code:`items` variable in the same working directory again, it will resume where it left off. Note that calling this function again with a different list of :code:`items` will restart the process and the save file from any other processes.
    :param bool ignore_errs: If True, any error that a curation raises will be ignored and the curation will be skipped. Any failed items will be returned as a list of 3-length tuples at the end of the function with the item, the error, and a dictionary of additional arguments that were passed in.
    :param bool overwrite: If True, this method will mix and overwrite files in existing curation folders instead of making the folder "Curation (2)", "Curation (3)", etc.
    :param int validate: *Added in 1.3*: Mode to validate each curation to make sure it has proper metadata. 0 means do not validate, 1 (default) means flexibly validate, and 2 means rigidly validate. See :func:`Curation.get_errors()`. Invalid curations will not raise any errors and will be skipped; however, if ignore_errs is True, the curation will be returned with an :class:`InvalidMetadataError` in the list at the end of the function.
    :param str config: *Added in 1.9*: If specified, `config` and `config_paths` will be given to :func:`fpclib.read_config()` and the return value will be given to curations in their "config" metadata value.
    :param [str,...] config_paths: *Added in 1.9*: See `config`, given to :func:`fpclib.read_config()` to find config files.

    :returns: None or a list of tuples including failed urls, errors, and data passed in. The format for this is `[(str,Exception,dict),...]`

    :raises ValueError: If :code:`items` is empty.
    :raises TypeError: *Added in 1.3*: If :code:`curation_class` is not a subclass of :class:`Curation`.
    """
    isave = save
    if not items:
        raise ValueError('Items list is empty.')
    if not issubclass(curation_class, Curation):
        raise TypeError('Class "' + curation_class.__name__ + '" is not a subclass of fpclib.Curation')

    debug('Curating {} urls with class "{}"', 1, len(items), curation_class.__name__, pre='[FUNC] ')
    global TABULATION
    TABULATION += 1
    try:
        if isave:
            sid = hash256(items).digest()
            try:
                with open('c-info.tmp', 'rb') as temp:
                    new_sid = temp.read(32)
                    if new_sid == sid:
                        (i, errs, config_data) = pickle.load(temp)
                    else:
                        raise FileNotFoundError('Save file not found')
                debug('Found "c-info.tmp" for items, starting at index {}', 1, i)
            except FileNotFoundError:
                i = 0
                errs = []
                config_data = {} if config is None else read_config(config, config_paths)
        else:
            i = 0
            errs = []
            config_data = {} if config is None else read_config(config, config_paths)

        count = len(items)
        while i < count:
            if isave:
                with open('c-info.tmp', 'wb') as temp:
                    temp.write(sid)
                    pickle.dump((i, errs, config_data), temp)

            item = items[i]
            if isinstance(item, tuple):
                (item, data) = item
            else:
                data = {}

            debug('Curating index {}, "{}"', 1, i, item)
            TABULATION += 1
            try:
                curation_class(url=item, config=config_data, **data).save(use_title, overwrite, True, validate=validate)
            except InvalidMetadataError as e:
                debug('Skipping curation, {}', 1, str(e), pre='[WARN] ')
                errs.append((item, e, data))
            except KeyboardInterrupt as e:
                debug('Interrupt received, terminating curation process (but not clearing save)', 1)
                if ignore_errs:
                    errs.append((item, e, data))
                    return errs
                else:
                    return None
            except Exception as e:
                if not ignore_errs:
                    raise e
                debug('Skipping curation, error:\n  {}', 1, str(e), pre='[ERR]  ')
                errs.append((item, e, data))
            finally:
                TABULATION -= 1

            i += 1

        if isave:
            clear_save()

        if ignore_errs:
            return errs
    finally:
        TABULATION -= 1

def curate_regex(items, links, use_title=False, save=False, ignore_errs=False, overwrite=False, validate=1, config=None, config_paths=["."]):
    """Curates from a list of urls given by :code:`items` with a list of :code:`links`.

    :see: :func:`curate()`

    :param [str|(str,dict),....] items: A list of urls of webpages with games/animations to curate.
    :param [(str|re,class),....] links: A list of tuples containing a regex and a sub-class of :class:`Curation`. The function will search the url of each item for each of the regexes using :code:`re.search()`, and the first match will decide which sub-class gets used. If there are no matches, the curation would be skipped. A good example of the :code:`links` variable is something like :code:`[('newgrounds\\.com', NewgroundsCuration), ('kongregate\\.com', KongregateCuration)]`. Regexes can be strings or a :code:`re` object.
    :param bool use_title: Specifies whether or not to use the title or id of a curation for its folder.
    :param bool save: Specifies whether or not to save progress and continue where left off if the function is called with the same arguments.
    :param bool ignore_errs: Specifies whether or not to ignore errors and return them at the end of the function.
    :param bool overwrite: Whether or not to mix new curations with older folders with the same name.
    :param int validate: *Added in 1.3*: Mode to validate each curation to make sure it has proper metadata.

    :returns: None or a list of tuples including failed urls, errors, and data passed in. The format for this is `[(str,Exception,dict),...]`

    :raises ValueError: If :code:`items` or :code:`links` is empty.
    """
    isave = save
    if not items:
        raise ValueError('Items list is empty.')
    if not links:
        raise ValueError('Regex-curation links list is empty.')

    debug('Curating {} urls with {} links', 1, len(items), len(links), pre='[FUNC] ')
    global TABULATION
    TABULATION += 1

    try:
        rlinks = []
        for i in range(len(links)):
            link = links[i]
            if issubclass(link[1], Curation):
                if isinstance(link[0], str):
                    rlinks.append((re.compile(link[0]), link[1]))
                else:
                    rlinks.append(link)
            else:
                debug('Link {} class "{}" is not a subclass of fpclib.Curation, skipping it', 1, i, pre='[WARN] ')

        if not rlinks:
            raise ValueError('Regex-curation links list has no valid entries.')

        debug('{}/{} are valid links', 1, len(rlinks), len(links))

        if isave:
            sid = hash256(items).digest()
            try:
                with open('c-info.tmp', 'rb') as temp:
                    new_sid = temp.read(32)
                    if new_sid == sid:
                        (i, errs, config_data) = pickle.load(temp)
                    else:
                        raise FileNotFoundError('Save file not found')
                debug('Found "c-info.tmp" for items, starting at index {}', 1, i)
            except FileNotFoundError:
                i = 0
                errs = []
                config_data = {} if config is None else read_config(config, config_paths)
        else:
            i = 0
            errs = []
            config_data = {} if config is None else read_config(config, config_paths)

        count = len(items)
        while i < count:
            if isave:
                with open('c-info.tmp', 'wb') as temp:
                    temp.write(sid)
                    pickle.dump((i, errs, config_data), temp)

            item = items[i]
            if not isinstance(item, str) and isinstance(item, Iterable):
                (item, data) = item
            else:
                data = {}

            for link in rlinks:
                if re.search(link[0], item) is not None:
                    debug('Curating index {}, "{}", with class "{}"', 1, i, item, link[1].__name__)
                    TABULATION += 1
                    try:
                        link[1](url=item, config=config_data, **data).save(use_title, overwrite, True, validate=validate)
                    except InvalidMetadataError as e:
                        debug('Skipping curation, {}', 1, str(e), pre='[WARN] ')
                        errs.append((item, e, data))
                    except KeyboardInterrupt as e:
                        debug('Interrupt received, terminating curation process (but not clearing save)', 1)
                        if ignore_errs:
                            errs.append((item, e, data))
                            return errs
                        else:
                            return None
                    except Exception as e:
                        if not ignore_errs:
                            raise e
                        debug('Skipping curation, error:\n  {}', 1, str(e), pre='[ERR]  ')
                        errs.append((item, e, data))
                    finally:
                        TABULATION -= 1
                    break
            else:
                debug('Skipping index {}, "{}", no regex-matches found', 1, i, item, link[1].__name__)
            i += 1

        if isave:
            clear_save()

        if ignore_errs:
            return errs
    finally:
        TABULATION -= 1

def load(curation):
    """Loads the curation in the folder :code:`curation` into :class:`Curation` object using ruamel.yaml.

    :param str curation: A string pointing to the location of a folder where a curation is stored.

    :returns: A :class:`Curation` object created with the metadata of the curation in the folder :code:`curation`.

    :note: The curation at :code:`curation` curation must be using the yaml curation format.

    :raises InvalidCharacterError: If :code:`curation` has invalid characters.
    :raises FileNotFoundError: If the folder given is not a valid curation.
    """
    debug('Loading curation in folder "{}"', 2, curation)

    data = yaml.round_trip_load(read(os.path.join(curation, 'meta.yaml')))
    c = Curation()
    c.meta = dict(data)
    c.meta['Additional Applications'] = dict(c.meta['Additional Applications'])
    for app in c.meta['Additional Applications']:
        c.meta['Additional Applications'][app] = dict(c.meta['Additional Applications'][app])

    folder = curation.replace('\\', '/')
    if '/' in folder:
        folder = folder[folder.rfind('/'):]
    if UUID.fullmatch(folder):
        c.id = folder

    return c

class Curation:
    """This is the base class for every kind of curation. If you want a good tutorial on how to use this class, see :doc:`The Basics </basics>`. Extend this class to redefine it's methods. Constructor:

    Accepts a single :class:`Curation` object as an argument or arguments in the same format as :func:`Curation.set_meta()`. The new curation will first have it's metadata, logo, screenshot, added args, and id deep-copied from :code:`curation`'s first if it's available, then have that data modified with :code:`kwargs` if available. This curation object will be linked to that curation object.

    :raises TypeError: If :code:`curation` is not an instance of :class:`Curation`.
    """

    RESERVED_APPS = {'extras', 'message'}
    """A set containing all of the reserved headings that cannot be used in additional applications. The check is case-insensitive, hence they are lowercase."""

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

    You can find the description of each of these tags on the `Curation Format <https://flashpointarchive.org/datahub/Curation_Format#Metadata>`_ page on the Flashpoint wiki.
    """

    def __init__(self, curation=None, config={}, **kwargs):
        if not curation:
            self.meta = {
                'Title': None,
                'Alternate Titles': None,
                'Library': 'arcade',
                'Series': None,
                'Developer': None,
                'Publisher': None,
                'Play Mode': 'Single Player',
                'Release Date': None,
                'Version': None,
                'Languages': 'en',
                'Extreme': 'No',
                'Tags': None,
                'Source': None,
                'Platform': 'Flash',
                'Status': 'Playable',
                'Application Path': FLASH,
                'Launch Command': None,
                'Game Notes': None,
                'Original Description': None,
                'Curation Notes': None,
                'Additional Applications': {}
            }
            """A dictionary containing all metadata for the curation. While you can modify it directly, it is recommended that you use :func:`Curation.set_meta()` and :func:`Curation.get_meta()` instead."""
            self.args = {}
            """A dictionary containing all arguments passed in through :func:`Curation.set_meta()` that do not map to any metadata. You can use this to pass in extra information that you want to use in :func:`Curation.parse()` or other methods for custom classes."""

            self.logo = None
            """A url pointing to an image to be used as the logo for this curation. Any non-PNG files will be converted into PNG files when downloaded. You can modify it at will."""
            self.ss = None
            """A url pointing to an image to be used as the screenshot for this curation. Any non-PNG files will be converted into PNG files when downloaded. You can modify it at will."""

            self.config = config
            """Config data that is passed in by :func:`fpclib.curate()` and :func:`fpclib.curate_regex()`"""

            self.id = str(uuid.uuid4())
            """A string UUID identifying this curation. By default this is the name of the folder the curation will be saved to when :func:`Curation.save()` is called. You can re-generate an id by using :func:`Curation.new_id()`."""
        elif isinstance(curation, Curation):
            self.meta = copy.deepcopy(curation.meta)
            self.args = copy.deepcopy(curation.args)
            self.logo = curation.logo
            self.ss = curation.ss
            self.id = curation.id
        else:
            raise TypeError('curation object given is not an instance of fpclib.Curation')
        debug('Created new curation object {}', 2, str(self))

        global DEBUG_LEVEL
        temp_debug, DEBUG_LEVEL = DEBUG_LEVEL, 0
        try:
            self.set_meta(**kwargs)
        finally:
            DEBUG_LEVEL = temp_debug

    def new_id(self):
        """Generate a new uuid for this curation.

        :see: :attr:`Curation.id`
        """
        debug('Regenerating id for curation {}', 2, str(self), pre='[FUNC] ')
        self.id = str(uuid.uuid4())

    def __setattr__(self, name, value):
        if name in Curation.ARGS:
            if value == '':
                self.meta[Curation.ARGS[name]] = None
            else:
                self.meta[Curation.ARGS[name]] = value
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        try:
            if name in Curation.ARGS:
                return self.meta[Curation.ARGS[name]]
            else:
                return self.args[name]
        except KeyError:
            return object.__getattribute__(self, name)

    def set_meta(self, **kwargs):
        """Set the metadata with :code:`kwargs`. This method does not do error checking.

        :since 1.5: You can also just set the metadata directly through the curation instead; e.g., :code:`curation.title = 'Title Goes Here'`

        :param ** kwargs: A list of arguments to set the metadata with. To see what you can use for :code:`kwargs`, see :attr:`Curation.ARGS`. Any value passed in that is not in :attr:`Curation.ARGS` will still be stored and can be retrieved through :func:`Curation.get_meta()`.

        :note: For example, to set the title of a curation you would use :code:`curation.set_meta(title='Title Goes Here')`
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

        :since 1.5: You can also just get the metadata directly through the curation instead; e.g., :code:`myVar = curation.title`

        :param str key: The name of an argument to get the value of. You can either use the keys referenced by :attr:`Curation.ARGS` or the name of the argument you passed in through :func:`Curation.set_meta()`.

        :returns: The meta referenced by :code:`key`, the data associated with it, or None if it hasn't been set.
        """
        try:
            if key in Curation.ARGS:
                return self.meta[Curation.ARGS[key]]
            else:
                return self.args[key]
        except KeyError:
            return None

    def add_app(self, heading, launch, path=FLASH):
        """Add an additional application. To add extras or a message, use :func:`Curation.add_ext()` and :func:`Curation.add_msg()` respectively.

        :param str heading: The name of the additional application.
        :param str launch: The name of the launch command for the additional application.
        :param str path: The application path for the additional application. Defaults to :data:`FLASH`.

        :seealso: The `Additional Applications <https://flashpointarchive.org/datahub/Curation_Format#Appendix_II:_Additional_Applications>`_ section of the Curation Format page.

        :note: Trying to add an additional app with a heading that already exists will result in replacing it.

        :raises ValueError: If :code:`heading` is in :attr:`Curation.RESERVED_APPS`.
        """
        debug('Adding app "{}" to curation {}', 2, heading, str(self), pre='[FUNC] ')
        if heading.lower() in Curation.RESERVED_APPS:
            raise ValueError('You cannot create an additional app with the name"' + heading + '"')
        self.meta['Additional Applications'][heading] = {
            'Application Path': path,
            'Launch Command': launch
        }

    def add_ext(self, folder):
        """Add extras from folder.

        :param str folder: The name of the folder the extras are located in.

        :seealso: The `Extras <https://flashpointarchive.org/datahub/Curation_Format#Extras>`_ section of the Curation Format page.

        :note: Calling this method more than once will replace the current extras."""
        debug('Adding extras folder "{}" to curation {}', 2, folder, str(self), pre='[FUNC] ')
        self.meta['Additional Applications']['Extras'] = folder

    def add_msg(self, message):
        """Add message.

        :param str message: The message to add to this curation.

        :seealso: The `Messages <https://flashpointarchive.org/datahub/Curation_Format#Messages>`_ section of the Curation Format page.

        :note: Calling this method more than once will replace the current message.
        """
        debug('Adding message to curation {}', 2, str(self), pre='[FUNC] ')
        self.meta['Additional Applications']['Message'] = message

    def del_app(self, heading):
        """Delete an additional application, extras, or message.

        :param str heading: The name of the additional application to delete. Use "Extras" or "Message" to delete an extras or message.

        :raises KeyError: If the app doesn't exist.
        """
        debug('Deleting app "{}" from curation {}', 2, heading, str(self), pre='[FUNC] ')
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
        """Download/Create all necessary content files for this curation. By default this method downloads the file linked by all launch commands and creates all the directories necessary for them to be in. It will not raise any errors if downloading fails.

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

    def save(self, use_title=False, overwrite=False, parse=False, validate=0, save_items=EVERYTHING):
        """Save the curation to a folder with the name of :attr:`Curation.id`. Consecutive calls to this method will not overwrite the previous folder, but will instead save it as "Curation (2)", "Curation (3)", etc.

        :param str use_title: If True, the folder will be generated with the title of the curation instead of its id.
        :param bool overwrite: If True, this method will mix and overwrite files in existing curation folders instead of making the folder "Curation (2)", "Curation (3)", etc.
        :param bool parse: *Added in 1.3*: If True, this function will call :func:`Curation.parse()` before saving metadata.
        :param int validate: *Added in 1.3*: Mode to validate this curation's metadata with. 0 (default) means do not validate, 1 means flexibly validate, and 2 means rigidly validate.
        :param int save_items: Flags determining what items to save as part of this curation. By default this is :data:`EVERYTHING`. If you wanted to save only the meta and logo, for example, use :code:`save_items=META|LOGO`.

        :raises InvalidMetadataError: *Added in 1.3*: If this curation has invalid metadata and :code:`validate` is set to 1 or higher.

        :see: :data:`EVERYTHING` and the surrounding constants, along with :func:`get_errors()`

        The process of this method is as follows:

        #. Create a BeautifulSoup object with :func:`Curation.soupify()`.
        #. Call method :func:`Curation.parse()` with the soup object just created.
        #. *New in 1.3*: Validate this curation's metadata with :func:`Curation.get_errors()` if :code:`validate` is 1 or higher. Raise an error if it's incorrect.
        #. Create curation folder for the curation and set it to the working directory (the working directory will be reset in the case of any error).
        #. Create meta file with :func:`Curation.get_yaml()` and download logo and screenshot through :func:`Curation.save_image()` if they are available.
        #. Create "content" folder and set it to the working directory.
        #. Call method :func:`Curation.get_files()` to get all files necessary for the curation.
        #. Reset working directory.

        You may overwrite any of these methods to allow for custom usability.
        """
        debug('Saving curation {}', 2, str(self), pre='[FUNC] ')
        global TABULATION
        TABULATION += 1
        cwd = os.getcwd()
        try:
            if parse:
                debug('Parsing source for metadata', 2)
                TABULATION += 1
                try:
                    self.parse(self.soupify())
                finally:
                    TABULATION -= 1

            c_errs = []
            if validate > 0:
                c_errs = self.get_errors(not(validate & 1))
            if c_errs:
                raise InvalidMetadataError('invalid metadata:\n  ' + '\n  '.join(c_errs))

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

            make_dir(folder, True, True)

            if save_items & META:
                write('meta.yaml', self.get_yaml(), True)

            if save_items & LOGO:
                debug('Downloading logo', 2)
                TABULATION += 1
                try:
                    if self.logo is not None:
                        self.save_image(self.logo, 'logo.png')
                finally:
                    TABULATION -= 1

            if save_items & SS:
                debug('Downloading screenshot', 2)
                TABULATION += 1
                try:
                    if self.ss is not None:
                        self.save_image(self.ss, 'ss.png')
                finally:
                    TABULATION -= 1

            if save_items & CONTENT:
                make_dir('content', True)
                TABULATION += 1
                try:
                    self.get_files()
                finally:
                    TABULATION -= 1

        finally:
            TABULATION -= 1
            os.chdir(cwd)

    def get_errors(self, rigid=False):
        """Validate this curation to see if it's metadata is correct.

        :param bool rigid: If True, this function will make sure this Curation's metadata is in order with the `Curation Format`_ page. By default, this function checks everything except Tags, Platform, and Application Path. Note that rigid checking will call :func:`update()` if it has not been called already or failed previously.

        :seealso: :func:`Curation.check_source()`

        :returns: A list of problems with this curation as strings. If there are no errors with this curation, an empty list will be returned.

        :since 1.3:
        """
        debug('Validating curation {}', 2, str(self), pre='[FUNC] ')
        errors = []
        global TABULATION
        TABULATION += 1
        try:
            # Get updated platforms and tags if necessary
            if rigid and (not TAGS or not PLATFORMS):
                update()

            # Check Title
            if not self.meta['Title']:
                errors.append(('Title: missing'))
            # Check Library
            if self.meta['Library'] not in LIBRARIES:
                errors.append('Library: invalid value "' + self.meta['Library'] + '", must be "arcade" or "theatre"')
            # Check Tags
            if rigid:
                tags = self.meta['Tags']
                if isinstance(tags, str):
                    tags = tags.split('; ')
                elif not isinstance(tags, list):
                    tags = [str(tags)]

                vtags = TAGS.copy()
                wtags = []
                for tag in tags:
                    if tag in vtags:
                        vtags.remove(tag)
                    else:
                        wtags.append(tag)

                if wtags:
                    errors.append('Tags: unknown/duplicate value(s) "' + '", "'.join(wtags) + '"')
            # Check Play Mode
            modes = self.meta['Play Mode']
            if isinstance(modes, str):
                modes = modes.split('; ')
            elif not isinstance(modes, list):
                modes = [str(modes)]

            vmodes = PLAY_MODES.copy()
            wmodes = []
            for mode in modes:
                if mode in vmodes:
                    vmodes.remove(mode)
                else:
                    wmodes.append(mode)

            if wmodes:
                errors.append('Play Mode: invalid/duplicate value(s) "' + '", "'.join(wmodes) + '"')
            # Check Status
            status = self.meta['Status']
            if isinstance(status, list):
                status = '; '.join(status)
            elif not isinstance(status, str):
                status = str(status)

            if status not in STATUSES:
                errors.append('Status: invalid value(s)')
            # Check Release Date
            date = self.meta['Release Date']
            if not(date is None or date == '' or DATE.fullmatch(date)):
                errors.append('Release Date: formatted incorrectly. Use YYYY-MM-DD, where -MM and -DD are optional.')
            # Check Languages
            langs = self.meta['Languages']
            if isinstance(langs, str):
                langs = langs.split('; ')
            elif not isinstance(langs, list):
                langs = [str(langs)]

            vlangs = LANGUAGES.copy()
            wlangs = []
            for lang in langs:
                if lang in vlangs:
                    vlangs.remove(lang)
                else:
                    wlangs.append(lang)

            if wlangs:
                errors.append('Languages: unknown/duplicate value(s) "' + '", "'.join(wlangs) + '"')
            # Check Extreme
            if self.meta['Extreme'] not in ['Yes', 'No', True, False]:
                errors.append('Extreme: invalid value, must be "Yes", "No", True, or False')
            # Check Source
            src_prob = self.check_source()
            if src_prob:
                errors.append('Source: ' + src_prob)
            # Group check
            if rigid:
                # Check Platform
                if self.meta['Platform'] not in PLATFORMS:
                    errors.append('Platform: unknown value "' + self.meta['Platform'] + '"')
                # Check Application Path
                if self.meta['Application Path'] not in APPLICATIONS:
                    errors.append('Application Path: unknown value')
            # Check Launch Command
            cmd = self.meta['Launch Command']
            if not cmd:
                errors.append('Launch Command: missing')
            elif (cmd[0] != '"') and (" " not in cmd) and normalize(cmd, False, True) != cmd:
                errors.append('Launch Command: formatted incorrectly. Use HTTP and don\'t use web.archive.org')
            # Check Additional Applications
            problems = []
            for heading in self.meta['Additional Applications']:
                if heading.lower() not in Curation.RESERVED_APPS:
                    try:
                        app = self.meta['Additional Applications'][heading]
                        if rigid and app['Application Path'] not in APPLICATIONS:
                            problems.append(heading)
                        elif not app['Launch Command']:
                            problems.append(heading)
                        elif normalize(app['Launch Command'], False, True) != app['Launch Command']:
                            problems.append(heading)
                    except:
                        problems.append(heading)
            if problems:
                errors.append('Additional Applications: improper apps "' + '", "'.join(problems) + '"')
            debug('Validation found {} problems', 2, len(errors))
        finally:
            TABULATION -= 1
        return errors

    def check_source(self):
        """Validates this curation's current source. Called by :func:`Curation.get_errors()`.

        :returns: A string of the source's current problem or None if there is no problem.

        :since 1.3:
        """
        source = self.meta['Source']
        if not source:
            return 'missing'
        elif normalize(source, False, True, True) != source:
            return 'formatted incorrectly. You should use full, proper urls'

        return None

class TestCuration(Curation):
    """An extension of :class:`Curation` that curates interactive buddy."""
    def parse(self, soup):
        self.set_meta(
            url='https://www.newgrounds.com/portal/view/218014',
            title='Interactive Buddy',
            tags=['Simulation', 'Toy'],
            dev='Shock Value',
            pub='Newgrounds',
            ver='1.01',
            date='2005-02-08',
            cmd='http://uploads.ungrounded.net/218000/218014_DAbuddy_latest.swf',
            desc='Use various weapons to beat up on the buddy, in order to get money to buy more weapons!\n\nUpdates will come if you guys want them. Just leave reviews with suggestions for items, skins, etc.\n\nNote that the graphics (such as the background) were left simple so that the framerate would be as high as possible. Around 36 fps is optimal, but some browsers have trouble displaying Flash movies at that rate (such as Firefox, which I use, unfortunately).'
        )
        self.logo = 'https://picon.ngfiles.com/218000/flash_218014_medium.gif'
        self.ss = 'http://web.archive.org/web/20200502013055im_/https://www.softpaz.com/screenshots/interactive-buddy-mofunzone/3.png'
        self.add_app('wrongo', 'ah')
        self.del_app('wrongo')
        self.add_app('Kongregate v1.02', 'http://chat.kongregate.com/gamez/0003/0303/live/ib2.swf?kongregate_game_version=1363985380')

class BrokenCuration(Curation):
    """An extension of :class:`Curation` that has literally everything wrong with it when parsed.

    :since 1.3:
    """
    def parse(self, soup):
        debug('Breaking curation {}', 2, str(self), pre='[FUNC] ')
        global TABULATION
        TABULATION += 1
        try:
            self.set_meta(
                title='',
                library='potato',
                mode='Single Player; Single Player',
                status='Nope, Playable',
                date='201-1-1',
                languages='potato,a; ja; aj; asdf; en; en; es',
                extreme='Potato',
                tags=['Simulation', 'Toys', 'asdfjeiq, mopadmsk'],
                source='potato',
                platform='F',
                app='potato.exe',
                cmd='https://uploads.ungrounded.net/218000/218014_DAbuddy_latest.swf'
            )
            self.add_app('wrongo', 'ah')
            self.add_app('Kongregate v1.02', 'https://chat.kongregate.com/gamez/0003/0303/live/ib2.swf?kongregate_game_version=1363985380')
        finally:
            TABULATION -= 1

    def get_errors(self, rigid=True):
        errs = super().get_errors(rigid)
        global TABULATION
        TABULATION += 1
        try:
            debug('13 problems is normal', 2)
        finally:
            TABULATION -= 1
        return errs

class DateParser:
    """Initialize a regex-powered date parser that gets initialized with a specific format and can parse any date into the proper iso format. It does not check that the date is a real date. The constructor takes a string :code:`format` specifying a regex to search for in future parsed strings. Note that the regex is case insensitive. Use these macros in the format string to specify parts of the date:

    "<y>" for year number to match - replaced with the capture group "(?P<year>\\d{4})",
    "<m>" for month to match - replaced with the capture group "(?P<month>\\d{1,3}|[A-Za-z]+)", and
    "<d>" for day to match - replaced with the capture group "(?P<day>\\d{1,3})"

    Month and day are optional, though using day requires using month. Note that the year, month, and day are automatically padded to the right number of zeros (4, 2, 2) automatically.

    If the macros don't quite work for you, feel free to use named capture groups and the callbacks "year", "month", and "day", which are called on the respective matched parts of a parsed string to turn it into the right number format to use in the returned string. If the "month" callback is not set, it defaults to :func:`DateParser.get_month`.

    :param str format: A string containing a regex and macros specifying how to parse strings.
    :param func year: A function to turn the matched "year" part of a parsed date into the right number format.
    :param func month: A function to turn the matched "month" part of a parsed date into the right number format.
    :param func day: A function to turn the matched "day" part of a parsed date into the right number format.

    :raises ValueError: if the given format does not contain a "year" named group/macro or contains a "day" named group/macro without the "month" named group/macro.

    :since 1.6:
    """

    def __init__(self, format, year=None, month=None, day=None):
        text = format.\
            replace("<y>", r"(?P<year>\d{4})").\
            replace("<m>", r"(?P<month>\d{1,3}|[A-Za-z]+)").\
            replace("<d>", r"(?P<day>\d{1,3})")

        if "(?P<year>" not in text or ("(?P<month>" not in text and "(?P<day>" in text):
            raise ValueError("The given format is invalid")

        self.format = re.compile(text, re.I)
        self.year = year
        self.month = month or DateParser.get_month
        self.day = day

    def get_month(s):
        """The default method called to turn the matched "month" part of a parsed date into the right number format. It tries to to find the first three characters of the string put into uppercase in :data:`fpclib.MONTHS`, then just returns :code:`s` if it fails."""
        if len(s) < 3: return s
        try:
            return MONTHS[s[:3].upper()]
        except KeyError:
            return s

    def parse(self, s):
        """Uses this date format object to parse the given string :code:`s` into a proper iso date.

        :param str s: A string to parse for a date.

        :returns: An iso date parsed from string :code:`s`

        :raises ValueError: if no date in :code:`s` could be found.
        """
        match = self.format.search(s)
        if not match: raise ValueError(f'No date in "{s}"')

        y = match["year"]
        if not y: raise ValueError(f'No year in "{s}"')
        try: m = match["month"]
        except IndexError: m = None
        try: d = match["day"]
        except IndexError: d = None

        if d and not m: raise ValueError(f'Day but no month in "{s}"')

        if self.year:
            year = self.year(y).zfill(4)
        else:
            year = y.zfill(4)

        if m:
            if self.month:
                month = "-" + self.month(m).zfill(2)
            else:
                month = "-" + m.zfill(2)
        else:
            month = ""

        if d:
            if self.day:
                day = "-" + self.day(d).zfill(2)
            else:
                day = "-" + d.zfill(2)
        else:
            day = ""

        return year + month + day

DP_US = DateParser(r"<m>(\s*.??<d>\w*)?,?\s*.??<y>")
"""A :class:`DateParser` that parses dates in the american format of "March 5th, 2016", "3/5/2016", "March 2016" or similar."""
DP_UK = DateParser(r"(<d>\w*(\s*of)?\s*.??)?<m>,?\s*.??<y>")
"""A :class:`DateParser` that parses dates in the european format of "5th of March, 2016", "5/3/2016", "March 2016" or similar."""
DP_ISO = DateParser(r"<y>(\s*.??<m>)?(\s*.??<d>\w*)?")
"""A :class:`DateParser` that parses dates in the format of "2016 March 5th" or similar."""


if __name__ == '__main__':
    test()
