import fpclib
import os

fpclib.replace(fpclib.scan_dir("build"), "_sources", "sources")
fpclib.replace(fpclib.scan_dir("build"), "_static", "static")

os.chdir("build/html")
os.rename("_sources", "sources")
os.rename("_static", "static")