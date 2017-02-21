
import os
import execution_tree as ext
import ntpath

colors = ['black', 'black']

def add_edge(graph, source_id, dest_id, thread_id, instruction):
    # add dummy node in the middle of the edge
    dummy_instr_id = "_instr_%s" % dest_id
    graph.add_node(dummy_instr_id, width='0', xlabel=("%s  " % instruction))
    graph.add_edge(source_id, dummy_instr_id, dir='none', color=colors[thread_id])
    graph.add_edge(dummy_instr_id, dest_id, color=colors[thread_id])
    
def add_happens_before_edge(graph, source_sched, dest_sched, label="hb"):
    graph.add_edge(ext.node_of_schedule(source_sched, "_instr_s."),
                   ext.node_of_schedule(dest_sched, "_instr_s."),
                   weight='0', 
                   style='dotted', 
                   label='  %s  ' % label)

def remove_happens_before_edge(graph, source_sched, dest_sched):
    graph.remove_edge(ext.node_of_schedule(source_sched, "_instr_s."),
                      ext.node_of_schedule(dest_sched, "_instr_s."))

    
def highlight(graph, node_id, color):
    node = graph.get_node(node_id)
    node.attr['fontcolor'] = color
    
def build_execution_tree(threads, output_dir, program_name, color='black', nodesep='3'):
    graph = ext.execution_tree(color, nodesep)
    graph.add_node("s")
    build_execution_subtree(graph, threads, "s", [0, 0], 0)
    return graph
    
def build_execution_subtree(graph, threads, node_id, thread_indices, build_index):
    for thread_id in range(0, len(threads)):
        thread_index = thread_indices[thread_id]
        if (thread_index < len(threads[thread_id])):
            child_node_id = "%s.%d" % (node_id, thread_id)
            graph.add_node(child_node_id)
            add_edge(graph, node_id, child_node_id, thread_id, threads[thread_id][thread_index])
            new_thread_indices = list(thread_indices)
            new_thread_indices[thread_id] += 1
            build_index = build_execution_subtree(graph, threads, child_node_id, new_thread_indices, build_index+1)
    return build_index
            
def add_execution(graph, threads, schedule):
    node_id = "s"
    graph.add_node(node_id)
    thread_indices = list(map(lambda x : 0, threads))
    for (thread_id, thread_index) in schedule:
        if (thread_index < len(threads[thread_id])):
            child_node_id = "%s.%d" % (node_id, thread_id)
            graph.add_node(child_node_id)
            add_edge(graph, node_id, child_node_id, thread_id, threads[thread_id][thread_index])
            thread_indices[thread_id] += 1
            node_id = child_node_id
            
def build_execution(threads, schedule, output_dir, program_name):
    graph = ext.execution_tree()
    add_execution(graph, threads, schedule)
    dump_execution(graph, schedule, output_dir, program_name)
            
#=======================================================================================================================
# DUMP
#=======================================================================================================================
    
def dump_execution(graph, schedule, output_dir, program_name):
    schedule_str = "".join(map(lambda x : str(x[0]), schedule))
    ext.dump(graph, output_dir, "%s-%s" % (program_name, schedule_str))

#-----------------------------------------------------------------------------------------------------------------------
# DATA_RACES (two dataraces)
#-----------------------------------------------------------------------------------------------------------------------

def print_data_races_cpp():
    thread1 = [ "0 read x", "0 read y" ]
    thread2 = [ "1 write x", "1 read x", "1 read y", "1 write z" ]
    threads = [thread1, thread2]
    
    # graph = ext.execution_tree()
    # schedule = [(0,0),(0,1),(1,0),(1,1),(1,2),(1,3)]
    # add_execution(graph, threads, schedule)
    # highlight(graph, "_instr_s.0", "red")
    # highlight(graph, "_instr_s.0.0.1", "red")
    # highlight(graph, "_instr_s.0.0", "blue")
    # highlight(graph, "_instr_s.0.0.1.1.1", "blue")
    # dump_execution(graph, schedule, "trees", "data_races[xy]")
    
    # TREE
    tree = build_execution_tree(threads, "trees", "data_races", 'black', '1.5')
    ext.dump(tree, "trees", "data_races")
    
    ext.highlight_schedule(tree, [1,0,1,0,1,1], "red")
    ext.dump(tree, "trees", "data_races_highlight1")
    
    ext.reset_schedule(tree, [1,0,1,0,1,1])
    ext.highlight_schedule(tree, [0,0,1,1,1,1], "green")
    ext.dump(tree, "trees", "data_races_highlight2")
    
print_data_races_cpp()

#----------------------------------------------------------------------------------------------------
# DATA_RACE (one race resolved)
#----------------------------------------------------------------------------------------------------

def print_data_race_cpp():
    thread1 = ["1 lock m", 
               "1 read x", 
               "1 unlock m"
            #    "1 read y" 
              ]
    thread2 = [ "2 lock m", "2 write x", "2 unlock m", "2 read x", "2 read y", "2 write z" ]
    threads = [thread1, thread2]
    
    graph = ext.execution_tree()
    schedule = [(0,0),
                (0,1),
                (0,2),
                # (0,3),
                (1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6)]
    add_execution(graph, threads, schedule)
    highlight(graph, "_instr_s.0.0", "red")
    highlight(graph, "_instr_s.0.0.0.1.1", "red")
    # highlight(graph, "_instr_s.0.0.0", "blue")
    # highlight(graph, "_instr_s.0.0.0.1.1.1.1.1", "blue")
    dump_execution(graph, schedule, "trees", "data_race[xy]")
    
    add_happens_before_edge(graph, "s.0.0.0", "s.0.0.0.1")
    add_happens_before_edge(graph, "s.0.0", "s.0.0.0.1.1")
    dump_execution(graph, schedule, "trees", "data_race[xy-hb]")
    
print_data_race_cpp()

#----------------------------------------------------------------------------------------------------
# DATA_RACE_BRANCH
#----------------------------------------------------------------------------------------------------
    
def print_data_race_branch_cpp():
    thread1 = [ "1 read x", "1 read y" ]
    thread2 = [ "2 write x", "2 read x", "2 read y", "2 write z" ]
    threads = [thread1, thread2]

    graph = ext.execution_tree()
    add_execution(graph, threads, [(0,0),(1,0),(1,1),(1,2),(1,3)])
    add_execution(graph, threads, [(1,0),(0,0),(0,1),(1,1),(1,2),(1,3)])
    # execution 1
    highlight(graph, "_instr_s.0", "red")
    highlight(graph, "_instr_s.0.1", "red")
    highlight(graph, "_instr_s.1", "red")
    highlight(graph, "_instr_s.1.0", "red")
    highlight(graph, "_instr_s.1.0.0", "blue")
    highlight(graph, "_instr_s.1.0.0.1.1", "blue")
    ext.dump(graph, "trees", "data_race_branch")

print_data_race_branch_cpp()

#---------------------------------------------------------------------------------------------------
# WORK_STEALING_QUEUE BS
#---------------------------------------------------------------------------------------------------

def print_work_stealing_queue_bs():
    output_dir = "trees/bs"
    
    ### Execution 1
    tree = ext.execution_tree()
    schedule = [0,0,0,0,0,0,1,1,1,1]
    ext.add_schedule(tree, schedule)
    ext.add_execution(tree, [
        (0,"0 atomic load tail"),   # 0
        (0,"0 atomic load head"),   # 0
        (0,"0 store jobs[0]"),      
        (0,"0 atomic store tail"),  # 1
        (0,"0 atomic load tail"),   # 1
        (0,"0 atomic load head"),   # 0
        (1,"1 atomic load head"),   # 0
        (1,"1 atomic store head"),  # 1
        (1,"1 atomic load tail"),   # 1
        (1,"1 load jobs[0]")
    ])
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,0]), "diamond", 0.3, 0.3, "blue")
    ext.dump(tree, "trees/bs", "work-stealing-queue-cs-1")
    
    ### Execution 2
    tree = ext.execution_tree()
    schedule = [0,0,0,0,0,1,1,1,1,0,0,0]
    ext.add_schedule(tree, schedule)
    ext.add_execution(tree, [
        (0,"0 atomic load tail"),   # 0
        (0,"0 atomic load head"),   # 0
        (0,"0 store jobs[0]"),      
        (0,"0 atomic store tail"),  # 1
        (0,"0 atomic load tail"),   # 1
        (1,"1 atomic load head"),   # 0
        (1,"1 atomic store head"),  # 1
        (1,"1 atomic load tail"),   # 1
        (1,"1 load jobs[0]"),       
        (0,"0 atomic load head"),   # 1
        (0,"0 store jobs[0]"),      
        (0,"0 atomic store tail"),  # 2
    ])
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0]), "diamond", 0.3, 0.3, "blue")
    ext.set_node_shape(tree, ext.node_of_schedule([0,0,0,0,0,1,1,1,1]), "diamond", 0.3, 0.3, "blue")
    ext.dump(tree, "trees/bs", "work-stealing-queue-cs-2")

print_work_stealing_queue_bs()