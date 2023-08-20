# install conda
# install poetry
# poetry install
# instal core


install_conda(){
	source onesync/packages/linux/conda/install.sh && echo "conda is installed"
}

install_pipx(){
	sudo apt update && sudo apt install pipx && echo "pipx is installed"
	pipx ensurepath 
}

install_poetry(){
	pipx install poetry
	source .bashrc
	echo "poetry is installed"
}

install_dependencies(){
	conda activate onesync
	poetry install
	echo "project dependencies are installed"
}

main(){
	install_conda && conda init bash && conda activate onesync
	install_poetry
	install_dependencies
}


main
