.PHONY: docs snowboy vlcpython

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
	@pip install -U -r requirements.txt

piprot:	deps
	@piprot -o requirements.txt; exit 0

py2app:	deps
	@python setup.py py2app

dmg:	py2app
	@hdiutil create -srcfolder dist/voiceplay.app ./voiceplay.dmg

docs:
	@cd docs; make docs; cd ../

clean:
	@rm -rf build/ dist/
	@rm -f ./*.dmg
	@rm -rf ./vlcpython/ ./snowboy/; mkdir ./vlcpython ./snowboy
	@cd docs; make clean; cd ../
