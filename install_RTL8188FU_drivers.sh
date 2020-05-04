sudo echo "deb http://ppa.launchpad.net/kelebek333/kablosuz/ubuntu bionic main" > /etc/apt/sources.list.d/kelebek333-ubuntu-kablosuz-bionic.list
sudo apt-get update
sudo apt install rtl8188fu-dkms
sudo reboot
