from setuptools import setup
from voiceplay import __copyright__, __title__, __version__

APP = ['voiceplay.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'images/Microphone.icns',
    'plist': {
        'CFBundleName': __title__,
        'CFBundleDisplayName': __title__,
        'CFBundleGetInfoString': "Voice controlled playback",
        'CFBundleIdentifier': "io.github.tb0hdan.voiceplay",
        'CFBundleVersion': __version__,
        'CFBundleShortVersionString': __version__,
        'NSHumanReadableCopyright': __copyright__,
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['SpeechRecognition'],
)
