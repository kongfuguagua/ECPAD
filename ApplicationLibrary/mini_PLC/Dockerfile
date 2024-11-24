FROM alpine:latest

ADD . /miniplc
WORKDIR /miniplc
RUN apk add --no-cache make automake gcc autoconf cmake bash g++ linux-headers libtool
RUN mkdir /lib64 && ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2
RUN apk del -r make automake autoconf cmake g++ linux-headers libtool

ENTRYPOINT ["/bin/bash"]