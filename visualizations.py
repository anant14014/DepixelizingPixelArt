import pygame
import matplotlib.pyplot as plt

def draw_graph(graph, title):
    plt.figure()
    plt.title(title)
    x = [node[0] for node in graph.nodes()]
    y = [node[1] for node in graph.nodes()]
    plt.scatter(y,x)
    for edge in graph.edges():
        plt.plot([edge[0][1],edge[1][1]],[edge[0][0],edge[1][0]])
    plt.show()

def draw_voronoi(graph, width, height, scale, title):
    pygame.init()
    WHITE = (255, 255, 255)
    size = (width*scale, height*scale)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(title)
    done = False
    clock = pygame.time.Clock()
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
        screen.fill(WHITE)
        #pygame.draw.polygon(screen, BLACK, [[0, 0], [10, 0], [10, 10], [0, 10]])
        for i in range(width):
            for j in range(height):
                voronoi_cell_vertices = graph.nodes[(i, j)]['voronoi_cell_vertices']
                vertices = []
                for vertex in voronoi_cell_vertices:
                    vertices.append([vertex[0]*scale, vertex[1]*scale])
                color = graph.nodes[(i, j)]['pixel_value']
                pygame.draw.polygon(screen, color, vertices)
        pygame.display.flip()
        clock.tick(60)
    # Be IDLE friendly
    pygame.quit()