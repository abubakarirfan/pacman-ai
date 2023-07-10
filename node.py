from heapq import heappush, heappop


class Node:
    def __init__(self, coordinates, parent=None):
        self.coordinates = coordinates
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.coordinates == other.coordinates

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash(self.coordinates)


def astar(maze, start, end):
    start_node = Node(start)
    end_node = Node(end)

    open_list = []
    closed_list = set()

    heappush(open_list, (start_node.f, start_node))

    while open_list:
        current_node = heappop(open_list)[1]

        closed_list.add(current_node)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.coordinates)
                current = current.parent
            return path[::-1]

        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.coordinates[0] + new_position[0], current_node.coordinates[1] + new_position[1])

            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            if maze[node_position[0]][node_position[1]] != 1:
                continue

            new_node = Node(node_position, current_node)

            if new_node in closed_list:
                continue

            new_node.g = current_node.g + 1
            new_node.h = ((new_node.coordinates[0] - end_node.coordinates[0]) ** 2) + ((new_node.coordinates[1] - end_node.coordinates[1]) ** 2)
            new_node.f = new_node.g + new_node.h

            for i, (f, node) in enumerate(open_list):
                if node == new_node and f > new_node.f:
                    open_list[i] = (new_node.f, new_node)
                    break
            else:
                heappush(open_list, (new_node.f, new_node))

