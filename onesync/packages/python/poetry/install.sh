offical_installer (){
    curl -sSL https://install.python-poetry.org | python3 -
}

manual_install(){
	python -m venv poetry
	poetry/bin/pip install -U pip setuptool
	poetry/bin/pip install poetry
}

pipx_install(){
	pip install pipx
	pipx install poetry
	pipx ensurepath
}

main(){
	manual_install
}

main
