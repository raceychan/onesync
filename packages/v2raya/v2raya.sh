
function enable_systemd(){
    #TODO: restart wsl
    if ! [ -e /etc/wsl.conf ];
    then
        echo "[boot] \nsystemd=true" | sudo tee -a /etc/wsl.conf
        reset
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
    # TODO: test if systemd is enabled on the system
    # if [ ps --no-headers -o comm 1 ];
    # then 

    sudo systemctl disable v2ray --now
    sudo systemctl start v2raya.service
    sudo systemctl enable v2raya.service
}

function setup_git(){
    type -p jq >/dev/null 2>&1 || sudo apt install -y jq # install jq only if its not installed    

    port=$(jq -r 'first(.inbounds[] | select(.protocol == "http")) | .port' /etc/v2raya/config.json) # extra first http port

    git config --global http.proxy http://127.0.0.1:$port # setup git http proxy
    git config --global https.proxy https://127.0.0.1:$port # set up git https proxy
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

    setup_git

    echo "finish settings up "
}