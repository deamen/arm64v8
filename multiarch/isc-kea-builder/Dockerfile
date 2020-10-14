FROM arm64v8/alpine:latest as builder
LABEL maintainer="deamen@gmail.com"

ENV PACKAGER="Song Tang <deamen@gmail.com>" \
    USERNAME="abuild" \
    KEA_VERSION="1.8.0"  \
    KEA_ISC_VERSION="1"

COPY bin/qemu-aarch64-static /usr/bin/
RUN apk update && apk --no-cache add \
    alpine-sdk \
    autoconf \
    automake \
    libtool \
    py3-sphinx \
    py3-pip \
    git build-base boost-dev log4cplus-dev bison openssl-dev flex libcap mariadb-dev postgresql-dev python3-dev procps 

RUN pip install sphinx_rtd_theme

RUN adduser -S -g abuild $USERNAME
RUN echo "$USERNAME:$USERNAME" | chpasswd
RUN echo "$USERNAME     ALL=(ALL) ALL" > /etc/sudoers
RUN echo 'PACKAGER="$PACKAGER"' > /etc/abuild.conf

RUN addgroup $USERNAME abuild

RUN mkdir -p /var/cache/distfiles
RUN chmod a+w /var/cache/distfiles
RUN chgrp abuild /var/cache/distfiles
RUN chmod g+w /var/cache/distfiles

RUN chmod 777 /home/${USERNAME}

USER root
WORKDIR /home/${USERNAME}

RUN abuild-keygen -a -i
RUN git clone https://gitlab.isc.org/isc-projects/kea-packaging.git
RUN sed -i '/pkgname.*premium/d' kea-packaging/alpine/APKBUILD
RUN sed -i "s/KEA_VERSION/${KEA_VERSION}/g" kea-packaging/alpine/APKBUILD
RUN sed -i "s/KEA_ISC_VERSION/${KEA_ISC_VERSION}/g" kea-packaging/alpine/APKBUILD
RUN cd kea-packaging/alpine && wget -c  https://ftp.isc.org/isc/kea/${KEA_VERSION}/kea-${KEA_VERSION}.tar.gz
RUN cd kea-packaging/alpine && abuild -P /home/${USERNAME} -F checksum
RUN cd kea-packaging/alpine && abuild -P /home/${USERNAME} -F -r

FROM scratch AS exporter

ENV PACKAGER="Song Tang <deamen@gmail.com>" \
    USERNAME="abuild" \
    KEA_VERSION="1.8.0"  \
    KEA_ISC_VERSION="1"
COPY --from=builder /home/${USERNAME}/kea-packaging/aarch64 /
