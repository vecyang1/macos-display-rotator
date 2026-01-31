from setuptools import setup

APP = ['screen_rotator.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'ScreenRotator',
        'CFBundleDisplayName': 'ScreenRotator',
        'CFBundleIdentifier': 'com.screenrotator.app',
        'CFBundleVersion': '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['rumps', 'pynput'],
    'excludes': ['tkinter', 'unittest'],
}

setup(
    name='ScreenRotator',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
