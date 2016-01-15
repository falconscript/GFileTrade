# PYTHON TUTORIAL LINK http://www.tutorialspoint.com/

# NAT PUNCHTHROUGH... NATPMP Python Module. Someday integrate this!
# https://github.com/yimingliu/py-natpmp/tree/master/natpmp


# PYTHON P2APP DOCUMENTATION
# http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html#installation


# Compile
cd "`dirname $0`"
cp __init__.py GFileTrade.py # Needed due to py2app not working on __init__
python py2app-setup.py py2app --iconfile icon.icns
rm -r build
rm GFileTrade.py
mv dist/* .
rmdir dist

echo "[*] Complete! The .app should be in this directory"