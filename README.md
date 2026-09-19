# Thief Detection using Constraint Satisfaction Problems (CSP)

A Python-based simulation system for detecting thieves using sensor networks and Constraint Satisfaction Problems. This project implements an intelligent detection system where thieves are frozen when detected by multiple sensors across different time groups.

## Features

- **Interactive GUI**: Manual placement of sensors, thieves, walls, and exits on a 20x20 grid
- **Real-time Simulation**: Watch thieves navigate through the grid towards exits
- **CSP-based Detection**: Uses Constraint Satisfaction Problems to determine when a thief should be frozen
- **Customizable Parameters**: Adjustable detection thresholds and group requirements
- **Visual Feedback**: Color-coded elements and detection arrows for clear visualization

## How It Works

The system uses a CSP-based detection algorithm with the following logic:

1. **K-Detection Rule**: A thief must be detected by at least K sensors in a single time step
2. **C-Groups Rule**: The thief must achieve K-detection in C different time groups
3. **Freezing Condition**: When both conditions are met, the thief is frozen and can no longer move

### Detection Parameters

- `K_DETECTION = 3`: Minimum number of sensors required to detect a thief in one time step
- `C_GROUPS = 3`: Number of different time groups required for freezing
- `SENSOR_RADIUS = 2`: Detection range of each sensor
- `COMM_RADIUS = 2`: Communication range between sensors

## Installation

### Prerequisites

- Python 3.6 or higher
- tkinter (usually included with Python)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Mahsa-Arjmand/Thief-detection-csp.git
cd Thief-detection-csp
```

2. Install required dependencies:
```bash
pip install python-constraint
```

## Usage

1. Run the main script:
```bash
python theif-detection.py
```

2. **Placement Phase**:
   - Select "Sensor" mode and click on the grid to place sensors (green circles)
   - Select "Thief" mode and place thieves (red circles)
   - Select "Wall" mode to place obstacles (black squares)
   - Select "Exit" mode to place exit points (blue squares)
   - Click "Start Simulation" when ready

3. **Simulation Phase**:
   - Watch thieves navigate towards exits using pathfinding
   - Thieves are detected when within sensor radius
   - Orange arrows show which sensors detected each thief
   - Thieves turn gray when frozen by the CSP algorithm
   - Thieves turn green when they successfully escape

## Algorithm Details

### CSP Detection System

The Constraint Satisfaction Problem approach ensures reliable detection by:

1. **Variable Assignment**: Each time group is assigned a time step index
2. **Domain Constraints**: Time steps must have sufficient sensor detections (≥ K)
3. **AllDifferent Constraint**: Each group must use a different time step
4. **Solution Validation**: A valid solution with C groups triggers freezing

### Pathfinding

Thieves use BFS (Breadth-First Search) to find the shortest path to exits while avoiding:
- Walls
- Sensor locations
- Grid boundaries

## Code Structure

- `PlacementApp`: Handles the initial manual placement phase
- `SensorNetworkGUI`: Manages the simulation and visualization
- `detect_thief()`: Identifies which sensors can detect a thief
- `csp_detect_freeze()`: Implements the CSP-based freezing logic
- `move_thief()`: Handles thief movement and pathfinding
- `blocked()`: Checks if walls block line-of-sight between sensors and thieves

## Customization

You can modify the constants at the top of the file to adjust behavior:

```python
CELL_SIZE = 30          # Size of each grid cell in pixels
GRID_WIDTH = 20         # Number of cells horizontally
GRID_HEIGHT = 20        # Number of cells vertically
SENSOR_RADIUS = 2       # Detection radius of sensors
COMM_RADIUS = 2         # Communication radius
K_DETECTION = 3         # Sensors needed for detection
C_GROUPS = 3            # Time groups needed for freezing
```

## Requirements

- Python 3.6+
- python-constraint library
- tkinter (GUI library)

## License

This project is provided as-is for educational and research purposes.

## Author

Developed as a CSP-based detection system for sensor networks.
