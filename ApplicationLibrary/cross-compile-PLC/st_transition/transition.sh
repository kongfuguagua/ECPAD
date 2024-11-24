#!/bin/bash

echo "Optimizing ST program..."
./st_optimizer ./st_files/* ./st_files/*

echo "Generating C files..."
./iec2c -f -l -p -r -R -a ./st_files/*
if [ $? -ne 0 ]; then
    echo "Error generating C files"
    echo "ST transition finished with errors!"
    exit 1
fi


echo "Generating glueVars..."
./glue_generator

echo "Moving Files..."
sed -i '1 i #include "POUS.h"' POUS.c
sed -i '17 d' Res0.c
mv -f POUS.c Config0.c Res0.c glueVars.cpp ../project/src
mv -f POUS.h Config0.h LOCATED_VARIABLES.h ../project/include
rm VARIABLES.csv  
if [ $? -ne 0 ]; then
    echo "Error moving files"
    echo "ST transition finished with errors!"
    exit 1
fi

# #compiling for each platform
# cd ../project

# echo "Generating object files..."
# g++ -std=gnu++11 -I ./lib -c Config0.c -lasiodnp3 -lasiopal -lopendnp3 -lopenpal -w
# if [ $? -ne 0 ]; then
#     echo "Error compiling C files"
#     echo "Compilation finished with errors!"
#     exit 1
# fi

# echo "Compiling Res0.c"
# g++ -std=gnu++11 -I ./lib -c Res0.c -lasiodnp3 -lasiopal -lopendnp3 -lopenpal
# if [ $? -ne 0 ]; then
#     echo "Error compiling C files"
#     echo "Compilation finished with errors!"
#     exit 1
# fi

# echo "Compiling main program..."
# g++ -std=gnu++11 *.cpp *.o -o openplc -I ./lib -I ./plc_net -pthread -fpermissive `pkg-config --cflags --libs libmodbus` -lasiodnp3 -lasiopal -lopendnp3 -lopenpal

# if [ $? -ne 0 ]; then
#     echo "Error compiling C files"
#     echo "Compilation finished with errors!"
#     exit 1
# fi


echo "ST transition finished successfully!"
exit 0