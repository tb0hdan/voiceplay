voiceplay - Client-side first music centered voice controlled player
======

[![Build Status](https://api.travis-ci.org/tb0hdan/voiceplay.svg?branch=master)](https://travis-ci.org/tb0hdan/voiceplay)
[![PyPI version](https://img.shields.io/pypi/v/voiceplay.svg)](https://pypi.python.org/pypi/voiceplay)
[![PyPI Python versions](https://img.shields.io/pypi/pyversions/voiceplay.svg)](https://pypi.python.org/pypi/voiceplay)
[![PyPI license](https://img.shields.io/pypi/l/voiceplay.svg)](https://pypi.python.org/pypi/voiceplay)
[![Code Climate](https://codeclimate.com/github/tb0hdan/voiceplay/badges/gpa.svg)](https://codeclimate.com/github/tb0hdan/voiceplay)
[![Test Coverage](https://codeclimate.com/github/tb0hdan/voiceplay/badges/coverage.svg)](https://codeclimate.com/github/tb0hdan/voiceplay/coverage)
[![Issue Count](https://codeclimate.com/github/tb0hdan/voiceplay/badges/issue_count.svg)](https://codeclimate.com/github/tb0hdan/voiceplay)


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
versions 2.7, 3.3, 3.4, 3.5, 3.6 and is not platform specific. It should work on
your Linux or on Mac OS X. It is released to the public domain, which means you can modify it,
redistribute it or use it however you like.

## Privacy notice
**voiceplay** submits its crashlogs to URL specified in `voiceplay/config/config.py` or configuration file
using `bugtracker_url` parameter. While there's nothing that can compromise your system, be sure to read
source code located at `voiceplay/utils/crashlog.py`. By using this software you're giving your consent
to transmit crash logs for further analysis and software bugfixes.



## Installation

### Vagrant universal (major platforms, recommended)

1. Download and install [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
2. Download and install [Vagrant](https://www.vagrantup.com/downloads.html)
3. Initialize vagrant image: `vagrant init tb0hdan/voiceplay`
4. Start vagrant VM: `vagrant up`
5. Use voiceplay `vagrant ssh` then `voiceplay -w`


## Configuration
Please follow the instructions of the following command:
```
voiceplay --configure
```

## Usage

Start application:

```
voiceplay -w
```

Then say 'Vicki', application should reply 'Yes', proceed with command from the list below.

## Console mode

Note: Add `-v` for increased verbosity level.

Note: Add `-s` to set Skype status on track change (doesn't work from Vagrant)

```
./voiceplay.sh -c
```

then type any command from the list below.

![console_play](https://raw.githubusercontent.com/tb0hdan/voiceplay/master/images/console_play.png)

to quit, either type 'quit' or press CTRL+D


## Command list

### Playback control

`pause`

`next`

`stop`


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

### Shuffle recent/new tracks

```
play new tracks by Robin Schulz
```

### Shuffle local library (~/Music, .mp3 only)

```
play my library
```

### Shuffle track history (songs that were already played)

```
play my history
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

### URL playback

#### Direct

```
play url http://66.207.196.218:8130/
```

#### Media (including youtube playlists)

```
play url https://www.youtube.com/watch?v=VrGScAzGtXs
```

P.S. Full list of supported media sources can be found at [youtube_dl extractors page](https://github.com/rg3/youtube-dl/tree/master/youtube_dl/extractor)


### DI.FM
User agent / Referer hack from https://github.com/Bitcrusher/Digitally-Imported-XBMC-plugin


```
play vocal trance station from di
```

## Advanced users & developers

### MAC

WARNING: Some systems require System Integrity Check (SIC!) disabled prior to installing system-wide python modules.
If this is the case either use `csrutil` to disable or `virtualenv/virtualenvwrapper` (recommended) to install packages locally.

Please make sure you have following dependencies resolved prior to proceeding with other steps:

1. Xcode (https://itunes.apple.com/us/app/xcode/id497799835)
2. Growl (http://growl.info/) installed and running
3. VLC (http://videolan.org) installed and up to date


then continue to:

```
brew install ffmpeg portaudio cmu-pocketsphinx swig libmagic
sudo easy_install-2.7 pip
sudo pip install pyobjc
```

### Linux (Debian/Ubuntu) (advanced users & developers)

```
sudo apt-get install python-all-dev python-setuptools
sudo apt-get install libav-tools festival festival-dev portaudio19-dev vlc
sudo apt-get install pocketsphinx swig libmagic1 libpulse-dev libreadline-dev
sudo apt-get install libblas-dev liblapack-dev libatlas-dev libatlas-base-dev
sudo apt-get install python-gobject libnotify-bin libnotify-dev
sudo easy_install pip
sudo pip install pyfestival
```

### Application and dependencies

```
git clone https://github.com/tb0hdan/voiceplay
cd voiceplay
sudo pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
./voiceplay.sh requirements
make deps
```


## Console mode (development)

```
./voiceplay.sh -cd
```

# Similar projects

## Console players

https://github.com/jkramer/shell-fm

https://github.com/dbrgn/orochi


## Voice controlled applications

https://github.com/alexa-pi/AlexaPi

https://github.com/edouardpoitras/eva

https://github.com/rcbyron/hey-athena-client

https://github.com/jasperproject/jasper-client

https://github.com/MycroftAI/mycroft-core

https://github.com/tajddin/voiceplay

## Home automation

https://github.com/home-assistant/home-assistant


# COPYRIGHT

voiceplay is released into the public domain by its authors.

This README file was originally written by [Bohdan Turkynewych](https://github.com/tb0hdan) and is likewise released into the public domain.
