if command -v yum; then
    yum install -y zlib-devel
fi
if command -v apk; then
    apk add -y zlib-dev
fi

(
    cd tcl
    unix/configure --disable-shared --disable-zipfs
    make -j$(nproc || sysctl -n hw.ncpu)
)

