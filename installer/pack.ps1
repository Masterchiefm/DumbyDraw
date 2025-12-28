conda activate py39
conda env list
Remove-Item DumbDrawPhD_env.tar.gz -Recurse -Force
conda pack -n py39 -o DumbDrawPhD_env.tar.gz --ignore-missing-files
Remove-Item  DumbDrawPhD_Setup.exe -Recurse -Force
& "C:\Program Files (x86)\NSIS\makensis.exe" install.nsi

