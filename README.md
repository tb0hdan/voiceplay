voiceplay - Client-side first music centered voice controlled player (OSX/Linux)

- [DESCRIPTION](#description)
- [INSTALLATION](#installation)
- [CONFIGURATION](#configuration)
- [USAGE](#usage)
- [CONSOLE MODE](#console-mode)
- [COPYRIGHT](#copyright)

## Description
**voiceplay** is a command-line program that listens to voice in background and gets
activated by a wake word - **Vicki** (processing is done offline using [Kitt.ai snowboy](https://snowboy.kitt.ai/) and only
after that records audio later transcribed by Google Voice Recognition (code can be modified to
use any of engines supported by [SpeechRecognition](https://github.com/Uberi/speech_recognition) library). It requires the Python interpreter,
version 2.7, 3.5 (so far) and is not platform specific. It should work on
your Linux or on Mac OS X (Python 2.7 only). It is released to the public domain, which means you can modify it,
redistribute it or use it however you like.



## Installation

### MAC

Please make sure you have following dependencies resolved prior to proceeding with other steps:

1. Xcode (https://itunes.apple.com/ua/app/xcode/id497799835?l=en&mt=12)
2. Growl (http://growl.info/)
3. VLC (http://videolan.org)


then continue to:

```
brew install ffmpeg portaudio cmu-pocketsphinx swig libmagic
sudo pip install pyobjc
```

### Linux (Debian/Ubuntu)

```
sudo apt-get install python-all-dev python-setuptools
sudo apt-get install libav-tools festival festival-dev portaudio19-dev vlc
sudo apt-get install pocketsphinx swig libmagic1 libpulse-dev libreadline-dev
sudo apt-get install libblas-dev liblapack-dev libatlas-dev libatlas-base-dev python-gobject
sudo easy_install pip
sudo pip install pyfestival
```

### Application and dependencies

```
git clone https://github.com/tb0hdan/voiceplay
cd voiceplay
./voiceplay.sh requirements
```

## Configuration

Sample is provided for convenience.

```
cp config.yaml.sample config.yaml
```


Register at [http://www.last.fm/api](http://www.last.fm/api) and then
paste Last.fm API key and secret into config.yaml

Register at [https://developer.vimeo.com](https://developer.vimeo.com) and then
paste client id(key), token and secret into config.yaml

Register at [https://console.developers.google.com](https://console.developers.google.com) and then
paste Google API key (for Server) into config.yaml and enable Youtube data api.


## Usage

Start application:

```
./voiceplay.sh
```

Start wake word listener:

```
./voiceplay.sh wakeword
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

or

```
play some tracks by Michael Jackson
```

or

```
play some songs by Michael Jackson
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

Billboard top 100:

```
play top 100 tracks
```

Rolling Stone top 500:

```
play top 500 tracks
```

Reddit music (/r/Music/):

```
play top reddit tracks
```

### Shuffle specific album

```
play tracks from crimson by sentenced
```

### Shuffle genre (station)

```
play edm station
```

or

```
play melodic death metal station
```

### Online radio

#### TuneIn

```
play dj fm station from tunein
```

### Radionomy

```
play folk metal station from radionomy
```

### IceCast

```
play etn.fm station from icecast
```


## Console mode

Note: Add `-v` for increased verbosity level.

```
./voiceplay.sh -c
```

then run any command from the list above

![console_play](https://raw.githubusercontent.com/tb0hdan/voiceplay/master/images/console_play.png)

to quit, either type 'quit' or press CTRL+D

## Console mode (development)

```
./voiceplay.sh -cd
```

# Similar projects

## Console players

https://github.com/jkramer/shell-fm

https://github.com/dbrgn/orochi


## Voice controlled applications

https://github.com/jasperproject/jasper-client

https://github.com/MycroftAI/mycroft-core

# COPYRIGHT

voiceplay is released into the public domain by its authors.

This README file was originally written by [Bohdan Turkynewych](https://github.com/tb0hdan) and is likewise released into the public domain.
