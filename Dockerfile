# sshd
#
# VERSION               0.0.2

FROM centos:centos7.2.1511
MAINTAINER Ramendra<ramendra.cs@gmail.com>

# -----------------------------------------------------------------------------
# Import the RPM GPG keys for Repositories
# -----------------------------------------------------------------------------
RUN rpm --import http://mirror.centos.org/centos/RPM-GPG-KEY-CentOS-7 \
	&& rpm --import https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-7 \
	&& rpm --import https://dl.iuscommunity.org/pub/ius/IUS-COMMUNITY-GPG-KEY

# -----------------------------------------------------------------------------
# Base Install
# -----------------------------------------------------------------------------
RUN rpm --rebuilddb \
	&& yum -y install \
	centos-release-scl \
	centos-release-scl-rh \
	epel-release \
	https://centos7.iuscommunity.org/ius-release.rpm \
	vim-minimal-7.4.160-1.el7 \
	sudo-1.8.6p7-16.el7 \
	openssh-6.6.1p1-23.el7_2 \
	openssh-server-6.6.1p1-23.el7_2 \
	openssh-clients-6.6.1p1-23.el7_2 \
	python-setuptools-0.9.8-4.el7 \
	yum-plugin-versionlock-1.1.31-34.el7 \
	vim-minimal \
	sudo \
	openssh \
	openssh-server \
	openssh-clients \
	python-setuptools \
	gcc* -y \
	net-tools \
	postfix \
	sendmail \
	git \
        yum-plugin-ovl \
	MySQL-python-1.2.5-1.el7.x86_64 \
	python-psycopg2-2.5.1-3.el7.x86_64 \
	python-pip \
	python-devel \
	libxslt-devel \
	libffi-devel \
	openssl-devel \
	httpd \
        wget \
        unzip \
	&& rm -rf /var/cache/yum/* \
	&& yum clean all

# Set the locale
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

RUN yum -y install crontabs
RUN yum -y install python-pip
RUN ssh-keygen -A
RUN mkdir /var/run/sshd
RUN mkdir /var/www/html/upload
RUN echo 'root:testauto' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN sed -i -e '/pam_loginuid.so/s/^/#/' /etc/pam.d/crond
RUN chmod 0644 /etc/crontab

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22 25 80 3306 5002
CMD ["/usr/sbin/sshd", "-D"]

ENV MYSQL_USER=root
ADD Mariadb.repo /etc/yum.repos.d/Mariadb.repo
RUN yum -y install  mariadb-devel mariadb-server mariadb-client
VOLUME /etc/mysql /var/lib/mysql

ENV test_auto_path /test_auto/
ENV PATH $test_auto_path:$PATH
RUN echo "export PATH=$PATH"

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app
COPY . /tmp/

ADD db.sql /app/inventory.sql

# Create the log file to be able to run tail
RUN touch /var/log/cron.log
# Run the command on container startup
COPY crontab /var/spool/cron/root

ENTRYPOINT ["/bin/bash"]
ADD run.sh /run.sh
RUN chmod 755 /*.sh
CMD ["/run.sh"]
