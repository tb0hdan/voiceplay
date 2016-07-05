voiceplay (proof of concept) - Voice controlled console playback (OSX/Linux)

- [DESCRIPTION](#description)
- [INSTALLATION](#installation)
- [CONFIGURATION](#configuration)
- [USAGE](#usage)
- [CONSOLE MODE](#console-mode-advanced)
- [COPYRIGHT](#copyright)

## Description
**voiceplay** is a command-line program that listens to voice in background and gets
activated by a wake word - **Vicki** (processing is done offline using [CMU PocketSphinx](http://cmusphinx.sourceforge.net/) and only
after that records audio later transcribed by Google Voice Recognition (code can be modified to
use any of engines supported by [SpeechRecognition](https://github.com/Uberi/speech_recognition) library). It requires the Python interpreter,
version 2.7, 3.5 (so far) and is not platform specific. It should work on
your Linux or on Mac OS X (Python 2.7 only). It is released to the public domain, which means you can modify it,
redistribute it or use it however you like.



## Installation

### MAC


Please make sure you have XCode installed prior to proceeding with other steps.

```
brew install ffmpeg mplayer portaudio cmu-pocketsphinx swig
```

### Linux (Debian/Ubuntu)

```
sudo apt-get install libav-tools python-dev festival festival-dev portaudio19-dev mplayer
sudo apt-get install pocketsphinx swig
sudo pip install pyfestival
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

Start application:

```
python ./voiceplay.py
```

Then say 'Vicki', application should reply 'Yes', proceed with command from the list below:


### Single track

```
play beat it by Michael Jackson
```

### Single track from top tracks (1-10)

```
play top tracks by Michael Jackson
```

Then select track number (1-10)

```
play one
```

### Shuffle top tracks

```
play some music by Michael Jackson
```

### Shuffle local library (~/Music, .mp3 only)

```
play my library
```

### Shuffle top tracks (global or country)

```
play top tracks in united states
```

or just

```
play top tracks
```

### Shuffle genre (station)

```
play edm station
```

or

```
play melodic death metal station
```

## Console mode (advanced)

```
./voiceplay -c
```

then run (or any other command from list above)

```
vicki.play_from_parser('play some music by atb')
```




# COPYRIGHT

voiceplay is released into the public domain by the copyright holders.

This README file was originally written by [Bohdan Turkynewych](https://github.com/tb0hdan) and is likewise released into the public domain.
