import tkinter as tk
from tkinter import messagebox
from collections import deque
import math
try:
    from constraint import Problem, AllDifferentConstraint
except ImportError:
    messagebox.showerror("Missing Dependency", "Please install the 'python-constraint' library using 'pip install python-constraint'")
    exit(1)

CELL_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
SENSOR_RADIUS = 2
COMM_RADIUS = 2
K_DETECTION = 3
C_GROUPS = 3

class PlacementApp:
    def __init__(self, master):
        self.master = master
        self.master.title("WST Manual Placement")
        self.canvas = tk.Canvas(master, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE)
        self.canvas.pack()
        self.mode = tk.StringVar(value="Sensor")
        self.positions = {"Sensor": [], "Thief": [], "Wall": [], "Exit": []}
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.place_item)
        modes = ["Sensor", "Thief", "Wall", "Exit"]
        for i, label in enumerate(modes):
            tk.Radiobutton(master, text=label, variable=self.mode, value=label).pack(side="left")
        tk.Button(master, text="Start Simulation", command=self.start_simulation).pack(side="right")

    def draw_grid(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    outline="lightgray"
                )

    def place_item(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        mode = self.mode.get()
        if (x, y) in sum(self.positions.values(), []):
            return
        colors = {
            "Sensor": ("limegreen", lambda: self.canvas.create_oval(
                x * CELL_SIZE + 8, y * CELL_SIZE + 8,
                (x + 1) * CELL_SIZE - 8, (y + 1) * CELL_SIZE - 8, fill="limegreen")),
            "Thief": ("red", lambda: self.canvas.create_oval(
                x * CELL_SIZE + 5, y * CELL_SIZE + 5,
                (x + 1) * CELL_SIZE - 5, (y + 1) * CELL_SIZE - 5, fill="red")),
            "Wall": ("black", lambda: self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill="black")),
            "Exit": ("dodgerblue", lambda: self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, fill="dodgerblue"))
        }
        colors[mode][1]()
        self.positions[mode].append((x, y))

    def start_simulation(self):
        if not self.positions["Sensor"] or not self.positions["Thief"] or not self.positions["Exit"]:
            messagebox.showerror("Missing Input", "You must place at least 1 Sensor, Thief, and Exit.")
            return
        self.master.destroy()
        root = tk.Tk()
        params = {
            "sensors": self.positions["Sensor"],
            "thieves": self.positions["Thief"],
            "walls": self.positions["Wall"],
            "exits": self.positions["Exit"]
        }
        SensorNetworkGUI(root, params)
        root.mainloop()

class SensorNetworkGUI:
    def __init__(self, root, params):
        self.root = root
        self.root.title("Sensor Network Simulation (CSP Detection)")
        self.sensors = params["sensors"]
        self.thieves = [list(p) for p in params["thieves"]]
        self.walls = params["walls"]
        self.exits = params["exits"]
        self.k_detections = [[] for _ in self.thieves]
        self.frozen = [False] * len(self.thieves)
        self.escaped = [False] * len(self.thieves)
        self.detection_history = [[] for _ in self.thieves]  # Store sensor IDs per time step

        self.canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE)
        self.canvas.pack()
        self.status = self.canvas.create_text(10, 10, anchor="nw", fill="navy", font=("Arial", 12))
        self.draw_grid()
        self.draw_static()
        self.canvas.create_text(200, 200, text="Initializing...", tag="loading")
        self.root.after(100, self.update)

    def draw_grid(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    outline="gainsboro"
                )

    def draw_static(self):
        for idx, (x, y) in enumerate(self.sensors):
            self.canvas.create_oval(
                (x - SENSOR_RADIUS) * CELL_SIZE,
                (y - SENSOR_RADIUS) * CELL_SIZE,
                (x + SENSOR_RADIUS + 1) * CELL_SIZE,
                (y + SENSOR_RADIUS + 1) * CELL_SIZE,
                outline="honeydew", dash=(2, 4)
            )
            self.canvas.create_oval(
                x * CELL_SIZE + 8, y * CELL_SIZE + 8,
                (x + 1) * CELL_SIZE - 8, (y + 1) * CELL_SIZE - 8,
                fill="limegreen"
            )
        for x, y in self.walls:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill="black"
            )
        for x, y in self.exits:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill="dodgerblue"
            )

    def draw_thief(self, idx, color):
        x, y = self.thieves[idx]
        self.canvas.create_oval(
            x * CELL_SIZE + 5, y * CELL_SIZE + 5,
            (x + 1) * CELL_SIZE - 5, (y + 1) * CELL_SIZE - 5,
            fill=color, tags="thief"
        )

    def draw_detection_arrows(self, thief_idx, sensor_ids):
        tx, ty = self.thieves[thief_idx]
        for sensor_id in sensor_ids:
            sx, sy = self.sensors[sensor_id]
            self.canvas.create_line(
                sx * CELL_SIZE + 15, sy * CELL_SIZE + 15,
                tx * CELL_SIZE + 15, ty * CELL_SIZE + 15,
                fill="orange", arrow=tk.LAST, tags="arrow"
            )

    def move_thief(self, idx):
        if self.frozen[idx]:
            return True

        start = tuple(self.thieves[idx])
        if start in self.exits:
            return False

        queue = deque([(start, [])])
        visited = set()

        while queue:
            pos, path = queue.popleft()
            if pos in visited:
                continue
            visited.add(pos)

            if pos in self.exits:
                if path:
                    self.thieves[idx] = list(path[0])
                return True

            x, y = pos
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and
                        (nx, ny) not in self.walls and
                        (nx, ny) not in self.sensors):
                    queue.append(((nx, ny), path + [(nx, ny)]))
        return False

    def detect_thief(self, idx):
        tx, ty = self.thieves[idx]
        sensor_ids = []
        for i, (sx, sy) in enumerate(self.sensors):
            if (abs(sx - tx) <= SENSOR_RADIUS and
                abs(sy - ty) <= SENSOR_RADIUS and
                not self.blocked(sx, sy, tx, ty)):
                sensor_ids.append(i)
        return sensor_ids

    def blocked(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        while True:
            if (x1, y1) in self.walls:
                return True
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy
        return False

    def csp_detect_freeze(self, idx):
        # Store current time step's detections
        sensor_ids = self.detect_thief(idx)
        self.detection_history[idx].append(sensor_ids)

        # Debug: Print detection history for this thief
        print(f"Thief {idx+1} detection history: {self.detection_history[idx]}")

        # If not enough time steps yet, can't freeze
        if len(self.detection_history[idx]) < C_GROUPS:
            print(f"Thief {idx+1}: Not enough time steps ({len(self.detection_history[idx])}/{C_GROUPS})")
            return False, sensor_ids

        # Set up CSP problem
        problem = Problem()

        # Variables: One for each group (up to C_GROUPS), representing time steps with detections
        for group in range(C_GROUPS):
            # Domain: indices of time steps in detection_history, or -1 if no detection
            possible_steps = list(range(len(self.detection_history[idx]))) + [-1]
            problem.addVariable(f"group_{group}", possible_steps)

        # Constraint 1: If a group is assigned a time step (not -1), it must have >= K_DETECTION sensors
        def valid_detection(group_time):
            if group_time == -1:
                return True
            return len(self.detection_history[idx][group_time]) >= K_DETECTION

        for group in range(C_GROUPS):
            problem.addConstraint(valid_detection, [f"group_{group}"])

        # Constraint 2: All assigned time steps must be different (or -1)
        problem.addConstraint(AllDifferentConstraint(), [f"group_{group}" for group in range(C_GROUPS)])

        # Solve CSP
        solutions = problem.getSolutions()
        print(f"Thief {idx+1}: CSP solutions found: {len(solutions)}")

        # Check if any solution satisfies C_GROUPS detections
        for solution in solutions:
            valid_groups = sum(1 for g in range(C_GROUPS) if solution[f"group_{g}"] != -1)
            if valid_groups >= C_GROUPS:
                print(f"Thief {idx+1}: Frozen by CSP (solution: {solution})")
                return True, sensor_ids

        print(f"Thief {idx+1}: Not frozen, insufficient groups")
        return False, sensor_ids

    def update(self):
        self.canvas.delete("thief", "arrow", "loading")
        status = [f"Detection Rules: K={K_DETECTION} sensors/group, C={C_GROUPS} groups\n"]

        for i in range(len(self.thieves)):
            if self.escaped[i]:
                status.append(f"Thief {i+1}: 🚪 Escaped")
                self.draw_thief(i, "green")
                continue

            if self.frozen[i]:
                status.append(f"Thief {i+1}: ❄️ FROZEN (K=" + "+".join(map(str, self.k_detections[i])) + f", C={len(self.k_detections[i])}/{C_GROUPS})")
                self.draw_thief(i, "gray")
                continue

            if not self.move_thief(i):
                self.escaped[i] = True
                status.append(f"Thief {i+1}: 🚪 Escaped")
                self.draw_thief(i, "green")
                continue

            is_frozen, sensor_ids = self.csp_detect_freeze(i)
            if is_frozen:
                self.frozen[i] = True
                self.k_detections[i].append(len(sensor_ids))
                status.append(f"Thief {i+1}: ❄️ FROZEN (K=" + "+".join(map(str, self.k_detections[i])) + f", C={len(self.k_detections[i])}/{C_GROUPS})")
                self.draw_thief(i, "gray")
            else:
                if len(sensor_ids) >= K_DETECTION:
                    self.k_detections[i].append(len(sensor_ids))
                    status.append(f"Thief {i+1}: ⚠️ Detected (K={len(sensor_ids)}) (K=" + "+".join(map(str, self.k_detections[i])) + f", C={len(self.k_detections[i])}/{C_GROUPS})")
                else:
                    status.append(f"Thief {i+1}: 🏃 Moving freely")
                self.draw_thief(i, "red")

            if len(sensor_ids) >= K_DETECTION:
                self.draw_detection_arrows(i, sensor_ids)

        self.canvas.itemconfig(self.status, text="\n".join(status))

        if not all(f or e for f, e in zip(self.frozen, self.escaped)):
            self.root.after(1000, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlacementApp(root)
    root.mainloop()