#!/bin/bash
set -x
/etc/init.d/mysql start
/usr/bin/mysqld_safe > /dev/null 2>&1 &

RET=1
while [[ RET -ne 0 ]]; do
    echo "=> Waiting for confirmation of MySQL service startup"
    sleep 10
    mysql -uroot -e "status" > /dev/null 2>&1
    RET=$?
done

#mysql -uroot -e "CREATE DATABASE inventory"
mysql -uroot < /app/inventory.sql
localedef -i en_US -f UTF-8 en_US.UTF-8
ssh-keygen -A
mkdir -p /var/run/sshd
echo 'root:testauto' | chpasswd
sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

/usr/sbin/sshd -D &
/sbin/crond &
/usr/sbin/apachectl -DFOREGROUND &
/usr/libexec/postfix/master -w
python -u /app/tef.py
