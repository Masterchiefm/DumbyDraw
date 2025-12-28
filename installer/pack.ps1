conda activate py39
conda env list
rm DumbDrawPhD_env.tar.gz
conda pack -n py39 -o DumbDrawPhD_env.tar.gz --ignore-missing-files
& "C:\Program Files (x86)\NSIS\makensis.exe" install.nsi

