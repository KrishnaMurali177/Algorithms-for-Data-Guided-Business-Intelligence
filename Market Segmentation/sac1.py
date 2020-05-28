import pandas as pd
import numpy as np
import sys
from igraph import *
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity_matrix(vert_1, vert_2, graph):
    v1 = np.array(list(graph.vs[vert_1].attributes().values())).reshape((1,-1))
    v2 = np.array(list(graph.vs[vert_2].attributes().values())).reshape((1,-1))
    return cosine_similarity(v1, v2)

def q_newman(graph, vertex, community, community_list):
    old_mod = graph.modularity(community_list, weights='weight')
    temp = community_list[vertex]
    community_list[vertex] = community
    new_mod = graph.modularity(community_list, weights='weight')
    community_list[vertex] = temp
    return float(new_mod - old_mod)

def q_attr(vertex, community, community_list, similarity_matrix):
    sum, count = 0,0
    for i in range(len(community_list)):
        if community_list[i] == community:
            sum += similarity_matrix[vertex][i]
            count += 1
    return float(sum/count*(len(set(community_list))))

def phase1(graph, alpha, similarity_matrix):
    comm_list = list(range(len(graph.vs)))
    flag = False
    max_iter = 15
    while not flag and max_iter != 0:
        max_iter-=1
        flag = True
        for vertex in range(len(graph.vs)):
            #Assign each vertex to a community
            comm_vert = comm_list[vertex]
            dq_max = -1
            comm = None
            for community in comm_list:
                if community != comm_vert:
                    #Compute delta Q using formula in equation 4 of the paper
                    dq = alpha * q_newman(graph, vertex, community, comm_list) + \
                         (1 - alpha) * q_attr(vertex, community, comm_list, similarity_matrix)
                    if dq_max < dq:
                        dq_max = dq
                        comm = community
                    # If there is positive gain
                if dq_max > 0 and comm:
                    flag = False
                    comm_list[vertex] = comm
                    # If negative gain, end the loop as it has converged
                elif dq_max <= 0:
                    flag = True
    return comm_list

def phase2(graph, phase1_communities, alpha):
    #Rebase the clusters and retain the original mappings
    comm_list, mapped_clusters = cluster_convert(phase1_communities)
    graph.contract_vertices(comm_list, combine_attrs="mean")
    graph.simplify(combine_edges=sum, multiple=True, loops=True)
    size = len(graph.vs)
    #Compute similarity matrix again
    sim_matrix = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            sim_matrix[i][j] = compute_similarity_matrix(i, j, graph)
    #Perform phase 1 again
    comm_list = phase1(graph, alpha, sim_matrix)
    return comm_list, mapped_clusters

def cluster_convert(list):
    mapping = {}
    converted_comm_list = []
    count = 0
    original_cluster_mapping = {}
    for i in range(len(list)):
        v = list[i]
        if v in mapping:
            converted_comm_list.append(mapping[v])
            original_cluster_mapping[mapping[v]].append(i)
        else:
            mapping[v] = count
            converted_comm_list.append(count)
            original_cluster_mapping[count] = [i]
            count += 1
    return converted_comm_list, original_cluster_mapping

def write_to_file(graph, community_list, mapped_clusters, alpha):
    output = ''
    for c in VertexClustering(graph, community_list):
        if c:
            final_list = []
            for v in c:
                final_list.extend(mapped_clusters[v])
            output += ','.join(str(i) for i in final_list)
            output += '\n'
    file = open("communities_" + str(alpha) + ".txt", "w+")
    file.write(output)
    file.close()
    return



def main(alpha):
    if alpha == 0.0:
        a = 0
    elif alpha == 0.5:
        a = 5
    elif alpha == 1.0:
        a = 1
    attr = pd.read_csv('data/fb_caltech_small_attrlist.csv')
    edges = [tuple([int(x) for x in line.strip().split(" ")]) for line in open('data/fb_caltech_small_edgelist.txt')]
    graph = Graph()
    graph.add_vertices(len(attr))
    graph.add_edges(edges)
    #Initialize weights
    graph.es['weight'] = 1
    size = len(attr)
    for column in attr.keys():
        graph.vs[column] = attr[column]
    sim_matrix = np.zeros((size,size))
    for i in range(size):
        for j in range(size):
            sim_matrix[i][j] = compute_similarity_matrix(i,j, graph)
    comm_phase1 = phase1(graph, alpha, sim_matrix)
    comm_phase2, mapped_clusters = phase2(graph, comm_phase1, alpha)
    write_to_file(graph, comm_phase2, mapped_clusters, a)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Enter valid alpha")
    else: main(float(sys.argv[1]))