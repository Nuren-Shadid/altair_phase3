# altair_phase3
 
Project Altair Software Recruitment, Batch 24, Phase 3: **The Turtle Has Field Duty** (A Practical Introduction to ROS 2).
 
A ROS 2 Python package (`ament_python`) with four small programs:
 
| Task | What it does | Executable | Node name |
|---|---|---|---|
| 1 | Publishes simulated rover telemetry once per second | `telemetry_pub` | `mars_telemetry_publisher` |
| 1 | Subscribes, prints readings, warns when battery is below 25% | `telemetry_sub` | `mission_control_monitor` |
| 2a | Keyboard driving menu (P, R, Z, Q) for turtlesim | `driving_menu` | `driving_menu_node` |
| 3 | Three-waypoint mission with pause / resume | `mission_node` | `mission_node` |
 
Task 2b and Task 4 are explanations (video and notes only, no code). See the Drive folder.
 
## Environment
 
- Ubuntu 22.04
- ROS 2 Humble
- Python 3 (the one that ships with Ubuntu 22.04)
- A working GUI (turtlesim opens a window)
## Dependencies
 
ROS packages: `rclpy`, `std_msgs`, `geometry_msgs`, `turtlesim`, `std_srvs`, `launch`, `launch_ros`.
 
Install the simulator and the build tool once:
 
```bash
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-turtlesim python3-colcon-common-extensions
```
 
## Get the code and build
 
```bash
mkdir -p ~/altair_phase3_ws/src
cd ~/altair_phase3_ws/src
git clone <THIS_REPOSITORY_URL> altair_phase3
 
cd ~/altair_phase3_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select altair_phase3
```
 
The `build/`, `install/` and `log/` folders are generated and are not in this repository.
 
In **every new terminal**, source both setup files before running anything:
 
```bash
source /opt/ros/humble/setup.bash
source ~/altair_phase3_ws/install/setup.bash
```
 
## Task 1: Rover telemetry
 
Use two terminals.
 
```bash
# Terminal 1
ros2 run altair_phase3 telemetry_pub
 
# Terminal 2
ros2 run altair_phase3 telemetry_sub
```
 
- Topic: `/rover_telemetry`
- Message type: `std_msgs/msg/String` containing JSON
- Rate: 1 Hz
Fields and units:
 
| Field | Unit |
|---|---|
| `battery_pct` | percent |
| `temperature_c` | degrees Celsius |
| `wheel_speed_mps` | metres per second |
| `elapsed_s` | seconds since the publisher started |
 
The battery starts at 100% and drops by 2 per second, so the monitor prints `LOW BATTERY WARNING!` once it is below 25% (about 38 seconds in). The starting value and drop rate are set in `telemetry_pub.py`.
 
Check the rate:
 
```bash
ros2 topic hz /rover_telemetry
```
 
## Task 2a: Turtle driving menu
 
```bash
# Terminal 1
ros2 run turtlesim turtlesim_node
 
# Terminal 2 (keep this terminal focused, it reads single key presses)
ros2 run altair_phase3 driving_menu
```
 
Keys: `P` patrol, `R` rectangle, `Z` zigzag, `Q` stop and quit. Other keys are ignored. The node publishes `geometry_msgs/msg/Twist` to `/turtle1/cmd_vel` at 10 Hz. Turning uses `angular.z` in rad/s.
 
Reset the turtle between patterns if needed:
 
```bash
ros2 service call /reset std_srvs/srv/Empty "{}"
```
 
## Task 3: Three stops before cha
 
Close keyboard teleop and the Task 2a driving menu first. The mission node must be the only publisher on `/turtle1/cmd_vel`.
 
```bash
ros2 launch altair_phase3 field.launch.py
```
 
This one launch file starts `turtlesim_node` and `mission_node` together. The turtle drives to Bottle (8.0, 5.5), Mallet (8.0, 8.0) and Base (5.5, 5.5), then publishes zero velocity and logs `DONE`.
 
Interfaces:
 
| Interface | Name | Type |
|---|---|---|
| Subscribes | `/turtle1/pose` | `turtlesim/msg/Pose` |
| Subscribes | `/field_blocked` | `std_msgs/msg/Bool` (true = blocked) |
| Publishes | `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` |
| Service | `/resume_mission` | `std_srvs/srv/Trigger` |
 
Inject the interruption from a second sourced terminal after the mission has started:
 
```bash
# Blocked: the turtle stops and the mission goes to PAUSED
ros2 topic pub --once /field_blocked std_msgs/msg/Bool "{data: true}"
 
# Try to resume while blocked: rejected
ros2 service call /resume_mission std_srvs/srv/Trigger "{}"
 
# Clear the report: the turtle stays still
ros2 topic pub --once /field_blocked std_msgs/msg/Bool "{data: false}"
 
# Explicit resume: accepted, the unfinished target continues
ros2 service call /resume_mission std_srvs/srv/Trigger "{}"
```
 
Clearing the blockage does not restart motion. Only a successful `/resume_mission` call does.
 
## Repository layout
 
```
altair_phase3/
  altair_phase3/
    telemetry_pub.py
    telemetry_sub.py
    driving_menu.py
    mission_node.py
  launch/
    field.launch.py
  resource/altair_phase3
  package.xml
  setup.py
  README.md
```
 
## Troubleshooting
 
- `Package 'altair_phase3' not found`: source `/opt/ros/humble/setup.bash` and then `install/setup.bash`, and make sure `colcon build` finished.
- Turtle does not move in Task 3: check that teleop and the Task 2a node are closed (`ros2 topic info /turtle1/cmd_vel --verbose` should show one publisher).
- No telemetry on the monitor: check both nodes are in the same terminal environment and `ros2 topic list` shows `/rover_telemetry`.
 
