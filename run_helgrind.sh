#!/bin/sh

sut=`echo $1`
nr_threads=`echo $2`

options=--suppressions=./my.supp
#options=--gen-suppressions=all

clang++ -std=c++14 -DNR_THREADS=${nr_threads} -O0 -g -lpthread ${sut} -o ${sut}_helgrind
valgrind --tool=helgrind ${options} -v ${sut}_helgrind
