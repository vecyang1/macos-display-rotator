from setuptools import setup

APP = ['screen_rotator.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'ScreenRotator',
        'CFBundleDisplayName': 'ScreenRotator',
        'CFBundleIdentifier': 'com.screenrotator.app',
        'CFBundleVersion': '2.4.0',
        'CFBundleShortVersionString': '2.4.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['rumps', 'pynput'],
    'excludes': [
        # Keep excludes minimal to avoid stripping py2app/runtime dependencies.
        'tkinter',
        'test',
        'unittest',
    ],
    'strip': True,  # Strip debug symbols
    'optimize': 2,   # Python bytecode optimization
}

setup(
    name='ScreenRotator',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
