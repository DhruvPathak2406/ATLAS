#!/usr/bin/env bash
# ATLAS Mission 1 Runner – Rubble Run
# Captures stdout/stderr to log file, sets DISPLAY for WSLg
set -euo pipefail

LOG="/tmp/atlas_mission1.log"
exec > "$LOG" 2>&1

echo "[$(date)] Starting Mission 1 – Rubble Run"
echo "[$(date)] Display: $DISPLAY"

cd "/mnt/c/Users/drash/ATLAS_AIR/ATLAS/Scenario 1"
source /opt/ros/jazzy/setup.bash
source install/setup.bash

export DISPLAY=:0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

echo "[$(date)] ROS2 environment sourced. Launching..."

exec ros2 launch atlas_person_1 mission_1.launch.py
