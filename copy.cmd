@echo off

:: Set the source and destination files
set src_file1=map1.json
set src_file2=map-maker.py
set dst_folder=Z:\

:: Copy the files
copy %src_file1% %dst_folder%
copy %src_file2% %dst_folder%

:: Display a success message
echo Files copied successfully to Z:\ drive!