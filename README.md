# ycrmWebcamUpload
Python script running on a pi handling ycrm.de ftp webcam image upload

This script is uploading new webcam images out of the local ftp space up to the ycrm.de webspace. To define new webcam images or change the paths just edit the files variable.
The result: https://ycrm.de/index.php/webcam-newmainmenu/webcam-clubhaus

## Installation
This steps are needed to setup the script on a raspberry pi.
- Update system via `sudo apt update && sudo apt upgrade`
- Install `git` via `sudo apt install git`
- Clone repository `git clone https://github.com/pstiegele/ycrmWebcamUpload.git`
- Install `python` via `sudo apt install python3`
- Update `pip` via `pip install --upgrade pip`
- Install rust: `sudo curl https://sh.rustup.rs -sSf | sh`
- Install openssl: `sudo apt install libssl-dev`
- Install `pysftp`: `pip install pysftp`
- Create ramdisk directory: `sudo mkdir /mnt/ramdisk`
- Add line to auto-mount ramdisk in fstab: `sudo nano /etc/fstab` --> add `tmpfs /mnt/ramdisk tmpfs nodev,nosuid,size=50M 0 0`
- Mount ramdisk: `sudo mount -a`
- Check newly mounted ramdisk: `df -h`
- Configure python script: `nano /home/ycrm/ycrmWebcamUpload/uploadwebcamimage.py` --> set ftp and telegram credentials
- Install local FTP server `vsftpd`: `sudo apt install vsftpd`
- Check installation success: `sudo systemctl status vsftpd`
- Adapt `vsftpd` config: `sudo nano /etc/vsftpd.conf` --> 
-- Make sure, `anonymous_enable` is set to `No`
-- Set `local_enable=YES`
-- Set `write_enable=YES`
-- Set `chroot_local_user=YES`
-- Set `local_umask=002`
- Restart `vsftpd` by `sudo /etc/init.d/vsftpd restart`
- Add local user to grant access to ramdisk directory: `sudo adduser ycrmwebcam --shell /bin/false --home /mnt/ramdisk --no-create-home`. Password can be used from previous installation (if available). 
- Add non existing shells by opening `sudo nano /etc/shells` and add the line `/bin/false` at the bottom.
- Create common group for directory access: `sudo groupadd ramdiskAccess`
- Add the users `ycrm` and `ycrmwebcam` to the group: `sudo usermod -aG ramdiskAccess ycrm && sudo usermod -aG ramdiskAccess ycrmwebcam`
- Chown the ramdisk directory by the group: `sudo chown -R :ramdiskAccess /mnt/ramdisk`
- Be sure to grant read and write access to group members: `sudo chmod -R g+rwxs /mnt/ramdisk`
- Add crontab entry: `sudo nano /etc/crontab` --> add `* *     * * *   ycrm    /usr/bin/python3 /home/ycrm/ycrmWebcamUpload/uploadwebcamimage.py`

- If not already configured, set the webcams to upload the images accordingly to the defined paths. 
## Hint
If python error occurs that host key is missing: just connect once manually per ssh to server, save host key and thats it

## Todo
- notify if offline upload occurs
- create notification if uploads occurs with an delay lesser than 90s

## Credits
(C) 2020 Paul Stiegele
