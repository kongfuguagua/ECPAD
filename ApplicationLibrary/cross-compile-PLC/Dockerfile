FROM debian:bookworm

ADD . /cross_compile
WORKDIR /cross_compile

RUN apt update && apt upgrade -y && apt install -y tar xz-utils build-essential cmake automake bison flex autoconf wget
RUN ./install.sh

ENV PATH=/opt/arm-gnu-toolchain-x86_64-aarch64-none-linux-gnu/bin:$PATH 

ENTRYPOINT [ "bash" ]