py=.venv/bin/python

build:
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
	pipx upgrade auto-dlp
	pipx upgrade auto-dlp
	auto-dlp --version .
