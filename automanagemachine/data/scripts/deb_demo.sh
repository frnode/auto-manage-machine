#!/bin/bash
function write_log
{
  while read text
  do
      LOGTIME=`date "+%Y-%m-%d %H:%M:%S"`
      LOG_FILE=deb_demo.log
      # If log file is not defined, just echo the output
      if [ "$LOG_FILE" == "" ]; then
    echo $LOGTIME": $text";
      else
        LOG=$LOG_FILE.`date +%Y%m%d`
    touch $LOG
        if [ ! -f $LOG ]; then echo "ERROR! Cannot create log file $LOG. Exiting."; exit 1; fi
    echo $LOGTIME": $text" | tee -a $LOG;
      fi
  done
}

function apt_install {
  sudo apt-get -y install $1
  if [ $? -ne 0 ]; then
    echo "Can not install package: $1 - Abort"
    exit 1
  fi
}

function wget_file {
  wget --no-check-certificate $1 -P $2
  if [ $? -eq 0 ]; then
      echo "File successfully downloaded."
  else
      echo "Unable to download the file!"
  fi
}

echo "*** Automated installation of SSH, NGINX, PHP and MariaDB ***"

echo "Updating lists..."
apt update

echo "Installing wget..."
apt_install wget

RSA_PUB_KEY_HTTP=https://gist.githubusercontent.com/frnode/681d838e61ff579e935eec1ac910a226/raw/OC_P5_RSA_PUB_KEY.pub
RSA_PUB_KEY_FILE=OC_P5_RSA_PUB_KEY.pub
USER_SSH=root
echo "Downloading and launching the SSH configuration script..."
wget_file https://gist.githubusercontent.com/frnode/7204df1e0225f55ff3e74045db7702d7/raw/deb_install_rsa_key.sh /
bash ./deb_install_rsa_key.sh $RSA_PUB_KEY_HTTP $RSA_PUB_KEY_FILE $USER_SSH | write_log