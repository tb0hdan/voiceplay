.PHONY: snowboy vlcpython

submodules:
	@git submodule init
	@git submodule update

snowboy:	submodules
	@cd snowboy/swig/Python; make
	@cp -v snowboy/swig/Python/*.so extlib/snowboydetect/
	@cp -v snowboy/swig/Python/*.py extlib/snowboydetect/
	@cp -v snowboy/examples/Python/*.py extlib/snowboydetect/
	@cp -R snowboy/resources extlib/snowboydetect

vlcpython:	submodules
	@cp -v vlcpython/generated/vlc.py extlib/vlcpython

deps:	snowboy vlcpython
	@sudo pip install -r requirements.txt

py2app:	deps
	@python setup.py py2app

dmg:	py2app
	@hdiutil create -srcfolder dist/voiceplay.app ./voiceplay.dmg

clean:
	@rm -rf build/ dist/
	@rm -f ./*.dmg
