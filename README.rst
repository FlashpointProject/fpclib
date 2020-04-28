General Overview
================
"fpclib" stands for "Flashpoint Curation Library" and is a powerful collection of functions and classes you can use and extend to hopefully curate any game in existence through python3. If you're not familiar with curating games for Flashpoint, first follow the `Curation Tutorial <https://bluemaxima.org/flashpoint/datahub/Curation_Tutorial>`_ page on the Flashpoint wiki. If you're not familiar with using python or coding, you should read the `official python tutorial <https://docs.python.org/3/tutorial/index.html>`_.

Although there are already several useful tools you can use for manually curating games for Flashpoint and downloading assets easily, such as Flashpoint Core, cURLsDownloader, and MAD4FP, none of these tools offer the ability to curate games through code or automate the process; fpclib was created to fix that. Of course, you should still always manually check any curation in Flashpoint Core to make sure it works properly.

There are numerous benefits of using fpclib to help you curate your games:

* By default, fpclib downloads main game files and puts them in the right file format based upon your launch commands.
* Logos and screenshots can be automatically downloaded from online and converted to PNG files.
* Curating similar games from a single or multiple sites is simple and easy thanks to the :code:`fpclib.curate()` function.
* **Nearly every kind of Curation is customizable!** This library and documentation were created with the intent of making it easy to overwrite the Curation class to make it do different things.

Here's some example code of using the library to curate "Interactive Buddy" from Newgrounds::

    from fpclib import Curation

    curation = Curation(url='https://www.newgrounds.com/portal/view/218014')
    curation.logo = 'https://picon.ngfiles.com/218000/flash_218014_medium.gif'
    curation.set_meta(title='Interactive Buddy', tags=['Simulation', 'Toy'])
    curation.set_meta(dev='Shock Value', pub='Newgrounds')
    curation.set_meta(ver='1.01', date='2005-02-08')
    curation.set_meta(cmd='http://uploads.ungrounded.net/218000/218014_DAbuddy_latest.swf')
    curation.add_app('Kongregate v1.02', 'http://chat.kongregate.com/gamez/0003/0303/live/ib2.swf?kongregate_game_version=1363985380')

    curation.save()

You can also test the library by running the script directly or with :code:`fpclib.test()`, which will also curate "Interactive Buddy" and download the swf file linked in the launch command into the proper place in a folder in the current working directory.

More Reading
============

You can read more about this library in the `official documentation <https://raw.githack.com/xMGZx/fpclib/master/doc/build/html/index.html>`_.

Usage
=====

You can install the library with
::

    pip install fpclib

or you can put the "fpclib.py" script (check the releases page) in the same directory as your script.

If you choose the second option, you'll need to install these libraries through pip::

    pip install requests
    pip install beautifulsoup4
    pip install pillow
    pip install ruamel.yaml

Once you have all of that set up, you can put :code:`import fpclib` at the top of your script to use it's methods.

Licence
=======

.. raw:: html
   
   <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br/>This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
