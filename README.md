## General Overview
"fpclib" stands for "Flashpoint Curation Library" and is a powerful collection of functions and classes you can use and extend to hopefully curate any game/animation in existence through python3. If you're not familiar with curating for Flashpoint and would like to know how to curate, first follow the [Curation Tutorial](https://flashpointarchive.org/datahub/Curation_Tutorial) page on the Flashpoint wiki. If you're not familiar with using python or coding, you should read the [official python tutorial](https://docs.python.org/3/tutorial/index.html) before using this library.

Although there are already several useful tools you can use for manually curating games/animations for Flashpoint and downloading assets easily, such as Flashpoint Core, cURLsDownloader, and MAD4FP, none of these tools offer the ability to curate through code or automate the process; fpclib was created to fix that. [fpcurator](https://github.com/FlashpointProject/fpcurator) uses fpclib to automatically generate curations. Of course, you should still always manually check any curation you make with fpclib in Flashpoint Core to make sure it works properly.

There are numerous benefits of using fpclib/fpcurator to help you curate:

* By default, fpclib downloads main game/animation files and puts them in the right file format based upon your launch commands.
* Logos and screenshots can be automatically downloaded from online and converted to PNG files.
* Curating similar games/animations from one or more websites is simple and easy thanks to the `fpclib.curate()` function.
* **Nearly every kind of Curation is possible to make with this library!** This library and documentation were created with the intent of making it easy to overwrite the Curation class to make it do different things. Anything you can do in the "Curate" tab in Flashpoint Core you can do with fpclib, except test games.

Here's some example code of using the library to curate "Interactive Buddy" from Newgrounds:
```python
# Import fpclib curation
from fpclib import Curation

# Create a curation from a given url
curation = Curation(url='https://www.newgrounds.com/portal/view/218014')
# Set the logo of the curation
curation.logo = 'https://picon.ngfiles.com/218000/flash_218014_medium.gif'

# You can set metadata through the object directly or through the set_meta method
curation.set_meta(title='Interactive Buddy', tags=['Simulation', 'Toy'])
curation.set_meta(dev='Shock Value', pub='Wrong Publisher')
curation.pub = 'Newgrounds'
curation.ver = '1.01'
curation.date = '2005-02-08'

# Add an additional app
curation.set_meta(cmd='http://uploads.ungrounded.net/218000/218014_DAbuddy_latest.swf')
curation.add_app('Kongregate v1.02', 'http://chat.kongregate.com/gamez/0003/0303/live/ib2.swf?kongregate_game_version=1363985380')

# Export this curation to the current working directory
curation.save()
```

You can also test the library by running the script directly or with `fpclib.test()`, which will also curate "Interactive Buddy" in the current working directory, delete the curation, and check an invalid curation.

## More Reading

You can read more about this library in the [official documentation](https://www.mathgeniuszach.com/bin/fpclib/).

## Usage

fpclib is available on pypi or pip; however, it requires a specific version of ruamel.yaml in order to run.

It is recommended that you install fpclib with poetry (`poetry add fpclib`) or something like pipx (`pipx install fpclib`) to run it properly.

## License

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br/>This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
