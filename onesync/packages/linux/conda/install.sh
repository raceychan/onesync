#!/bin/zsh

download_and_install_miniconda() {
    # Check if Miniconda is already installed
    if [ -d "$HOME/miniconda3" ]; then
        echo "Miniconda is already installed. Skipping installation."
        return
    fi

    # Update the system and install curl
    sudo apt-get update && sudo apt-get install -y curl

    # Change to the /tmp directory
    cd /tmp

    # Download the Miniconda installer
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh

    # Make the installer executable
    chmod +x miniconda.sh

    # Run the installer with silent mode
    ./miniconda.sh -b -p "$HOME/miniconda3"

    # Add Miniconda to the PATH environment variable
    echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> "$HOME/.bashrc"

    # source the bashrc file
    source "$HOME/.bashrc"

}

update_and_init_conda() {
    # Init conda
    conda init bash

    # Update conda
    conda update conda

    # create a default env
    conda create -n -y onesync python=3.11

    # init in current shell
    local shell=echo $0
    conda init $shell

    # Activate the new environment
    conda activate onesync

}

main() {
    # Check if conda is installed
    if ! command -v conda &> /dev/null; then
        download_and_install_miniconda
    fi

    update_and_init_conda "$@"
}

# Call the main function with command-line arguments
main "$@"
