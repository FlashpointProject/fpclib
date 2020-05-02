@echo off
if exist dist del /q dist build __pycache__
if exist doc\build del /q "doc\build"
py metadata.py
echo.
echo ---------- Building Documentation ----------
echo.
start /b /w /d doc make html
echo.
echo ------------- Building Library -------------
echo.
py setup.py sdist bdist_wheel
echo.
echo ------------------- Done -------------------
echo.
pause