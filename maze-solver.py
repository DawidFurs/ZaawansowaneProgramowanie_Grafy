import random

# Reprezentacja ruchów w 4 strony (dół, góra, prawo, lewo)
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def generate_solvable_maze(width, height):  # Generacja labiryntu o zadanym rozmiarze (szerokość, wysokość)
    maze = [["#" for _ in range(width)] for _ in range(height)]  # Utworzenie siatki wypełnionej ścianami

    def is_valid_move(x, y):  # Walidacja ruchu
        if 0 < x < width - 1 and 0 < y < height - 1:  # jeśli jest wewnątrz labiryntu (z dala od ściany)
            walls = sum(1 for dx, dy in directions if maze[y + dy][x + dx] == "#") # Obliczenie liczby sąsiednich ścian punktu
            return walls >= 3  # Wymagane Min. 3 ściany sąsiadujące z punktem
        return False

    def carve_path(x, y):   #
        maze[y][x] = "."
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy
            if is_valid_move(nx, ny):
                maze[y + dy][x + dx] = "."
                carve_path(nx, ny)

    carve_path(1, 1)
    maze[1][1] = "S"
    maze[-2][-2] = "W"
    return maze

class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.path = []
        self.visited = set()
        self.stack = []
        self.start, self.end = self.find_points()
        self.stack.append((self.start, [self.start]))

    def find_points(self): # Odnajdowanie punktu startowego i końcowego
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == "S":
                    start = (x, y)
                elif cell == "W":
                    end = (x, y)
        return start, end

    def solve_step(self):   # Odnajdowanie ruchu
        if not self.stack:
            return None  # Brak rozwiązania

        (x, y), path = self.stack.pop()

        # Jeśli już odwiedzono, pomijamy
        if (x, y) in self.visited:
            return "in progress"

        # Oznaczenie jako odwiedzone
        self.visited.add((x, y))
        self.path = path

        # Sprawdzenie, czy znaleziono wyjście
        if (x, y) == self.end:
            return "solved"

        # Sortowanie kierunków według odległości do celu (priorytet ruchów bliżej celu)
        next_moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                dist = abs(self.end[0] - nx) + abs(self.end[1] - ny)
                next_moves.append(((nx, ny), dist))

        # Dodawanie ruchów do stosu (najbliższe ruchy najpierw)
        for (nx, ny), _ in sorted(next_moves, key=lambda move: move[1]):
            self.stack.append(((nx, ny), path + [(nx, ny)]))

        return "in progress"

    def is_valid_move(self, x, y):
        return (
                0 <= x < len(self.maze[0]) and
                0 <= y < len(self.maze) and
                self.maze[y][x] in (".", "W") and
                (x, y) not in self.visited
        )

# Test - maze generator
width = 15
height = 15
maze_test = generate_solvable_maze(width, height)

for x in range(0, height):
    print(maze_test[x])



