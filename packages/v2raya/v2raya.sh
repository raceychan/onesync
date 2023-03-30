
function enable_systemd(){
    if ! [ -e /etc/wsl.conf ]
    then
        echo "[boot] \nsystemd=true" | sudo tee -a /etc/wsl.conf
    fi
}


function download_install_v2raya(){
    curl -Ls https://mirrors.v2raya.org/go.sh | sudo bash
    wget -qO - https://apt.v2raya.org/key/public-key.asc | sudo tee /etc/apt/trusted.gpg.d/v2raya.asc
    echo "deb https://apt.v2raya.org/ v2raya main" | sudo tee /etc/apt/sources.list.d/v2raya.list 
    sudo apt update
    sudo apt install v2raya
}

function autostart_v2raya(){
    sudo systemctl disable v2ray --now
    sudo systemctl start v2raya.service
    sudo systemctl enable v2raya.service
}

function main(){
    enable_systemd

    if  [ type -p v2raya ];
    then
        if ! [ systemctl is-enabled v2raya.service ];
        then
            autostart_v2raya
        fi;
    else
        download_install_v2raya && autostart_v2raya
    fi;

    echo "finish settings up "
}