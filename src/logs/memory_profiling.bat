@echo off
exit
echo Begin of profiling
del .\memory-profile.log /f /q
mprof run --include-children -o logs/memory-profile.log --interval 0.05 python ../main.py
mprof plot --output ./memory-profile.png ./memory-profile.log
echo End of profiling
pause