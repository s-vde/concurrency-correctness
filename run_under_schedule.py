#!/bin/sh

import os

state_space_explorer = "/Volumes/Repositories/projects/programming/state-space-explorer"

file = open("%s/schedules/schedule.txt" % state_space_explorer, 'w+')
file.write("[0,0,1,1,0,0,1,1,0,1]")
file.close()
file = open("%s/schedules/threads.txt" % state_space_explorer, 'w+')
file.write("2")
file.close()
file = open("%s/schedules/sleepset.txt" % state_space_explorer, 'w+')
file.write("")
file.close()

os.system("cd %s; source ./instrument.sh ../multithreaded/scheduler_demo.cpp 2; ./instrumented/scheduler_demo" % state_space_explorer)
