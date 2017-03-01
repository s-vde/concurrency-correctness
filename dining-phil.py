
import os
import execution_tree as ext
import itertools
import ntpath
import search_tree as st

#---------------------------------------------------------------------------------------------------

phil0 = ["0 lock forks[0]",
         "0 lock fork[1]",
         "0 write number_of_meals[0]", 
         "0 unlock fork[1]",
         "0 unlock fork[0]"]

#---------------------------------------------------------------------------------------------------
                 
phil1 = ["1 lock fork[1]",
         "1 lock fork[0]",
         "1 write number_of_meals[1]", 
         "1 unlock fork[0]",
         "1 unlock fork[1]"]
                 
#---------------------------------------------------------------------------------------------------

program = [phil0, phil1]



#---------------------------------------------------------------------------------------------------

def print_dining_phil_tsan():
    output_dir = "trees/sanitizer"
    
    # Print step-by-step
    tree = ext.execution_tree()

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ### Execution 1
    schedule = [0,0,0,0,0,1,1,1,1,1]
    ext.add_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "dining-phil-tsan")
    
#---------------------------------------------------------------------------------------------------

print_dining_phil_tsan()
