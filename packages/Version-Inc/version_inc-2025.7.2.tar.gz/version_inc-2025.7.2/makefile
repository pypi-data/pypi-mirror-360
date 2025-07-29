py=.venv/bin/python
program-name=version-inc

build: .requirements
	make clean
	$(py) -m build

clean:
	touch dist/fuck
	rm dist/*

upload:
	vinc
	make build
	$(py) -m twine upload --repository pypi dist/* $(flags)

reload:
	make upload
	pipx upgrade $(program-name)
	pipx upgrade $(program-name)

.requirements:
	touch .requirements
	$(py) -m pip install build twine
