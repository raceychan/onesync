from base import shell

def setup_repository():
    shell("sudo apt-get update")
    shell("sudo apt-get install ca-certificates curl gnupg")
    """
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    """


