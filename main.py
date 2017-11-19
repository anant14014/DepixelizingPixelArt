import networkx as nx
from PIL import Image
import heuristics
import visualizations
import color


# I/O
filename = 'input_images/smw_dolphin_input.png'
img = Image.open(filename)
img = img.convert('YCbCr')
pixels = img.load()

#Create graph
similarity_graph = nx.Graph()

#TODO: check channels, range, other error possibilities (for the below 2 steps)

#Add nodes
for i in range(img.width):
    for j in range(img.height):
        similarity_graph.add_node((i, j), pixel_value=pixels[i, j])

#Add edges
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
                color_current = similarity_graph.nodes[current_node]['pixel_value']
                color_neighbour = similarity_graph.nodes[neighbour_node]['pixel_value']
                if not color.is_different(color_current, color_neighbour):
                    similarity_graph.add_edge(current_node, neighbour_node)

#visualizations.draw_graph(similarity_graph, "Before Removing Diagonals")

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
                heuristics.curve_heuristic(similarity_graph, i, j)
                heuristics.sparsity_heuristic(similarity_graph, i, j)
                heuristics.island_heuristic(similarity_graph, i, j)
                #print similarity_graph[(i, j)][(i + 1, j + 1)]['score']
                #print similarity_graph[(i + 1, j)][(i, j + 1)]['score']
                if similarity_graph[(i, j)][(i + 1, j + 1)]['score'] > similarity_graph[(i + 1, j)][(i, j + 1)]['score']:
                    similarity_graph.remove_edge((i + 1, j), (i, j + 1))
                else:
                    similarity_graph.remove_edge((i, j), (i + 1, j + 1))
            else:
                "Error! Block has abnormal number of edges"

# visualizations.draw_graph(similarity_graph, "After Removing Diagonals")

# voronoi cells
for x in range(img.width):
    for y in range(img.height):

        voronoi_cell_center_x = x + 0.5
        voronoi_cell_center_y = y + 0.5

        similarity_graph.nodes[(x, y)]['voronoi_cell_center'] = (voronoi_cell_center_x, voronoi_cell_center_y)

        voronoi_cell_vertices = []

        # top left
        if similarity_graph.has_edge((x, y), (x - 1, y - 1)):
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.25, voronoi_cell_center_y - 0.75))
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.75, voronoi_cell_center_y - 0.25))
        elif similarity_graph.has_edge((x, y - 1), (x - 1, y)):
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.25, voronoi_cell_center_y - 0.25))
        else:
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.5, voronoi_cell_center_y - 0.5))

        # left
        voronoi_cell_vertices.append((voronoi_cell_center_x - 0.5, voronoi_cell_center_y))

        # bottom left
        if similarity_graph.has_edge((x, y), (x - 1, y + 1)):
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.75, voronoi_cell_center_y + 0.25))
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.25, voronoi_cell_center_y + 0.75))
        elif similarity_graph.has_edge((x, y + 1), (x - 1, y)):
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.25, voronoi_cell_center_y + 0.25))
        else:
            voronoi_cell_vertices.append((voronoi_cell_center_x - 0.5, voronoi_cell_center_y + 0.5))

        # bottom
        voronoi_cell_vertices.append((voronoi_cell_center_x, voronoi_cell_center_y + 0.5))

        # bottom right
        if similarity_graph.has_edge((x, y), (x + 1, y + 1)):
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.25, voronoi_cell_center_y + 0.75))
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.75, voronoi_cell_center_y + 0.25))
        elif similarity_graph.has_edge((x, y + 1), (x + 1, y)):
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.25, voronoi_cell_center_y + 0.25))
        else:
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.5, voronoi_cell_center_y + 0.5))

        # right
        voronoi_cell_vertices.append((voronoi_cell_center_x + 0.5, voronoi_cell_center_y))

        # top right
        if similarity_graph.has_edge((x, y), (x + 1, y - 1)):
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.75, voronoi_cell_center_y - 0.25))
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.25, voronoi_cell_center_y - 0.75))
        elif similarity_graph.has_edge((x, y - 1), (x + 1, y)):
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.25, voronoi_cell_center_y - 0.25))
        else:
            voronoi_cell_vertices.append((voronoi_cell_center_x + 0.5, voronoi_cell_center_y - 0.5))

        # top
        voronoi_cell_vertices.append((voronoi_cell_center_x, voronoi_cell_center_y - 0.5))

        similarity_graph.nodes[(x, y)]['voronoi_cell_vertices'] = voronoi_cell_vertices
        #print voronoi_cell_vertices

scale = 20
visualizations.draw_voronoi(similarity_graph, img.width, img.height, scale, "Voronoi Before Removing Valence 2")

# calculate valencies of voronoi cell vertices
valency = {}
for i in range(img.width):
    for j in range(img.height):
        voronoi_cell_vertices = similarity_graph.nodes[(i, j)]['voronoi_cell_vertices']
        for vertex in voronoi_cell_vertices:
            if vertex in valency:
                valency[vertex] = valency[vertex] + 1
            else:
                valency[vertex] = 1

# remove valency-2 voronoi points
for i in range(img.width):
    for j in range(img.height):
        voronoi_cell_vertices = similarity_graph.nodes[(i, j)]['voronoi_cell_vertices']
        for vertex in voronoi_cell_vertices:
            x = vertex[0]
            y = vertex[1]
            if x != 0 and x != img.width and y != 0 and y != img.height:
                if valency[vertex] == 2:
                    voronoi_cell_vertices.remove(vertex)

visualizations.draw_voronoi(similarity_graph, img.width, img.height, scale, "Voronoi After Removing Valence 2")




# build voronoi graph
voronoi_graph = nx.Graph()
for i in range(img.width):
    for j in range(img.height):
        voronoi_cell_vertices = similarity_graph.nodes[(i, j)]['voronoi_cell_vertices']
        for l in range(len(voronoi_cell_vertices)):
            r = (l + 1)%len(voronoi_cell_vertices)
            v1 = voronoi_cell_vertices[l]
            v2 = voronoi_cell_vertices[r]
            if voronoi_graph.has_edge(v1, v2):
                voronoi_graph.edges[(v1, v2)]['belongs_to'].append((i, j))
            else:
                voronoi_graph.add_edge(v1, v2)
                voronoi_graph.edges[(v1, v2)]['belongs_to'] = [(i, j)]


# chaikin's method (equivalent to b-splines)
for node in similarity_graph.nodes:
    P = similarity_graph.nodes[node]['voronoi_cell_vertices']
    Q_R = []
    i = 0
    for i in range(len(P)):
        p_l = P[i]
        p_r = P[(i + 1)%len(P)]
        shouldSmooth = False
        cell_centers = voronoi_graph.edges[(p_l, p_r)]['belongs_to']
        if (len(cell_centers) == 2):
            color_1 = similarity_graph.nodes[cell_centers[0]]['pixel_value']
            color_2 = similarity_graph.nodes[cell_centers[1]]['pixel_value']
            if color.is_different(color_1, color_2):
                shouldSmooth = True
        if shouldSmooth:
            q_i = (0.75 * p_l[0] + 0.25 * p_r[0], 0.75 * p_l[1] + 0.25 * p_r[1])
            r_i = (0.25 * p_l[0] + 0.75 * p_r[0], 0.25 * p_l[1] + 0.75 * p_r[1])
            Q_R.append(q_i)
            Q_R.append(r_i)
        else:
            if p_l not in Q_R:
                Q_R.append(p_l)
            if p_r not in Q_R:
                Q_R.append(p_r)
    similarity_graph.nodes[node]['voronoi_cell_vertices'] = Q_R

visualizations.draw_voronoi(similarity_graph, img.width, img.height, scale, "Voronoi After Chaikin")