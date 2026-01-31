"""
Setup script for py2app
Run: python3 setup.py py2app
"""

from setuptools import setup

APP = ['screen_rotator.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,  # Can add custom .icns file here
    'plist': {
        'CFBundleName': 'Screen Rotator',
        'CFBundleDisplayName': 'Screen Rotator',
        'CFBundleIdentifier': 'com.screenrotator.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,  # Hide from dock (menu bar app)
        'NSHighResolutionCapable': True,
    },
    'packages': ['rumps', 'pynput'],
}

setup(
    app=APP,
    name='Screen Rotator',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
