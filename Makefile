.PHONY: snowboy vlcpython

snowboy:
	@cd snowboy/swig/Python; make
	@cp -v snowboy/swig/Python/*.so extlib/snowboydetect/
	@cp -v snowboy/swig/Python/*.py extlib/snowboydetect/
	@cp -v snowboy/examples/Python/*.py extlib/snowboydetect/
	@cp -R snowboy/resources extlib/snowboydetect

vlcpython:
	@cp -v vlcpython/generated/vlc.py extlib/vlcpython

deps:	snowboy vlcpython
	@pip install -r requirements.txt
