
all: deploy-win7

clean-pyc:
	find . -name '*.pyc' | xargs rm -f


deploy-win7: clean-pyc
	rm -rf ../win7-deploy/scripts
	mkdir -p ../win7-deploy/scripts
	cp -r * ../win7-deploy/scripts


run-local:
	./main.py
