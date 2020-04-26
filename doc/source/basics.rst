##########
The Basics
##########

This is a basic tutorial on using fpclib to curate games for Flashpoint.

If you've never coded in python before, you should check out the `official python tutorial <https://docs.python.org/3/tutorial/index.html>`_ page first.

This tutorial assumes that you already know the basics of curating for Flashpoint. If you do not know how to curate games for Flashpoint, please follow the `Curation Tutorial <https://bluemaxima.org/flashpoint/datahub/Curation_Tutorial>`_ before using fpclib.

.. contents:: Quick Links
   :local:

Purpose
=======

As stated on the :doc:`Home </index>` page, there are numerous benefits of using fpclib to help you curate your games:

* By default, fpclib downloads main game files and puts them in the right file format based upon your launch commands.
* Logos and screenshots can be automatically downloaded from online and converted to PNG files.
* Curating similar games from a single or multiple sites is simple and easy thanks to the :py:func:`fpclib.curate()` function.
* **Nearly every kind of Curation is customizable!** This library and documentation were created with the intent of making it easy to overwrite the Curation class to make it do different things.

Ultimately, fpclib is not meant to replace other curating tools such as Flashpoint Core; it is meant to be used alongside of them. *Always* make sure any curation you make with fpclib is tested in Flashpoint Core before you submit it.

Usage
=====

You can install this library with pip using::

    pip install fpclib

After you've installed fpclib, you can put :code:`import fpclib` at the top of your script to use it's methods.

Special Functions
=================

To help you with common curating tasks, fpclib comes packaged with several useful functions for your code. Here's a quick list of all of them, you can click on any of them for more detail:

Internet
--------

.. autosummary::
   
   download
   download_all
   download_image
   normalize
   get_soup
   read_url

File IO
-------

.. autosummary::
   
   read
   read_lines
   read_table
   write
   write_line
   write_table
   hash256
   hash

Curating
--------

.. autosummary::
   
   test
   clear_save
   curate
   curate_regex
  

A Single Curation
=================

Before curating entire lists of games with fpclib, it's important to understand how to use the library to curate single games at a time. As shown on the :doc:`Home </index>` page, here's some very basic code you can use to curate a game::

    import fpclib

    curation = fpclib.Curation(url='https://www.newgrounds.com/portal/view/218014')
    curation.logo = 'https://picon.ngfiles.com/218000/flash_218014_medium.gif'
    curation.set_meta(title='Interactive Buddy', tags=['Simulation', 'Toy'])
    curation.set_meta(dev='Shock Value', pub='Newgrounds')
    curation.set_meta(ver='1.01', date='2005-02-08')
    curation.set_meta(cmd='http://uploads.ungrounded.net/218000/218014_DAbuddy_latest.swf')
    curation.add_app('Kongregate v1.02', 'http://chat.kongregate.com/gamez/0003/0303/live/ib2.swf?kongregate_game_version=1363985380')

    curation.save()

Here's what each step in this code does:

#. Import the library with :code:`import fpclib`
#. Create a new :class:`Curation` object. You don't have to set it's url immediately, but it should be set before you call :func:`Curation.save()`.
#. Set the url of the curation's logo. You can also set the screenshot with :attr:`Curation.ss`. Note that this will automatically be converted to a png file when the curation is saved. You do not need to set the logo or screenshot for every curation.
#. Set the curation's metadata using :func:`Curation.set_meta()`. You can put as many arguments into this function as you want. To see what arguments map to which parts of the curation's metadata, see :attr:`Curation.ARGS`. Note that descriptions and notes support multiple line strings (split lines with :code:`\\n`).
#. Add an additional app with :func:`Curation.add_app()`. You can also create extras, a message, or delete additional applications with other functions too (see the functions after :func:`Curation.add_app()`).
#. Finally, Save the curation to a folder with :func:`Curation.save()`. This accepts an argument named :code:`use_title` which if you set to True, will generate the curation folder with the curation's title instead of its id (see :attr:`Curation.id`).

You can find a full listing of every function in the :class:`Curation` class in the :doc:`Classes </classes>` page.

Further Reading
===============

If you fully understand how to curate a single game, you should move on to the :doc:`Advanced Stuff </advanced>` page to figure out how to curate more than one game at a time. If not, you'll probably want to re-read this page again.