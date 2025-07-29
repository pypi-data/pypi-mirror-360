py=.venv/bin/python
user=guenthner

set_user:
	cp ~/.pypirc_$(user) ~/.pypirc

build:
	make clean
	make version
	$(py) -m build

version:
	vinc

clean:
	touch dist/fuck
	rm dist/*

upload:
	make set_user
	make build
	$(py) -m twine upload --repository pypi dist/* $(flags)

reload:
	make upload
	pipx upgrade pycopy
	pipx upgrade pycopy
	pycopy --version . .
