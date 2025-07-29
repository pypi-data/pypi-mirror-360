py=.venv/bin/python
user=vorak

set_user:
	cp ~/.pypirc_$(user) ~/.pypirc

build:
	make clean
	$(py) -m build

clean:
	touch dist/fuck
	rm dist/*

upload:
	make set_user
	vinc
	make build
	$(py) -m twine upload --repository pypi dist/* $(flags)

reload:
	make upload
	pipx upgrade auto-dlp
	pipx upgrade auto-dlp
	auto-dlp --version .
