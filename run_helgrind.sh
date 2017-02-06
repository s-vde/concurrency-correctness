#!/bin/sh

sut=`echo $1`

options=--suppressions=./${sut}.supp
#options=--gen-suppressions=all

clang++ -std=c++14 -O0 -g -lpthread ${sut} -o ${sut}_helgrind
valgrind --tool=helgrind ${options} -v ${sut}_helgrind
