
import os
import pygraphviz as pgv

colors = ['black', 'black']

#----------------------------------------------------------------------------------------------------

def execution_graph():
    graph = pgv.AGraph(strict=False,directed=True)
    
    graph.graph_attr['dpi'] = '300'
    graph.graph_attr['strict'] = 'False'
    graph.graph_attr['directed'] = 'True' 
    graph.graph_attr['rankdir'] = 'TB'      # vertical edge direction
    graph.graph_attr['ranksep'] = '0.3'
    graph.graph_attr['nodesep'] = '2'
    # node style
    graph.node_attr['shape'] = 'point'
    graph.node_attr['fixedsize'] = 'true'
    graph.node_attr['width'] = '.05'
    graph.node_attr['style'] = 'filled'
    graph.node_attr['fillcolor'] = 'black'
    graph.node_attr['fontname'] = 'Ubuntu Code'
    # graph.node_attr['label'] = '""'
    graph.edge_attr['arrowsize'] = '0.5'
    graph.edge_attr['weight'] = '1'
    graph.edge_attr['fontname'] = 'Ubuntu Code'
    
    return graph
#----------------------------------------------------------------------------------------------------

    
def add_edge(graph, source_id, dest_id, thread_id, instruction):
    # add dummy node in the middle of the edge
    dummy_instr_id = "_instr_%s" % dest_id
    graph.add_node(dummy_instr_id, width='0', xlabel=("%s  " % instruction))
    graph.add_edge(source_id, dummy_instr_id, dir='none', color=colors[thread_id])
    graph.add_edge(dummy_instr_id, dest_id, color=colors[thread_id])
    
def add_happens_before_edge(graph, source_id, dest_id):
    graph.add_edge("_instr_%s" % source_id, "_instr_%s" % dest_id, weight='0', style='dotted', label='  hb  ')
    
def highlight(graph, node_id, color):
    node = graph.get_node(node_id)
    node.attr['fontcolor'] = color
    
def build_execution_tree(threads, output_dir, program_name):
    graph = execution_graph()
    graph.add_node(0)
    build_execution_subtree(graph, threads, 0, [0, 0], 0)
    dump_tree(graph, output_dir, "%s.dot" % program_name)
    
def build_execution_subtree(graph, threads, node_id, thread_indices, build_index):
    for thread_id in range(0, len(threads)):
        thread_index = thread_indices[thread_id]
        if (thread_index < len(threads[thread_id])):
            child_node_id = "%d-%d-%d" % (build_index, thread_id, thread_index)
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
            child_node_id = "%s-%d" % (node_id, thread_id)
            graph.add_node(child_node_id)
            add_edge(graph, node_id, child_node_id, thread_id, threads[thread_id][thread_index])
            thread_indices[thread_id] += 1
            node_id = child_node_id
            
def build_execution(threads, schedule, output_dir, program_name):
    graph = execution_graph()
    add_execution(graph, threads, schedule)
    dump_execution(graph, schedule, output_dir, program_name)
            
#=======================================================================================================================
# DUMP
#=======================================================================================================================
            
def dump_tree(graph, output_dir, program_name):
    os.system("test -d %s || mkdir -p %s" % (output_dir, output_dir))
    dot_name = "%s/%s.dot" % (output_dir, program_name)
    graph.write(dot_name)
    os.system("dot %s -Tjpg -o %s.jpg" % (dot_name, dot_name))
    
def dump_execution(graph, schedule, output_dir, program_name):
    schedule_str = "".join(map(lambda x : str(x[0]), schedule))
    dump_tree(graph, output_dir, "%s-%s" % (program_name, schedule_str))

#-----------------------------------------------------------------------------------------------------------------------
# DATA_RACES (two dataraces)
#-----------------------------------------------------------------------------------------------------------------------

def print_data_races_cpp():
    thread1 = [ "1 read x", "1 read y" ]
    thread2 = [ "2 write x", "2 read x", "2 read y", "2 write z" ]
    threads = [thread1, thread2]
    
    graph = execution_graph()
    schedule = [(0,0),(0,1),(1,0),(1,1),(1,2),(1,3)]
    add_execution(graph, threads, schedule)
    highlight(graph, "_instr_s-0", "red")
    highlight(graph, "_instr_s-0-0-1", "red")
    highlight(graph, "_instr_s-0-0", "blue")
    highlight(graph, "_instr_s-0-0-1-1-1", "blue")
    dump_execution(graph, schedule, "trees", "data_races[xy]")
    
    # TREE
    build_execution_tree(threads, "trees", "data_races")
    
print_data_races_cpp()

#----------------------------------------------------------------------------------------------------
# DATA_RACE (one race resolved)
#----------------------------------------------------------------------------------------------------

def print_data_race_cpp():
    thread1 = [ "1 lock m", "1 read x", "1 unlock m", "1 read y" ]
    thread2 = [ "2 lock m", "2 write x", "2 unlock m", "2 read x", "2 read y", "2 write z" ]
    threads = [thread1, thread2]
    
    graph = execution_graph()
    schedule = [(0,0),(0,1),(0,2),(0,3),(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6)]
    add_execution(graph, threads, schedule)
    highlight(graph, "_instr_s-0-0", "red")
    highlight(graph, "_instr_s-0-0-0-0-1-1", "red")
    highlight(graph, "_instr_s-0-0-0-0", "blue")
    highlight(graph, "_instr_s-0-0-0-0-1-1-1-1-1", "blue")
    dump_execution(graph, schedule, "trees", "data_race[xy]")
    
    add_happens_before_edge(graph, "s-0-0-0", "s-0-0-0-0-1")
    add_happens_before_edge(graph, "s-0-0", "s-0-0-0-0-1-1")
    dump_execution(graph, schedule, "trees", "data_race[xy-hb]")
    
print_data_race_cpp()

#----------------------------------------------------------------------------------------------------
# DATA_RACE_BRANCH
#----------------------------------------------------------------------------------------------------
    
def print_data_race_branch_cpp():
    thread1 = [ "1 read x", "1 read y" ]
    thread2 = [ "2 write x", "2 read x", "2 read y", "2 write z" ]
    threads = [thread1, thread2]

    graph = execution_graph()
    add_execution(graph, threads, [(0,0),(1,0),(1,1),(1,2),(1,3)])
    add_execution(graph, threads, [(1,0),(0,0),(0,1),(1,1),(1,2),(1,3)])
    # execution 1
    highlight(graph, "_instr_s-0", "red")
    highlight(graph, "_instr_s-0-1", "red")
    highlight(graph, "_instr_s-1", "red")
    highlight(graph, "_instr_s-1-0", "red")
    highlight(graph, "_instr_s-1-0-0", "blue")
    highlight(graph, "_instr_s-1-0-0-1-1", "blue")
    dump_tree(graph, "trees", "data_race_branch")

print_data_race_branch_cpp()

#----------------------------------------------------------------------------------------------------
# DATA_RACE_BRANCH_FIX
#----------------------------------------------------------------------------------------------------
    
def data_race_branch_fix_cpp(schedule):
    thread1 = [ "1 lock m", "1 read x", "1 unlock m", "1 read y" ]
    thread2 = [ "2 lock m", "2 write x", "2 unlock m", "2 read x", "2 read y", "2 write z" ]
    threads = [thread1, thread2]
    # build_execution(threads, [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(1,3),(1,4),(1,5)], "trees", "data_race_branch_fix")
    graph = execution_graph()
    add_execution(graph, threads, schedule)
    return graph
    
def print_data_race_branch_fix_cpp():
    
    schedule = [(1,0),(1,1),(1,2),(0,0),(0,1),(0,2),(1,3),(1,4),(1,5)]
    
    graph = data_race_branch_fix_cpp(schedule)
    # [x:] without happens-before
    highlight(graph, "_instr_s-1-1", "red")
    highlight(graph, "_instr_s-1-1-1-0-0", "red")
    dump_execution(graph, schedule, "trees", "data_race_branch_fix[hb-1]")
    # [x:] with happens-before
    add_happens_before_edge(graph, "s-1-1-1", "s-1-1-1-0")
    add_happens_before_edge(graph, "s-1-1", "s-1-1-1-0-0")
    dump_execution(graph, schedule, "trees", "data_race_branch_fix[hb-2]")

#----------------------------------------------------------------------------------------------------


#print_data_race_branch_cpp()
#print_data_race_branch_fix_cpp()


