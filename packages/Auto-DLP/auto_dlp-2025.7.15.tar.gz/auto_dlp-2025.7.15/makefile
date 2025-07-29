py=.venv/bin/python
user=vorak
app=auto-dlp

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
	pipx upgrade $(app)
	pipx upgrade $(app)
	auto-dlp --version .

force_reload:
	pipx uninstall $(app)
	pipx install $(app)
