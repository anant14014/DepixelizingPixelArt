import networkx as nx
from keys import *

def curve_length(graph, source):
    queue = []
    explored = set([])
    queue.append(source)
    while (len(queue) > 0):
        node = queue.pop(0)
        if nx.degree(graph, node) == 2:
            for neighbour in graph[node]:
                if neighbour not in explored and neighbour not in queue:
                    queue.append(neighbour)
        explored.add(node)
    score = max(len(explored) - 1, 2)
    #print score
    return score

def curve_heuristic(graph, i, j):
    node_1 = (i, j)
    node_2 = (i + 1, j + 1)
    length = curve_length(graph, node_1)
    graph[node_1][node_2][HEURISTICS_SCORE] = graph[node_1][node_2][HEURISTICS_SCORE] + length
    node_1 = (i + 1, j)
    node_2 = (i, j + 1)
    length = curve_length(graph, node_1)
    graph[node_1][node_2][HEURISTICS_SCORE] = graph[node_1][node_2][HEURISTICS_SCORE] + length

def sparsity_heuristic(graph, i, j):
    #TODO: consider 8X8 window around diagonal only
    cc_1 = nx.node_connected_component(graph, (i, j))
    cc_2 = nx.node_connected_component(graph, (i + 1, j))
    score = min(abs(len(cc_1) - len(cc_2)), 64)
    if len(cc_1) < len(cc_2):
        graph[(i, j)][(i + 1, j + 1)][HEURISTICS_SCORE] = graph[(i, j)][(i + 1, j + 1)][HEURISTICS_SCORE] + score
    elif len(cc_1) > len(cc_2):
        graph[(i + 1, j)][(i, j + 1)][HEURISTICS_SCORE] = graph[(i + 1, j)][(i, j + 1)][HEURISTICS_SCORE] + score

def island_heuristic(graph, i, j):
    score = 5
    if nx.degree(graph, (i, j)) == 1 or nx.degree(graph, (i + 1, j + 1)) == 1:
        graph[(i, j)][(i + 1, j + 1)][HEURISTICS_SCORE] = graph[(i, j)][(i + 1, j + 1)][HEURISTICS_SCORE] + score
    if nx.degree(graph, (i + 1, j)) == 1 or nx.degree(graph, (i, j + 1)) == 1:
        graph[(i + 1, j)][(i, j + 1)][HEURISTICS_SCORE] = graph[(i + 1, j)][(i, j + 1)][HEURISTICS_SCORE] + score