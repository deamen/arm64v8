export container=$(buildah from arm64v8/alpine:3.16)
buildah config --label maintainer=""github.com/deamen"" $container

buildah run $container apk add git gcc make libc-dev bison flex openssl-dev python3 dtc gcc-arm-none-eabi py3-setuptools swig python3-dev
buildah run $container git clone https://github.com/ARM-software/arm-trusted-firmware.git
buildah run $container git clone https://github.com/u-boot/u-boot.git

buildah config --workingdir "/arm-trusted-firmware" $container
buildah run $container git checkout v2.8
buildah run $container make PLAT=rk3399 DEBUG=0 bl31
buildah config --env BL31="/arm-trusted-firmware/build/rk3399/release/bl31/bl31.elf" $container

buildah config --workingdir "/u-boot" $container
buildah run $container git checkout v2023.01
buildah copy $container rk3399-nanopi-r4se.dts arch/arm/dts/
buildah copy $container rk3399-nanopi-r4se-u-boot.dtsi arch/arm/dts/
buildah copy $container nanopi-r4se-rk3399_defconfig configs/nanopi-r4se-rk3399_defconfig
buildah run $container make -j$(nproc --ignore 1) nanopi-r4se-rk3399_defconfig
buildah run $container sed -i -e 's!^CONFIG_BOOTCOMMAND=.*!CONFIG_BOOTCOMMAND="console=ttyS2,115200n8;run distro_bootcmd"!' .config
buildah run $container sed -i -e 's!^CONFIG_BAUDRATE=.*!CONFIG_BAUDRATE=115200!' .config
buildah run $container make -j$(nproc --ignore 1)

buildah config --label maintainer=""github.com/deamen"" $container


cat << 'EOF' >> copy-u-boot.sh
#!/bin/sh
mnt=$(buildah mount $container)
cp $mnt/u-boot/u-boot-rockchip.bin ./u-boot-nanopi-r4se.bin
buildah umount $container
EOF
chmod a+x copy-u-boot.sh
buildah unshare ./copy-u-boot.sh
rm ./copy-u-boot.sh
buildah rm $container
