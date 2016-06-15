voiceplay (proof of concept) - Voice controlled console playback (OSX only so far)

- [INSTALLATION](#installation)
- [COPYRIGHT](#copyright)

## Installation

### System dependencies

```
brew install ffmpeg mplayer portaudio
```

### Application dependencies

```
pip install -r requirements.txt
```

## Configuration

Sample is provided for convenience.

### Paste google api key into config.yaml and enable youtube data api.

### Paste last.fm key and secret into config.yaml


## Run

```
python ./voiceplay.py
```

Then say:

```
Vicki play Michael Jackson beat it
```

# COPYRIGHT

voiceplay is released into the public domain by the copyright holders.

This README file was originally written by [Bohdan Turkynewych](https://github.com/tb0hdan) and is likewise released into the public domain.
