#!/bin/bash

DZB=`pwd`

echo '=== Installing prerequisites ==='
sudo apt-get update
sudo apt-get -y install i2c-tools python-smbus
sudo easy_install pygame

echo '=== Removing I2C devices from the blacklisting ==='
sudo cp /etc/modprobe.d/raspi-blacklist.conf /etc/modprobe.d/raspi-blacklist.conf.old
sudo sed -i 's/^blacklist i2c-bcm2708/#\0    # We need this enabled for I2C add-ons, e.g. ZeroBorg/g' /etc/modprobe.d/raspi-blacklist.conf

echo '=== Adding I2C devices to auto-load at boot time ==='
sudo cp /etc/modules /etc/modules.old
sudo sed -i '/^\s*i2c-dev\s*/d' /etc/modules
sudo sed -i '/^\s*i2c-bcm2708\s*/d' /etc/modules
sudo sed -i '/^#.*XLoBorg.*/d' /etc/modules
sudo bash -c "echo '' >> /etc/modules"
sudo bash -c "echo '# Kernel modules needed for I2C add-ons, e.g. ZeroBorg' >> /etc/modules"
sudo bash -c "echo 'i2c-dev' >> /etc/modules"
sudo bash -c "echo 'i2c-bcm2708' >> /etc/modules"

echo '=== Adding user "pi" to the I2C permissions list ==='
sudo adduser pi i2c

echo '=== Make scripts executable ==='
chmod a+x *.py
chmod a+x *.sh

echo '=== Create a desktop shortcut for the GUI example ==='
ZB_SHORTCUT="${HOME}/Desktop/ZeroBorg.desktop"
echo "[Desktop Entry]" > ${ZB_SHORTCUT}
echo "Encoding=UTF-8" >> ${ZB_SHORTCUT}
echo "Version=1.0" >> ${ZB_SHORTCUT}
echo "Type=Application" >> ${ZB_SHORTCUT}
echo "Exec=${DZB}/zbGui.py" >> ${ZB_SHORTCUT}
echo "Icon=${DZB}/piborg.ico" >> ${ZB_SHORTCUT}
echo "Terminal=false" >> ${ZB_SHORTCUT}
echo "Name=ZeroBorg Demo GUI" >> ${ZB_SHORTCUT}
echo "Comment=ZeroBorg demonstration GUI" >> ${ZB_SHORTCUT}
echo "Categories=Application;Development;" >> ${ZB_SHORTCUT}

echo '=== Finished ==='
echo ''
echo 'Your Raspberry Pi should now be setup for running ZeroBorg'
echo 'Please restart your Raspberry Pi to ensure the I2C driver is running'
