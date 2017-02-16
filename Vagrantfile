# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/trusty64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 8000, host: 8765

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "~/.config", "/home/vagrant/.config"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
     vb.customize ["modifyvm", :id, '--audio', 'coreaudio', '--audiocontroller', 'hda']
     # Customize the amount of memory on the VM:
     vb.memory = "1024"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
     # for SpeechRecognition module/flac encoder
     dpkg --add-architecture i386
     apt-get update
     apt-get install -y linux-firmware alsa-tools mc libssl-dev
     apt-get install -y python-all-dev python-setuptools build-essential
     apt-get install -y libav-tools festival festival-dev portaudio19-dev vlc
     apt-get install -y pocketsphinx-utils swig libmagic1 libpulse-dev libreadline-dev
     apt-get install -y libblas-dev liblapack-dev libatlas-dev libatlas-base-dev
     apt-get install -y python-gobject libnotify-bin libnotify-dev
     apt-get install -y pulseaudio
     # for SpeechRecognition module/flac encoder
     apt-get install -y libc6:i386 libncurses5:i386 libstdc++6:i386
     easy_install pip
     pip install pyfestival requests
     pip install -U voiceplay urllib3[secure]
     # Fix audio ( https://wiki.ubuntu.com/Audio/UpgradingAlsa/DKMS )
     wget -q https://code.launchpad.net/~ubuntu-audio-dev/+archive/ubuntu/alsa-daily/+files/oem-audio-hda-daily-dkms_0.201702150732~ubuntu14.04.1_all.deb
     dpkg -i ./oem-audio-hda-daily-dkms*.deb
     gpasswd -a vagrant audio
     gpasswd -a vagrant pulse
     gpasswd -a vagrant pulse-access
     echo 'pulseaudio --start --daemonize 2>/dev/null' >> /home/vagrant/.bashrc
     sed -i -e 's/pcm.rear cards.pcm.rear/#pcm.rear cards.pcm.rear/g' /usr/share/alsa/alsa.conf
     sed -i -e 's/pcm.center_lfe cards.pcm.center_lfe/#pcm.center_lfe cards.pcm.center_lfe/g' /usr/share/alsa/alsa.conf
     sed -i -e 's/pcm.side cards.pcm.side/#pcm.side cards.pcm.side/g' /usr/share/alsa/alsa.conf
     # Fix festival voice
     wget -q http://www.speech.cs.cmu.edu/cmu_arctic/packed/cmu_us_clb_arctic-0.95-release.tar.bz2
     tar -xjpf ./cmu_us_clb_arctic-0.95-release.tar.bz2 -C /usr/share/festival/voices/english
     ln -s /usr/share/festival/voices/english/cmu_us_clb_arctic /usr/share/festival/voices/english/cmu_us_clb_arctic_clunits
     echo "(set! voice_default 'voice_cmu_us_clb_arctic_clunits)" >> /etc/festival.scm
     rm /var/cache/apt/archives/*.deb
  SHELL
end
