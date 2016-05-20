FROM phusion/baseimage

RUN rm /usr/sbin/policy-rc.d \
  && apt-get update \
  && apt-get install -y \
    curl \
    git-core \
    make \
    python3 \
    python3-dev \
    python3-pyqt4 \
    python-virtualenv \
    libxml2-dev \
    libxslt-dev \
    unzip \
    vim \
    wget \
    zip

RUN useradd -G sudo -u 1000 -m docker \
  && echo "docker ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
  && mkdir -p /docker

RUN virtualenv --python=python3 --system-site-packages /home/docker/venv3

COPY ./provision/docker/docker.bashrc /home/docker/.bashrc

WORKDIR /docker

RUN chown -R docker:docker /docker /home/docker
