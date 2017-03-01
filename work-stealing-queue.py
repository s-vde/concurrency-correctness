
import os
import execution_tree as ext
import itertools
import ntpath
import search_tree as st

#---------------------------------------------------------------------------------------------------

state_space_explorer = "/Volumes/Repositories/projects/programming/state-space-explorer/"

#---------------------------------------------------------------------------------------------------

master_thread = ["0 thread create",
                 "0 atomic load tail",
                 "0 atomic load head", 
                 "0 load mask",
                 "0 store jobs[0]",      
                 "0 atomic store tail",
                 "0 atomic load tail",
                 "0 atomic load head",
                 "0 load mask",
                 "0 store jobs[1]",      
                 "0 atomic store tail"]

#---------------------------------------------------------------------------------------------------
                 
worker_thread = ["1 thread create",
                 "1 atomic load head",
                 "1 atomic store head",
                 "1 atomic load tail",
                 "1 load mask",
                 "1 load jobs[0]"]
                 
#---------------------------------------------------------------------------------------------------

program = [master_thread, worker_thread]



#---------------------------------------------------------------------------------------------------
# DPOR
#---------------------------------------------------------------------------------------------------

def add_and_remove_happens_before(tree, source_sched, dest_sched, backtrack_thread,
                                  program_name, execution_index, hb_index):
    st.add_happens_before_edge(tree, source_sched, dest_sched)
    ext.dump(tree, "trees/dpor", "%s-%d-hb-%d" % (program_name, execution_index, hb_index))
    new_schedule = list(source_sched)
    new_schedule.pop()
    ext.add_to_node_label(tree, ext.node_of_schedule(new_schedule), "todo={%d}" % backtrack_thread, "blue")
    ext.dump(tree, "trees/dpor", "%s-%d-hb-%d-bt" % (program_name, execution_index, hb_index))
    st.remove_happens_before_edge(tree, source_sched, dest_sched)
    
#---------------------------------------------------------------------------------------------------

def print_work_stealing_queue_dpor(file_name):
    output_dir = "trees/dpor"
    
    # Print the whole tree
    tree = ext.parse(file_name)
    ext.dump(tree, output_dir, "%s-all" % ntpath.basename(file_name))
    
    # Print step-by-step
    tree = ext.execution_tree()

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ### Execution 1
    schedule = [0,0,0,0,0,0,0,0,1,1,1,1,1,1]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "work-stealing-queue-1")
    
    # Happens-before 1
    add_and_remove_happens_before(tree, [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,1,1,1], 1,
                                  "work-stealing-queue", 1, 1)
    add_and_remove_happens_before(tree, [0,0,0,0,0,0], [0,0,0,0,0,0,0,0,1,1,1,1], 1,
                                  "work-stealing-queue", 1, 2)
    add_and_remove_happens_before(tree, [0,0,0,0,0], [0,0,0,0,0,0,0,0,1,1,1,1,1,1], 1,
                                  "work-stealing-queue", 1, 3)
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ### Execution 2
    schedule = [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "work-stealing-queue-2")
    
    # Happens-before 2
    # sleep-set-blocked
    add_and_remove_happens_before(tree, [0,0,0,0,0,0,0,1,1,1], [0,0,0,0,0,0,0,1,1,1,1,1,1,0], 0,
                                  "work-stealing-queue", 2, 1)
    add_and_remove_happens_before(tree, [0,0,0,0,0,0,0,1,1,1,1,1,1], [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0], 0,
                                  "work-stealing-queue", 2, 2)
    # transitive reduction
    add_and_remove_happens_before(tree, [0,0,0,0,0,0,0,1,1,1,1], [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0], 0,
                                  "work-stealing-queue", 2, 3)
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ### Execution 3
    schedule = [0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "work-stealing-queue-3")
    
    # Happens-before 3
    add_and_remove_happens_before(tree, [0,0,0,0,0,0,0,1,1,1,1,1,0,0,0], [0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1], 1,
                                  "work-stealing-queue", 3, 1)
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)

#---------------------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------------------
# BOUNDED SEARCH 
#---------------------------------------------------------------------------------------------------

def print_work_stealing_queue_bounded_search(bounded_search_preemptions_path):
    output_dir = "trees/bounded_search"
    
    # Print the whole tree (0 preemptions)
    tree = ext.parse("%s/0/visible_schedules.txt" % bounded_search_preemptions_path)
    ext.dump(tree, output_dir, "%s-preemptions-0" % ntpath.basename("work-stealing-queue-all"))
    
    # Print the whole tree (1 preemptions)
    tree = ext.parse("%s/1/visible_schedules.txt" % bounded_search_preemptions_path)
    ext.dump(tree, output_dir, "%s-preemptions-1" % ntpath.basename("work-stealing-queue-all"))
    
    
    tree = ext.execution_tree()
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ### Execution 0.1
    schedule = [0,0,0,0,0,0,0,0,1,1,1,1,1,1]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "work-stealing-queue-pre-0-1")
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    ### Execution 0.2
    schedule = [0,0,0,0,0,0,0,1]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,0]), "diamond", 0.3, 0.3, "blue")
    ext.dump(tree, output_dir, "work-stealing-queue-pre-0-1-no-1")
    ext.reset_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,0]))
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    ext.remove_schedule(tree, schedule, 8)
    
    ### Execution 0.3
    schedule = [0,0,0,0,0,0,1]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0]), "diamond", 0.3, 0.3, "blue")
    ext.dump(tree, output_dir, "work-stealing-queue-pre-0-1-no-2")
    ext.reset_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0]))
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    ext.remove_schedule(tree, schedule, 7)
    
    ### Execution 0.4
    schedule = [1,1,1,1,0,0,0,0,0,0,0]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "work-stealing-queue-pre-0-2")
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    
    tree = ext.execution_tree()
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ### Execution 1.1
    schedule = [0,0,0,0,0,0,0,0,1,1,1,1,1,1]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.dump(tree, output_dir, "work-stealing-queue-pre-1-1")
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    ### Execution 1.2
    schedule = [0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,0]), "diamond", 0.3, 0.3, "blue")
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,0,1,1,1,1,1,1]), "diamond", 0.3, 0.3, "lightblue")
    ext.dump(tree, output_dir, "work-stealing-queue-pre-1-2")
    ext.reset_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,0]))
    ext.reset_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,0,1,1,1,1,1,1]))
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    ### Execution 1.3
    schedule = [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0]
    ext.add_schedule(tree, schedule)
    ext.highlight_schedule(tree, schedule)
    ext.add_execution_from_program_and_schedule(tree, program, schedule)
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0]), "diamond", 0.3, 0.3, "blue")
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,1,1,1,1,1,1]), "diamond", 0.3, 0.3, "lightblue")
    ext.dump(tree, output_dir, "work-stealing-queue-pre-1-3")
    ext.reset_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0]))
    ext.reset_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0,1,1,1,1,1,1]))
    ext.add_schedule(tree, schedule)
    ext.reset_schedule(tree, schedule)
    
    ### Execution 0.4
    # schedule = [1,1,1,1,0,0,0,0,0,0,0]
    # ext.add_schedule(tree, schedule)
    # ext.highlight_schedule(tree, schedule)
    # ext.add_execution_from_program_and_schedule(tree, program, schedule)
    # ext.dump(tree, output_dir, "work-stealing-queue-pre-0-2")
    # ext.add_schedule(tree, schedule)
    # ext.reset_schedule(tree, schedule)
    
# def print_work_stealing_queue_dfs():
    # output_dir = "trees/dfs"
    
    # tree = ext.execution_tree()
    # schedules = itertools.permutations([0,0,0,0,0,0,0,0,1,1,1,1,1,1])
    # for schedule in schedules:
        # print (schedule)
        # ext.add_schedule(tree, schedule)
    # ext.dump(tree, output_dir, "work-stealing-queue-all")


#---------------------------------------------------------------------------------------------------

# print_work_stealing_queue_dfs()
print_work_stealing_queue_bounded_search("%s/output/work-stealing-queue2/depth_first_search/bound/Preemptions" % state_space_explorer)
print_work_stealing_queue_dpor("%s/output/work-stealing-queue2/depth_first_search/dpor/Persistent/visible_schedules.txt" % state_space_explorer)
