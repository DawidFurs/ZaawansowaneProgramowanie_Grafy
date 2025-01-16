from flask import Flask, request, render_template_string
import random

app = Flask(__name__)

def generate_solvable_maze(width, height):
    """
    Generates a solvable maze using recursive backtracking (DFS).
    """
    # Initialize maze with walls
    maze = [["#" for _ in range(width)] for _ in range(height)]

    # Define movement directions (down, up, right, left)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def is_valid_move(x, y):
        """
        Check if the cell can be carved out.
        """
        if 0 < x < width - 1 and 0 < y < height - 1:  # Inside boundaries
            # Count surrounding walls
            walls = sum(1 for dx, dy in directions if maze[y + dy][x + dx] == "#")
            return walls >= 3
        return False

    def carve_path(x, y):
        """
        Recursively carve paths in the maze.
        """
        maze[y][x] = "."  # Mark the current cell as a path
        random.shuffle(directions)  # Randomize direction order
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy  # Move two cells in the chosen direction
            if is_valid_move(nx, ny):
                maze[y + dy][x + dx] = "."  # Open wall between cells
                carve_path(nx, ny)

    # Set start and exit points
    start_x, start_y = 1, 1
    exit_x, exit_y = width - 2, height - 2

    # Start carving paths
    carve_path(start_x, start_y)

    # Place start and exit explicitly
    maze[start_y][start_x] = "S"  # Start
    maze[exit_y][exit_x] = "W"  # Exit

    # Ensure there's a path leading to the exit
    if maze[exit_y - 1][exit_x] == "#":
        maze[exit_y - 1][exit_x] = "."

    # Add termination line
    maze.append(["*"])
    return maze

def maze_to_ascii(maze):
    """
    Converts the maze list to ASCII string.
    """
    return "\n".join("".join(row) for row in maze)

@app.route('/')
def home():
    return '''
    <!doctype html>
    <title>Maze Generator</title>
    <h1>Maze Generator</h1>
    <form method="post" action="/generate">
        <label for="width">Width:</label>
        <input type="range" id="width" name="width" min="10" max="50" value="20" oninput="this.nextElementSibling.value = this.value">
        <output>20</output><br>
        <label for="height">Height:</label>
        <input type="range" id="height" name="height" min="10" max="30" value="10" oninput="this.nextElementSibling.value = this.value">
        <output>10</output><br>
        <input type="submit" value="Generate Solvable Maze">
    </form>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    try:
        width = int(request.form.get("width", 20))
        height = int(request.form.get("height", 10))

        # Ensure odd dimensions for proper maze generation
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1

        # Generate the maze
        maze = generate_solvable_maze(width, height)
        ascii_maze = maze_to_ascii(maze)

        return render_template_string('''
            <!doctype html>
            <title>Generated Maze</title>
            <h1>Your Maze</h1>
            <pre>{{ ascii_maze }}</pre>
            <form action="/">
                <button type="submit">Generate Another</button>
            </form>
        ''', ascii_maze=ascii_maze)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
