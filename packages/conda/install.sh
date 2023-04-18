#!/bin/zsh

download_and_install_miniconda() {
    # Update the system and install curl
    sudo apt-get update && sudo apt-get install curl

    # Change to the /tmp directory
    cd /tmp

    # Download the Miniconda installer
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

    # Make the installer executable
    chmod +x Miniconda3-latest-Linux-x86_64.sh

    # Run the installer
    ./Miniconda3-latest-Linux-x86_64.sh

    # Source the .zshrc file
    source ~/.zshrc
}

update_and_init_conda() {
    # Update conda
    conda update conda

    # Create a new conda environment with the given arguments
    conda create "$@"

    # Initialize conda for zsh
    conda init zsh

    # Activate the new environment
    conda activate myproject
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