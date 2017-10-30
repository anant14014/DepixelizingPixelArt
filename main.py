import networkx as nx
from PIL import Image

if __name__ == "__main__":

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
            similarity_graph.add_node((i, j), pixel_value=pixels[i, j])

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
                else:
                    "Error! Block has abnormal number of edges"






