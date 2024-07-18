$env:PYTHONHOME="C:\Program Files\QGIS 3.20.3\apps\Python39"
& 'C:\Program Files\QGIS 3.20.3\apps\Python39\Scripts\pip' install --upgrade -r .\bankfull_module_jb\requirements_ems.txt --user
Move-Item -Path .\bankfull_module_jb\ -Destination $env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\ -Force
PAUSE