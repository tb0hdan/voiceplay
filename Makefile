.PHONY: cloc docs pylint snowboy vlcpython vagrant

ifeq ($(shell uname),Darwin)
    SED = sed -E
    SEDINPLACE = $(SED) -i '' -e
else
    SED = sed -r
    SEDINPLACE = $(SED) -i -e
endif

VERSION = $(shell cat voiceplay/__init__.py|grep '__version__'|$(SED) "s/((.+)=|'|\ )//g")
CPU_COUNT = $(shell python -c 'import multiprocessing; print multiprocessing.cpu_count() * 2 + 1')

submodules:
	@git submodule init
	@git submodule update

snowboy:	submodules
	@cd snowboy/swig/Python; make
	@cp -v snowboy/swig/Python/*.so voiceplay/extlib/snowboydetect/
	@cp -v snowboy/swig/Python/*.py voiceplay/extlib/snowboydetect/
	@cp -v snowboy/examples/Python/*.py voiceplay/extlib/snowboydetect/
	@cp -R snowboy/resources voiceplay/extlib/snowboydetect
	@touch voiceplay/extlib/snowboydetect/__init__.py
	@$(SEDINPLACE) '/import snowboydetect/s/import snowboydetect/import voiceplay.extlib.snowboydetect.snowboydetect as snowboydetect/g' voiceplay/extlib/snowboydetect/snowboydecoder.py

vlcpython:	submodules
	@cp -v vlcpython/generated/vlc.py voiceplay/extlib/vlcpython

deps:	snowboy vlcpython
	@pip install -r requirements.txt

piprot:	deps
	@piprot -o requirements.txt; exit 0

py2app:	deps
	@python setup_py2app.py py2app

pypi:	deps
	@python setup.py build sdist
	@twine upload dist/*

pylint:
	@pylint -j $(CPU_COUNT) --ignore extlib voiceplay; exit 0

dmg:	py2app
	@hdiutil create -srcfolder dist/voiceplay.app ./voiceplay.dmg

docs:
	@cd docs; make docs; cd ../

tag:
	@git tag -a v$(VERSION) -m 'v$(VERSION)'
	@git push origin v$(VERSION)

# make tag_delete tag=v0.2.0
tag_delete:
	@git tag -d $(tag)
	@git push origin :refs/tags/$(tag)

# Reboot step is required for audio drivers to catch up after installation
vagrant:
	@vagrant destroy -f
	@vagrant box update
	@vagrant up
	@vagrant ssh -c 'sudo reboot'
	@sleep 30; vagrant ssh -c 'amixer set Master 100%'
	@vagrant ssh -c 'sudo alsactl store'

vagrant_rebuild:	vagrant
	@rm -f voiceplay.box
	@vagrant package --output voiceplay.box

test:
	@py.test -c ./tests/etc/pytest.ini -v tests/

coverage:
	@py.test -c ./tests/etc/pytest.ini --cov=./voiceplay --cov-config=./tests/etc/coveragerc tests/

coverage_ci:	coverage
	@codeclimate-test-reporter

cloc:
	@cloc --exclude-dir=.idea,build,dist,extlib,vlcpython,snowboy ./

clean:
	@rm -rf build/ dist/ voiceplay.egg-info/ voiceplay/extlib; git checkout voiceplay/extlib
	@rm -f ./*.dmg
	@rm -rf ./vlcpython/ ./snowboy/; mkdir ./vlcpython ./snowboy
	@cd docs; make clean; cd ../
