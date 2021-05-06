FROM alpine:latest as builder
LABEL maintainer="deamen@gmail.com"

ENV PACKAGER="Song Tang <deamen@gmail.com>" \
    USERNAME="abuild" \
    TRANSMISSION_VERSION="3.00" 

RUN apk update && apk --no-cache add \
    build-base pkgconfig curl-static curl-dev \
    brotli-static brotli-dev nghttp2-static zlib-static \
    openssl-libs-static libevent-static libevent-dev xz

RUN adduser -S -g abuild $USERNAME
RUN echo "$USERNAME:$USERNAME" | chpasswd
RUN echo "$USERNAME     ALL=(ALL) ALL" >/etc/sudoers
RUN echo 'PACKAGER="$PACKAGER"' >/etc/abuild.conf

RUN addgroup $USERNAME abuild

RUN mkdir -p /var/cache/distfiles
RUN chmod a+w /var/cache/distfiles
RUN chgrp abuild /var/cache/distfiles
RUN chmod g+w /var/cache/distfiles

RUN chmod 777 /home/${USERNAME}

# LD doesn't search for *-static.a
RUN ln -s /usr/lib/libbrotlidec-static.a /usr/lib/libbrotlidec.a
RUN ln -s /usr/lib/libbrotlienc-static.a /usr/lib/libbrotlienc.a
RUN ln -s /usr/lib/libbrotlicommon-static.a /usr/lib/libbrotlicommon.a

USER abuild
WORKDIR /home/${USERNAME}

RUN wget -c https://github.com/transmission/transmission/releases/download/${TRANSMISSION_VERSION}/transmission-${TRANSMISSION_VERSION}.tar.xz
RUN tar -xf transmission-${TRANSMISSION_VERSION}.tar.xz
RUN cd transmission-${TRANSMISSION_VERSION} && \
    ./configure --prefix=/home/${USERNAME}/transmission-packaging/usr/local \
        --without-gtk \
        --without-inotify \
        --without-kqueue \
        --without-systemd \
        --disable-cli \
        --disable-nls \
        LIBCURL_LIBS="$(pkg-config --libs --static libcurl libbrotlidec libnghttp2)" && \
    make LDFLAGS="-all-static" && \
    make install

#Remove unnecessary files
RUN rm -rf /home/${USERNAME}/transmission-packaging/usr/local/share/man
RUN find /home/${USERNAME}/transmission-packaging/usr/local/bin -type f ! -iname transmission-daemon -exec rm -rf "{}" \;

RUN cd transmission-packaging && \
    tar -cJf /home/${USERNAME}/transmission-packaging/transmission-daemon-static-${TRANSMISSION_VERSION}.tar.xz usr

FROM scratch AS exporter

ENV PACKAGER="Song Tang <deamen@gmail.com>" \
    USERNAME="abuild" \
    TRANSMISSION_VERSION="3.00" 

COPY --from=builder /home/${USERNAME}/transmission-packaging/transmission-daemon-static-${TRANSMISSION_VERSION}.tar.xz /
