from flask import Flask, request, render_template_string, jsonify
import random

app = Flask(__name__)

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

solver = None

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Maze Solver</title>
    <h1>Maze Solver</h1>
    <form method="post" action="/generate">
        <label for="width">Width:</label>
        <input type="range" id="width" name="width" min="10" max="50" value="20" oninput="this.nextElementSibling.value = this.value">
        <output>20</output><br>
        <label for="height">Height:</label>
        <input type="range" id="height" name="height" min="10" max="30" value="10" oninput="this.nextElementSibling.value = this.value">
        <output>10</output><br>
        <button type="submit">Generate Maze</button>
    </form>
    '''


@app.route('/generate', methods=['POST'])
def generate():
    global solver
    width = int(request.form.get("width", 21))
    height = int(request.form.get("height", 21))
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    maze = generate_solvable_maze(width, height)
    solver = MazeSolver(maze)
    maze_html = render_maze(maze)
    return render_template_string('''
    <!doctype html>
    <title>Maze Solver</title>
    <h1>Generated Maze</h1>
    <div id="maze">{{ maze_html|safe }}</div>
    <div id="message"></div>
    <button onclick="generateNew()">Generate New Maze</button>
    <script>
        async function solveMaze() {
            while (true) {
                const response = await fetch('/solve-step');
                const data = await response.json();
                if (data.status === "solved") {
                    document.getElementById("message").innerText = "Maze solved!";
                    break;
                }
                if (data.status === "no solution") {
                    document.getElementById("message").innerText = "No solution found!";
                    break;
                }
                document.getElementById("maze").innerHTML = data.html;
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }
        function generateNew() {
            window.location = "/";
        }
        solveMaze(); // Automatically start solving
    </script>
    ''', maze_html=maze_html)


@app.route('/solve-step')
def solve_step():
    global solver
    if solver is None:
        return jsonify({"status": "no maze"})

    result = solver.solve_step()
    if result == "solved":
        maze_html = render_maze(solver.maze, solver.path)
        return jsonify({"status": "solved", "html": maze_html})
    elif result is None:
        return jsonify({"status": "no solution"})
    else:
        maze_html = render_maze(solver.maze, solver.path)
        return jsonify({"status": "in progress", "html": maze_html})


def render_maze(maze, path=None):
    maze_copy = [row.copy() for row in maze]
    if path:
        for x, y in path:
            if maze_copy[y][x] not in ("S", "W"):
                maze_copy[y][x] = "*"

    return "<pre>" + "\n".join(
        ''.join(f'<span style="color:red;">*</span>' if cell == "*" else cell for cell in row)
        for row in maze_copy
    ) + "</pre>"


if __name__ == '__main__':
    app.run(debug=True)



