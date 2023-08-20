#!/bin/zsh

# Tutorial Url: https://www.cnblogs.com/tuilk/p/16287472.html

hostip=$(cat /etc/resolv.conf | grep nameserver | awk '{ print $2 }')
wslip=$(hostname -I | awk '{print $1}')
port=$(sudo jq -r 'first(.inbounds[] | select(.protocol == "http")) | .port' /etc/v2raya/config.json)
 
PROXY_HTTP="http://${hostip}:${port}"
 
set_proxy(){
  export http_proxy="${PROXY_HTTP}"
  export HTTP_PROXY="${PROXY_HTTP}"
 
  export https_proxy="${PROXY_HTTP}"
  export HTTPS_PROXY="${PROXY_HTTP}"
 
  export all_proxy=${PROXY_SOCKS5}
  export ALL_PROXY="${PROXY_SOCKS5}"
 
  git config --global http.https://github.com.proxy ${PROXY_HTTP}
  git config --global https.https://github.com.proxy ${PROXY_HTTP}
 
  echo "Proxy has been opened. proxy address: ${PROXY_HTTP}"
}
 
unset_proxy(){
  unset http_proxy
  unset HTTP_PROXY

  unset https_proxy
  unset HTTPS_PROXY

  unset all_proxy
  unset ALL_PROXY

  git config --global --unset http.https://github.com.proxy
  git config --global --unset https.https://github.com.proxy
 
  echo "Proxy has been closed."
}
 
test_setting(){
  echo "Host IP:" ${hostip}
  echo "WSL IP:" ${wslip}
  echo "Try to connect to Google..."
  resp=$(curl -I -s --connect-timeout 5 -m 5 -w "%{http_code}" -o /dev/null www.google.com)
  if [ ${resp} = 200 ]; then
    echo "Proxy setup succeeded!"
  else
    echo "Proxy setup failed!"
  fi
}
 
if [ "$1" = "set" ]
then
  set_proxy
elif [ "$1" = "unset" ]
then
  unset_proxy
elif [ "$1" = "test" ]
then
  test_setting
else
  echo "Unsupported arguments."
fi
