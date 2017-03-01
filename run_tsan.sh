#!/bin/sh

sut=`echo $1`
nr_threads=`echo $2`
# llvm_base=`echo $3`

llvm_base=/Users/sanne/Desktop/tools/llvm-repo

here=`pwd .`

#cd ${llvm_base}/build/projects/compiler-rt/lib/tsan
#make
#cd ${here}

${llvm_base}/build/bin/clang++ -std=c++14 -DNR_THREADS=${nr_threads} -O0 -g -fsanitize=thread ${sut} -o ${sut}_tsan
./${sut}_tsan


