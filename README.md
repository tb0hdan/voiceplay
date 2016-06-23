voiceplay (proof of concept) - Voice controlled console playback (OSX only so far)

- [INSTALLATION](#installation)
- [COPYRIGHT](#copyright)

## Installation

### System dependencies

```
brew install ffmpeg mplayer portaudio
```

### Application and dependencies

```
git clone https://github.com/tb0hdan/voiceplay
cd voiceplay
pip install -r requirements.txt
```

## Configuration

Sample is provided for convenience.

```
cp config.yaml.sample config.yaml
```

Paste Google API key into config.yaml and enable Youtube data api.

Paste Last.fm API key and secret into config.yaml


## Run

```
python ./voiceplay.py
```

Available modes

### Single track

```
Vicki play beat it by Michael Jackson
```

### Single track from top tracks (1-10)

```
Vicki play top tracks by Michael Jackson
```

Then select track number (1-10)

```
Vicki play one
```

### Shuffle top tracks

```
Vicki play some music by Michael Jackson
```

### Shuffle local library (~/Music, .mp3 only)

```
Vicki play my library
```




# COPYRIGHT

voiceplay is released into the public domain by the copyright holders.

This README file was originally written by [Bohdan Turkynewych](https://github.com/tb0hdan) and is likewise released into the public domain.
