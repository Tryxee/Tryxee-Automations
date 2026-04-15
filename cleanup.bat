echo Cleaning old build folders...
if exist "dist" (
    rmdir /s /q "dist"
    echo  Deleted: dist\
)
if exist "build" (
    rmdir /s /q "build"
    echo  Deleted: build\
)
echo  Done.
echo.