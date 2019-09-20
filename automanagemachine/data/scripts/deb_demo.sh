#!/bin/sh
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

RSA_PUB_KEY_HTTP=https://gist.githubusercontent.com/frnode/681d838e61ff579e935eec1ac910a226/raw/OC_P5_RSA_PUB_KEY.pub
RSA_PUB_KEY_FILE=OC_P5_RSA_PUB_KEY.pub
USER_SSH=root
echo "Downloading the RSA key..." | write_log
wget --no-check-certificate $RSA_PUB_KEY_HTTP -P /root/.ssh | write_log
if [ $? -eq 0 ]; then
    echo "RSA public key file successfully downloaded" | write_log
else
    echo "Unable to download the file containing the RSA public key!" | write_log
fi

echo "Add RSA SSH key to authorized list..." | write_log

###
# START:SSH CONFIG
###
mkdir /$USER_SSH/.ssh | write_log
chmod 700 /$USER_SSH/.ssh | write_log

cd /$USER_SSH | write_log

touch /$USER_SSH/.ssh/authorized_keys | write_log
chmod 644 /$USER_SSH/.ssh/authorized_keys | write_log

cat /$USER_SSH/.ssh/$RSA_PUB_KEY_FILE >> /$USER_SSH/.ssh/authorized_keys | write_log

chmod 644 /$USER_SSH/.ssh/known_hosts | write_log
rm /$USER_SSH/.ssh/$RSA_PUB_KEY_FILE | write_log

sed -i 's/#\?\(PermitRootLogin\s*\).*$/\1yes/' /etc/ssh/sshd_config | write_log
sed -i 's/#\?\(PubkeyAuthentication\s*\).*$/\1yes/' /etc/ssh/sshd_config | write_log
sed -i 's/#\?\(PermitEmptyPasswords\s*\).*$/\1 no/' /etc/ssh/sshd_config | write_log
sed -i 's/#\?\(PasswordAuthentication\s*\).*$/\1 no/' /etc/ssh/sshd_config | write_log

service ssh restart | write_log
###
# END:SSH CONFIG
###
#
## apt_install nginx
#