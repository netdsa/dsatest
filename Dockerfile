FROM alpine
MAINTAINER Vivien Didelot <vivien.didelot@savoirfairelinux.com>

RUN apk update \
 && apk upgrade \
 && apk add --no-cache \
    build-base \
    iproute2 \
    libffi \
    libffi-dev \
    openssh \
    openssl \
    openssl-dev \
    python3 \
    python3-dev \
 && pip3 install --no-cache-dir --upgrade \
    configparser \
    paramiko \
    pip \
    setuptools \
 && apk del \
    build-base \
    libffi-dev \
    openssl-dev \
    python3-dev \
 && apk info

WORKDIR /opt/dsatest
COPY . .
RUN python3 setup.py install
WORKDIR /
RUN rm -rf /opt/dsatest

ENTRYPOINT ["dsatest", "-f", "/etc/bench.cfg"]
