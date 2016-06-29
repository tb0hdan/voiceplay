voiceplay (proof of concept) - Voice controlled console playback (OSX only so far)

- [INSTALLATION](#installation)
- [CONFIGURATION](#configuration)
- [USAGE](#usage)
- [CONSOLE MODE](#console mode (advanced))
- [COPYRIGHT](#copyright)


## Installation

### System dependencies

Please make sure you have XCode installed prior to proceeding with other steps.

```
brew install ffmpeg mplayer portaudio
```

### Application and dependencies

```
git clone https://github.com/tb0hdan/voiceplay
cd voiceplay
sudo pip install -r requirements.txt
```

## Configuration

Sample is provided for convenience.

```
cp config.yaml.sample config.yaml
```


Register at [http://www.last.fm/api](http://www.last.fm/api) and then
paste Last.fm API key and secret into config.yaml

Register at [https://developer.dailymotion.com](https://developer.dailymotion.com) and then
paste DailyMotion key, secret, username, password into config.yaml

Register at [https://developer.vimeo.com](https://developer.vimeo.com) and then
paste client id(key), token and secret into config.yaml

Register at [https://console.developers.google.com](https://console.developers.google.com) and then
paste Google API key (for Server) into config.yaml and enable Youtube data api.


## Usage

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

### Shuffle top tracks (global or country)

```
Vicki play top tracks in united states
```

or just

```
Vicki play top tracks
```

### Shuffle genre (station)

```
Vicki play edm station
```

or

```
Vicki play melodic death metal station
```

## Console mode (advanced)

```
./voiceplay -c
```

then run (or any other command from list above)

```
vicki.play_from_parser('Vicki play some music by atb')
```




# COPYRIGHT

voiceplay is released into the public domain by the copyright holders.

This README file was originally written by [Bohdan Turkynewych](https://github.com/tb0hdan) and is likewise released into the public domain.
