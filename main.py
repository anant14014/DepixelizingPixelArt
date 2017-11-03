import networkx as nx
from PIL import Image
import matplotlib.pyplot as plt

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
    graph[node_1][node_2]['score'] = graph[node_1][node_2]['score'] + length
    node_1 = (i + 1, j)
    node_2 = (i, j + 1)
    length = curve_length(graph, node_1)
    graph[node_1][node_2]['score'] = graph[node_1][node_2]['score'] + length

def sparsity_heuristic(graph, i, j):
    #TODO: consider 8X8 window around diagonal only
    cc_1 = nx.node_connected_component(graph, (i, j))
    cc_2 = nx.node_connected_component(graph, (i + 1, j))
    score = min(abs(len(cc_1) - len(cc_2)), 64)
    if len(cc_1) < len(cc_2):
        graph[(i, j)][(i + 1, j + 1)]['score'] = graph[(i, j)][(i + 1, j + 1)]['score'] + score
    elif len(cc_1) > len(cc_2):
        graph[(i + 1, j)][(i, j + 1)]['score'] = graph[(i + 1, j)][(i, j + 1)]['score'] + score

def island_heuristic(graph, i, j):
    score = 5
    if nx.degree(graph, (i, j)) == 1 or nx.degree(graph, (i + 1, j + 1)) == 1:
        graph[(i, j)][(i + 1, j + 1)]['score'] = graph[(i, j)][(i + 1, j + 1)]['score'] + score
    if nx.degree(graph, (i + 1, j)) == 1 or nx.degree(graph, (i, j + 1)) == 1:
        graph[(i + 1, j)][(i, j + 1)]['score'] = graph[(i + 1, j)][(i, j + 1)]['score'] + score

def print_graph(graph,title):
    plt.figure()
    plt.title(title)
    x = [-node[0] for node in similarity_graph.nodes()]
    y = [node[1] for node in similarity_graph.nodes()]
    plt.scatter(y,x)
    for edge in similarity_graph.edges():
        plt.plot([edge[0][1],edge[1][1]],[-edge[0][0],-edge[1][0]])
    plt.show()


# I/O
filename = 'input_images/smw_boo_input.png'
img = Image.open(filename)
img = img.convert('YCbCr')
pixels = img.load()

#Create graph
similarity_graph = nx.Graph()

#Add nodes
for i in range(img.width):
    for j in range(img.height):
        similarity_graph.add_node((i, j), pixel_value=pixels[j, i])

#Add edges
#TODO check channels, range, other error possibilities
y_threshold = 48
u_threshold = 7
v_threshold = 6
for i in range(img.width):
    for j in range(img.height):
        current_node = (i, j)
        nodes_to_connect = []
        nodes_to_connect.append((i + 1, j))
        nodes_to_connect.append((i - 1, j))
        nodes_to_connect.append((i, j + 1))
        nodes_to_connect.append((i, j - 1))
        nodes_to_connect.append((i + 1, j + 1))
        nodes_to_connect.append((i + 1, j - 1))
        nodes_to_connect.append((i - 1, j + 1))
        nodes_to_connect.append((i - 1, j - 1))
        for neighbour_node in nodes_to_connect:
            if (similarity_graph.has_node(neighbour_node)):
                y_diff = abs(similarity_graph.nodes[current_node]['pixel_value'][0] - similarity_graph.nodes[neighbour_node]['pixel_value'][0])
                u_diff = abs(similarity_graph.nodes[current_node]['pixel_value'][1] - similarity_graph.nodes[neighbour_node]['pixel_value'][1])
                v_diff = abs(similarity_graph.nodes[current_node]['pixel_value'][2] - similarity_graph.nodes[neighbour_node]['pixel_value'][2])
                if (y_diff <= y_threshold) and (u_diff <= u_threshold) and (v_diff <= v_threshold):
                    similarity_graph.add_edge(current_node, neighbour_node)

#print_graph(similarity_graph, "before removing")

#Remove diagonals from fully-connected blocks
for i in range(img.width - 1):
    for j in range(img.height - 1):
        nodes = []
        nodes.append((i, j))
        nodes.append((i + 1, j))
        nodes.append((i, j + 1))
        nodes.append((i + 1, j + 1))
        edges = [edge for edge in similarity_graph.edges(nodes) if (edge[0] in nodes and edge[1] in nodes)]
        if similarity_graph.has_edge((i, j), (i + 1, j + 1)) and similarity_graph.has_edge((i + 1, j), (i, j + 1)):
            if (len(edges) == 6):
                similarity_graph.remove_edge((i, j), (i + 1, j + 1))
                similarity_graph.remove_edge((i + 1, j), (i, j + 1))
            elif (len(edges) == 2):
                similarity_graph[(i, j)][(i + 1, j + 1)]['score'] = 0
                similarity_graph[(i + 1, j)][(i, j + 1)]['score'] = 0
                curve_heuristic(similarity_graph, i, j)
                sparsity_heuristic(similarity_graph, i, j)
                island_heuristic(similarity_graph, i, j)
                #print similarity_graph[(i, j)][(i + 1, j + 1)]['score']
                #print similarity_graph[(i + 1, j)][(i, j + 1)]['score']
                if similarity_graph[(i, j)][(i + 1, j + 1)]['score'] > similarity_graph[(i + 1, j)][(i, j + 1)]['score']:
                    similarity_graph.remove_edge((i + 1, j), (i, j + 1))
                else:
                    similarity_graph.remove_edge((i, j), (i + 1, j + 1))
            else:
                "Error! Block has abnormal number of edges"

# print_graph(similarity_graph, "after removing")

# voronoi cells
for x in range(img.width):
    for y in range(img.height):

        voronoi_cell_center_x = x + 0.5
        voronoi_cell_center_y = y + 0.5

        similarity_graph.nodes[(x, y)]['voronoi_cell_center'] = (voronoi_cell_center_x, voronoi_cell_center_y)

        voronoi_cell_vertices = []

        # top left
        if similarity_graph.has_edge((x, y), (x-1, y-1)):
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.25, voronoi_cell_center_y - 0.75))
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.75, voronoi_cell_center_y - 0.25))
        elif similarity_graph.has_edge((x, y - 1), (x - 1, y)):
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.25, voronoi_cell_center_y - 0.25))
        else:
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.5, voronoi_cell_center_y - 0.5))

        # top
        voronoi_cell_vertices.append((voronoi_cell_center_x, voronoi_cell_center_y - 0.5))


        similarity_graph.nodes[(x, y)]['voronoi_cell_vertices'] = voronoi_cell_vertices