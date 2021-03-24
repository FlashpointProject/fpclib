@echo off
del /s /q dist build __pycache__
del /s /q "doc\build"
rmdir /s /q dist build __pycache__
rmdir /s /q "doc\build"
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