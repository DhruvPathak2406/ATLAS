#!/usr/bin/env bash
# ATLAS Mission 3 Runner – Counter Threat
set -euo pipefail

LOG="/tmp/atlas_mission3.log"
exec > "$LOG" 2>&1

echo "[$(date)] Starting Mission 3 – Counter Threat"

cd "/mnt/c/Users/drash/ATLAS_AIR/ATLAS/Scenario 2 and 3"
source /opt/ros/jazzy/setup.bash
source install/setup.bash

export DISPLAY=:0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

echo "[$(date)] ROS2 environment sourced. Launching..."

exec ros2 launch atlas_person_2 mission_3.launch.py
