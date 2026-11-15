#!/usr/bin/env bash
# ATLAS Mission 2 Runner – Hostile Corridor
set -euo pipefail

LOG="/tmp/atlas_mission2.log"
exec > "$LOG" 2>&1

echo "[$(date)] Starting Mission 2 – Hostile Corridor"

cd "/mnt/c/Users/drash/ATLAS_AIR/ATLAS/Scenario 2 and 3"
source /opt/ros/jazzy/setup.bash
source install/setup.bash

export DISPLAY=:0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

echo "[$(date)] ROS2 environment sourced. Launching..."

exec ros2 launch atlas_person_2 mission_2.launch.py
