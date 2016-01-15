copy __init__.py GFileTrade.py # Copy for temp 
python py2exe-setup.py py2exe -i dbhash

# Rmdir -> \s for recursive, \q for quiet
RMDIR /S /Q build
RMDIR /S /Q "GFileTrade/GFileTrade Resources"

# move dist "GFileTrade/GFileTrade Resources" # Not sure I want this anymore
move dist windowsExeBuild


del GFileTrade.py # Delete temp