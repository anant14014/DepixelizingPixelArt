import networkx as nx
from PIL import Image
import heuristics
import visualizations
import color_utils
import itertools
from keys import *
import os

# I/O
input_filename = 'input_images/smw_boo_input.png'
output_directory = './outputs'
output_filename = output_directory + '/boo.svg'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
scale = 10

# Load Image
img_rgb = Image.open(input_filename)
img_yuv = img_rgb.convert('YCbCr')
pixels_rgb = img_rgb.load()
pixels_yuv = img_yuv.load()

#Create graph
similarity_graph = nx.Graph()

#TODO: check channels, range, other error possibilities (for the below 2 steps)

#Add nodes
for i in range(img_yuv.width):
    for j in range(img_yuv.height):
        similarity_graph.add_node((i, j))
        similarity_graph.nodes[(i, j)][YUV_VALUE] = pixels_yuv[i, j]
        similarity_graph.nodes[(i, j)][RGB_VALUE] = pixels_rgb[i, j]

#Add edges
for i in range(img_yuv.width):
    for j in range(img_yuv.height):
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
                color_current = similarity_graph.nodes[current_node][YUV_VALUE]
                color_neighbour = similarity_graph.nodes[neighbour_node][YUV_VALUE]
                if not color_utils.is_different(color_current, color_neighbour):
                    similarity_graph.add_edge(current_node, neighbour_node)

#visualizations.draw_graph(similarity_graph, "Before Removing Diagonals")

#Remove diagonals from fully-connected blocks
for i in range(img_yuv.width - 1):
    for j in range(img_yuv.height - 1):
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
                similarity_graph[(i, j)][(i + 1, j + 1)][HEURISTICS_SCORE] = 0
                similarity_graph[(i + 1, j)][(i, j + 1)][HEURISTICS_SCORE] = 0
                heuristics.curve_heuristic(similarity_graph, i, j)
                heuristics.sparsity_heuristic(similarity_graph, i, j)
                heuristics.island_heuristic(similarity_graph, i, j)
                if similarity_graph[(i, j)][(i + 1, j + 1)][HEURISTICS_SCORE] > similarity_graph[(i + 1, j)][(i, j + 1)][HEURISTICS_SCORE]:
                    similarity_graph.remove_edge((i + 1, j), (i, j + 1))
                else:
                    similarity_graph.remove_edge((i, j), (i + 1, j + 1))
            else:
                "Error! Block has abnormal number of edges"

# visualizations.draw_graph(similarity_graph, "After Removing Diagonals")

# voronoi cells
for x in range(img_yuv.width):
    for y in range(img_yuv.height):

        voronoi_cell_center_x = x + 0.5
        voronoi_cell_center_y = y + 0.5

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

        similarity_graph.nodes[(x, y)][VORONOI_CELL_VERTICES] = voronoi_cell_vertices
        #print voronoi_cell_vertices

#visualizations.render_as_pygame_screen(similarity_graph, img_yuv.width, img_yuv.height, scale, "Voronoi Before Removing Valence 2")

# calculate valencies of voronoi cell vertices
valency = {}
for i in range(img_yuv.width):
    for j in range(img_yuv.height):
        voronoi_cell_vertices = similarity_graph.nodes[(i, j)][VORONOI_CELL_VERTICES]
        for vertex in voronoi_cell_vertices:
            if vertex in valency:
                valency[vertex] = valency[vertex] + 1
            else:
                valency[vertex] = 1

# remove valency-2 voronoi points
for i in range(img_yuv.width):
    for j in range(img_yuv.height):
        voronoi_cell_vertices = similarity_graph.nodes[(i, j)][VORONOI_CELL_VERTICES]
        for vertex in voronoi_cell_vertices:
            x = vertex[0]
            y = vertex[1]
            if x != 0 and x != img_yuv.width and y != 0 and y != img_yuv.height:
                if valency[vertex] == 2:
                    voronoi_cell_vertices.remove(vertex)

#visualizations.render_as_pygame_screen(similarity_graph, img_yuv.width, img_yuv.height, scale, "Voronoi After Removing Valence 2")


num_iterations = 4
num_different_colors_threshold = 3
diagonal_length_threshold = 0.8
for iteration in range(num_iterations):
    # build voronoi graph
    voronoi_graph = nx.Graph()
    for i in range(img_yuv.width):
        for j in range(img_yuv.height):
            voronoi_cell_vertices = similarity_graph.nodes[(i, j)][VORONOI_CELL_VERTICES]
            for l in range(len(voronoi_cell_vertices)):
                r = (l + 1) % len(voronoi_cell_vertices)
                v1 = voronoi_cell_vertices[l]
                v2 = voronoi_cell_vertices[r]
                if voronoi_graph.has_edge(v1, v2):
                    voronoi_graph.edges[(v1, v2)][BELONGS_TO].append((i, j))
                else:
                    voronoi_graph.add_edge(v1, v2)
                    voronoi_graph.edges[(v1, v2)][BELONGS_TO] = [(i, j)]

    # mark junctions in voronoi graph
    for node in voronoi_graph.nodes:
        adjacent_cell_colors = set([])
        edges = voronoi_graph.edges(node)
        for edge in edges:
            belongs_to = voronoi_graph.edges[edge][BELONGS_TO]
            for cell_center in belongs_to:
                cell_color = similarity_graph.nodes[cell_center][YUV_VALUE]
                adjacent_cell_colors.add(cell_color)
        adjacent_cell_color_pairs = set(itertools.combinations(adjacent_cell_colors, 2))
        num_different_colors = 0
        for pair in adjacent_cell_color_pairs:
            if color_utils.is_different(pair[0], pair[1]):
                num_different_colors = num_different_colors + 1
        if num_different_colors > num_different_colors_threshold:
            voronoi_graph.nodes[node][IS_JUNCTION] = True
        else:
            voronoi_graph.nodes[node][IS_JUNCTION] = False

    # chaikin's method (b-splines)
    for node in similarity_graph.nodes:
        P = similarity_graph.nodes[node][VORONOI_CELL_VERTICES]
        Q_R = []
        i = 0
        for i in range(len(P)):
            p_l = P[i]
            p_r = P[(i + 1) % len(P)]
            is_p_l_junction = voronoi_graph.nodes[p_l][IS_JUNCTION]
            is_p_r_junction = voronoi_graph.nodes[p_r][IS_JUNCTION]
            shouldSmooth = False
            cell_centers = voronoi_graph.edges[(p_l, p_r)][BELONGS_TO]
            if (len(cell_centers) == 2) and (not is_p_l_junction) and (not is_p_r_junction):
                color_1 = similarity_graph.nodes[cell_centers[0]][YUV_VALUE]
                color_2 = similarity_graph.nodes[cell_centers[1]][YUV_VALUE]
                if color_utils.is_different(color_1, color_2):
                    shouldSmooth = True
            if shouldSmooth:
                factor_1 = 0.75
                factor_2 = 1.0 - factor_1
                diagonal_length = visualizations.distance(p_l, p_r)
                if diagonal_length > diagonal_length_threshold:
                    factor_1 = (1.0/8.0)
                    factor_2 = 1.0 - factor_1
                q_i = (factor_1*p_l[0] + factor_2*p_r[0], factor_1*p_l[1] + factor_2*p_r[1])
                r_i = (factor_2*p_l[0] + factor_1*p_r[0], factor_2*p_l[1] + factor_1*p_r[1])
                Q_R.append(q_i)
                Q_R.append(r_i)
            else:
                if p_l not in Q_R:
                    Q_R.append(p_l)
                if p_r not in Q_R:
                    Q_R.append(p_r)
        similarity_graph.nodes[node][VORONOI_CELL_VERTICES] = Q_R

#visualizations.render_as_pygame_screen(similarity_graph, img_yuv.width, img_yuv.height, scale, "Voronoi After Chaikin")
visualizations.render_as_svg(similarity_graph, img_yuv.width, img_yuv.height, scale, output_filename)