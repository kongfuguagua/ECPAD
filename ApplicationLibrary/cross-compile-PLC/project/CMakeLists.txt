cmake_minimum_required(VERSION 3.20)
project(CrossCompilePLC)

set(CMAKE_C_COMPILER "g++")
set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-w -fpermissive")
set(CMAKE_C_FLAGS "-w -fpermissive")
aux_source_directory(src sources)
add_executable(openplc main.cpp ${sources})

target_include_directories(openplc PUBLIC include)