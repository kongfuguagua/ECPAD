#!/bin/bash


cross_compile_plc="/cross_compile"

function install_st_optimizer {
    echo "[ST OPTIMIZER]"
    cd "$cross_compile_plc/utils/st_optimizer_src"
    g++ st_optimizer.cpp -o "$cross_compile_plc/st_transition/st_optimizer" || echo "Error compiling ST Optimizer"
    cd "$cross_compile_plc"
}


function install_matiec {
    echo "[MATIEC COMPILER]"
    cd "$cross_compile_plc/utils/matiec_src"
    autoreconf -i
    ./configure
    make
    cp ./iec2c "$cross_compile_plc/st_transition/" || echo "Error compiling MatIEC"
    cd "$cross_compile_plc"
}


function install_glue_generator {
    echo "[GLUE GENERATOR]"
    cd "$cross_compile_plc/utils/glue_generator_src"
    g++ -std=c++11 glue_generator.cpp -o "$cross_compile_plc/st_transition/glue_generator" || echo "Error compiling Glue Generator"
    cd "$cross_compile_plc"
}

function install_cross_compile {
    echo "[INASTALL ARM-GNU-TOOLCHAIN]"
    wget https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz
    tar -xJf arm-gnu-toolchain-13.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz
    rm arm-gnu-toolchain-13.2.rel1-x86_64-aarch64-none-linux-gnu.tar.xz
    mv arm-gnu-toolchain-13.2.Rel1-x86_64-aarch64-none-linux-gnu /opt/arm-gnu-toolchain-x86_64-aarch64-none-linux-gnu
}

function install_all_libs {
    install_st_optimizer
    install_glue_generator
    install_matiec
    install_cross_compile
}


install_all_libs
rm -rf "$cross_compile_plc/utils"


