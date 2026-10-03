# testbed_navigation — ROS2 Nav2 Navigation Package

## Overview

This package implements a complete, **Nav2-plugin-based navigation workflow** for the **Testbed-T1.0.0** robot without relying on the monolithic `nav2_bringup` launch file. Each component of the navigation pipeline (map loading, localization, planning, control, recovery) is started explicitly so the system is transparent, easy to debug, and straightforward to extend.

---

## Repository Structure

```
testbed_navigation/
├── config/
│   ├── amcl_params.yaml       # AMCL localization parameters
│   └── nav2_params.yaml       # Full Nav2 stack parameters (planner, controller, etc.)
├── behavior_trees/
│   └── navigate_to_pose_w_replanning_and_recovery.xml  # Custom BT
├── launch/
│   ├── map_loader.launch.py   # Step 1 — load the occupancy-grid map
│   ├── localization.launch.py # Step 2 — AMCL particle-filter localization
│   └── navigation.launch.py  # Step 3 — full Nav2 stack
└── README.md                  # This file
```

---

## Plugins Used

| Component | Plugin / Package |
|---|---|
| Map server | `nav2_map_server` / `map_server` |
| Localization | `nav2_amcl` / `amcl` |
| Global planner | `nav2_navfn_planner` / `NavfnPlanner` (Dijkstra) |
| Local planner | `dwb_core` / `DWBLocalPlanner` |
| BT navigator | `nav2_bt_navigator` / `bt_navigator` |
| Recovery behaviours | `nav2_behaviors` — Spin, BackUp, Wait |
| Path smoother | `nav2_smoother` / `SimpleSmoother` |
| Velocity smoother | `nav2_velocity_smoother` / `velocity_smoother` |
| Collision monitor | `nav2_collision_monitor` / `collision_monitor` |
| Lifecycle manager | `nav2_lifecycle_manager` / `lifecycle_manager` |

---

## Prerequisites

- ROS 2 Humble
- Gazebo Classic 11.10.2
- Nav2 (`sudo apt install ros-humble-navigation2`)
- `colcon` build tool

### Recommended DDS (for Nav2 stability)

```bash
sudo apt install ros-humble-rmw-cyclonedds-cpp
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

## Build

```bash
mkdir -p ~/assignment_ws/src
cd ~/assignment_ws/src
git clone <your-fork-url>
cd ~/assignment_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Launch Sequence

Each step can be run **independently** in a separate terminal for debugging, or you can jump straight to Step 3 which includes all components.

### Step 1 — Start the simulation

```bash
ros2 launch testbed_bringup testbed_full_bringup.launch.py
```

This starts Gazebo with the testbed_playground world, spawns the robot, and launches Rviz.

### Step 2 — Load the map (optional standalone test)

```bash
ros2 launch testbed_navigation map_loader.launch.py
```

Verify in Rviz: add a **Map** display on topic `/map`. You should see the occupancy grid.

### Step 3 — Localization (optional standalone test)

```bash
ros2 launch testbed_navigation localization.launch.py
```

Verify in Rviz:
- Add a **PoseArray** display on topic `/particlecloud` to see AMCL particles.
- Use the **2D Pose Estimate** tool to set the initial pose if particles are scattered.

### Step 4 — Full navigation stack

```bash
ros2 launch testbed_navigation navigation.launch.py
```

Then send a navigation goal:
- In Rviz, use the **Nav2 Goal** (or **2D Nav Goal**) tool to click a target pose.
- Or via CLI: `ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose ...`

---

## Verification Commands

```bash
# Check all active nodes
ros2 node list

# List available actions (should include /navigate_to_pose)
ros2 action list

# Check TF tree
ros2 run tf2_tools view_frames

# Echo the map topic
ros2 topic echo /map --once

# Echo AMCL pose
ros2 topic echo /amcl_pose

# Echo laser scan
ros2 topic echo /scan
```

---

## Design Decisions & Approach

### Why NavFn (Dijkstra) for global planning?
The testbed environment is a small, fully-mapped box room. NavFn with Dijkstra guarantees finding an optimal path without the heuristic tuning overhead of A*. This is the safest choice for an assignment where verifying correctness is important.

### Why DWB for local control?
DWB (Dynamic Window Approach) is well-suited to differential-drive robots. Its `RotateToGoal` critic cleanly handles the final orientation alignment, and it is easy to tune via the `nav2_params.yaml` critics section.

### Why separate launch files?
Following the KISS principle (from `help.md`): testing each component in isolation (map → localization → navigation) makes debugging dramatically easier. If the map is wrong, you catch it before AMCL fails mysteriously.

### Lifecycle management
All Nav2 nodes are managed by `lifecycle_manager` with `autostart: true`. This is the standard Nav2 pattern — nodes start in UNCONFIGURED, the manager transitions them to ACTIVE. Without this, nav2 nodes publish nothing.

---

## Challenges & Solutions

| Challenge | Solution |
|---|---|
| Map not loading | Fixed `wrong_path_testbed_world.pgm` → `testbed_world.pgm` in `testbed_world.yaml` (Bug 1) |
| Robot description won't parse | Removed duplicate `>` in `testbed.gazebo` IMU plugin tag (Bug 2) |
| Package not found by downstream | Added `()` to `ament_package` call in `testbed_description/CMakeLists.txt` (Bug 3) |
| Robot spawns outside world | Changed spawn Y from 5.0 m to 0.0 m, Z to 0.05 m to avoid clipping (Bug 4) |
| Map files not found at runtime | Added `maps` to install targets in `testbed_bringup/CMakeLists.txt` (Bug 5) |

---

## Contact Information

- **Name:** Your Full Name
- **Contact Number:** Your contact number
- **Email:** your-email@example.com
