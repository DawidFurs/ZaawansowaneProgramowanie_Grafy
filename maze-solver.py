import random

# Reprezentacja ruchów w 4 strony (dół, góra, prawo, lewo)
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def generate_solvable_maze(width, height):  # Generacja labiryntu o zadanym rozwmiarze (szerokość, wysokość)
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


# Test
width = 10
height = 10
maze_test = generate_solvable_maze(width, height)

# Test generacji labiryntu
for x in range(0, height):
    print(maze_test[x])



