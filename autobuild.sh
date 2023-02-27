command -v python3 >/dev/null 2>&1 && PYEXISTS=true && PYVERSION=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')

 
function install_python {
    if [ ! -f "~/.hushlogin" ];then
        touch ~/.hushlogin
        echo ".hushlogin file created"
    fi;

    if [ "$PYEXISTS" = false ] || ! which pip > /dev/null;then 
        echo "python not exists, installing python 3.10"
        # do something here
    else
        # check if python version matches requirement
        echo "place holder"
    fi;

    if [ ! -f "${HOME}/.bashrc" ]; then
        touch $HOME/.bashrc
        # echo "alias python=python3" >> ~/.bashrc
        # alias python to python3
    fi;

    if ! which pip > /dev/null 2>&1;then 
            echo "pip not installed on current env, installing pip"
            sudo apt update && sudo apt install -y python3-pip
    else
            python3 pyautobuild.py
    fi;
}

install_python