.PHONY: docs snowboy vlcpython

submodules:
	@git submodule init
	@git submodule update

snowboy:	submodules
	@cd snowboy/swig/Python; make
	@cp -v snowboy/swig/Python/*.so voiceplay/extlib/snowboydetect/
	@cp -v snowboy/swig/Python/*.py voiceplay/extlib/snowboydetect/
	@cp -v snowboy/examples/Python/*.py voiceplay/extlib/snowboydetect/
	@cp -R snowboy/resources voiceplay/extlib/snowboydetect

vlcpython:	submodules
	@cp -v vlcpython/generated/vlc.py voiceplay/extlib/vlcpython

deps:	snowboy vlcpython
	@pip install -U -r requirements.txt

piprot:	deps
	@piprot -o requirements.txt; exit 0

py2app:	deps
	@python setup_py2app.py py2app

pypi:	deps
	@python setup.py build sdist
	@twine upload dist/*

dmg:	py2app
	@hdiutil create -srcfolder dist/voiceplay.app ./voiceplay.dmg

docs:
	@cd docs; make docs; cd ../

test:
	@py.test -c ./tests/etc/pytest.ini -v tests/

coverage:
	@py.test -c ./tests/etc/pytest.ini --cov=./voiceplay --cov-config=./tests/etc/coveragerc tests/

clean:
	@rm -rf build/ dist/
	@rm -f ./*.dmg
	@rm -rf ./vlcpython/ ./snowboy/; mkdir ./vlcpython ./snowboy
	@cd docs; make clean; cd ../
