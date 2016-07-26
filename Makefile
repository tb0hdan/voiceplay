.PHONY: snowboy

CURDIR=$(shell pwd)

snowboy:
	@cd snowboy/swig/Python; make
	@cp -v snowboy/swig/Python/*.so extlib/snowboydetect/
	@cp -v snowboy/swig/Python/*.py extlib/snowboydetect/
	@cp -v snowboy/examples/Python/*.py extlib/snowboydetect/
	@cp -R snowboy/resources extlib/snowboydetect
	@cd $(CURDIR)

deps:	snowboy
	@pip install -r requirements.txt
