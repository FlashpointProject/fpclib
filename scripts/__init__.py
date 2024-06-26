from pathlib import Path
import shutil
import glob
import platform
import os
import re

VERSION = re.compile(r'^(version\s+=\s+"\d+\.\d+\.\d+)(\.\d+)?(")', re.MULTILINE)

PROJECT_DIR = Path(__file__).parent.parent
PROJECT = PROJECT_DIR / "pyproject.toml"

def rm(file):
    pfile = Path(file)
    if pfile.is_dir():
        shutil.rmtree(pfile)
    elif pfile.exists():
        pfile.unlink(True)

def rmpycache():
    for f in glob.glob("**/__pycache__", recursive=True):
        rm(f)

def clean():
    rmpycache()
    rm(PROJECT_DIR / "dist")
    rm(PROJECT_DIR / "doc/build")

def docs():
    rmpycache()
    rm(PROJECT_DIR / "doc/build")

    # Build initial docs
    if platform.system() == "Windows":
        os.system("start /b /w /d doc make html")
    else:
        os.system("make html -C doc")

    # For github, replace "_static" with "static" and "_sources" with "sources"
    HTML = PROJECT_DIR / "doc/build/html"
    os.rename(HTML / "_static", HTML / "static")
    os.rename(HTML / "_sources", HTML / "sources")
    for f in HTML.glob("**/*"):
        if f.suffix not in [".html", ".css", ".js"]: continue

        with open(f, "r") as file:
            r = file.read()
            nr = r.replace("_static", "static").replace("_sources", "sources")
            if len(r) == len(nr): continue

        with open(f, "w") as file:
            file.write(nr)


def resetbuild():
    with open(PROJECT, "r") as file:
        data = VERSION.sub(lambda m: f'{m[1]}{m[3]}', file.read())
    with open(PROJECT, "w") as file:
        file.write(data)

def incbuild():
    with open(PROJECT, "r") as file:
        data = VERSION.sub(lambda m: f'{m[1]}.{int(m[2][1:])+1 if m[2] else 1}{m[3]}', file.read())
    with open(PROJECT, "w") as file:
        file.write(data)

def build():
    incbuild()
    rmpycache()
    rm(PROJECT_DIR / "dist")
    docs()
    os.system("poetry build")

def upload():
    with open(Path(__file__).parent / "auth", "r") as file:
        p = file.read()
    os.system(f'poetry publish -u __token__ -p {p}')