from distutils.core import setup
import py2exe

setup(
    options = {
            "py2exe":{
            'bundle_files': 1,
            "dll_excludes": ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe"],
            
        }
    },
    console = [{'script': 'File_Transfer.py'}],
    zipfile = None
)
