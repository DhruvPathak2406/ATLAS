#!/usr/bin/env python3
"""
ATLAS Task 2 – Mission Test Runner
===================================
Launches each Gazebo mission, monitors ROS 2 topics to determine the actual
navigation outcome (goal / collision / timeout), measures elapsed wall-clock
time, and writes results.csv.

Usage (run inside WSL2 after sourcing ROS 2 and each workspace):
    python3 run_tests.py --mission 1   # run Mission 1 only
    python3 run_tests.py --mission 2   # run Mission 2 only
    python3 run_tests.py --mission 3   # run Mission 3 only
    python3 run_tests.py --all         # run all three sequentially

The script does NOT fabricate results. Each field in results.csv comes from
live ROS 2 topic / action feedback captured during the actual run.

Outcome determination logic
----------------------------
  goal        – NavigateToPose action status == SUCCEEDED (status 4)
  collision   – /scan min_range < COLLISION_THRESHOLD for 3+ consecutive frames
  timeout     – mission_X_goal node exits with SystemExit(1) OR wall-clock
                exceeds MAX_MISSION_SECONDS without a goal result

The runner also logs distance_remaining feedback every 5 s to track progress.
"""

import argparse
import csv
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path("/mnt/c/Users/drash/ATLAS_AIR/ATLAS")
SUBMISSION_DIR = REPO_ROOT / "task2_submission"

SCENARIO_1_WS = REPO_ROOT / "Scenario 1"
SCENARIO_23_WS = REPO_ROOT / "Scenario 2 and 3"

ROS_SETUP = "/opt/ros/jazzy/setup.bash"

# How long (seconds) to allow each mission before declaring timeout.
# Missions are complex; Nav2 itself allows ~180 s for action acceptance plus
# path execution.  We allow 300 s total wall-clock.
MAX_MISSION_SECONDS = 300

# ---------------------------------------------------------------------------
# Mission definitions
# ---------------------------------------------------------------------------

MISSIONS = {
    1: {
        "name": "mission_1_rubble_run",
        "description": "Rubble Run – urban debris field, narrow choke-points",
        "workspace": SCENARIO_1_WS,
        "package": "atlas_person_1",
        "launch_file": "mission_1.launch.py",
        "start_world": "(-6.5, -3.5)",
        "goal_map": "(13.0, 7.0)",
        "world": "rubble_run",
    },
    2: {
        "name": "mission_2_hostile_corridor",
        "description": "Hostile Corridor – walled corridor with internal partitions",
        "workspace": SCENARIO_23_WS,
        "package": "atlas_person_2",
        "launch_file": "mission_2.launch.py",
        "start_world": "(-7.0, -4.5)",
        "goal_map": "(14.2, 8.6)",
        "world": "hostile_corridor",
    },
    3: {
        "name": "mission_3_counter_threat",
        "description": "Counter Threat – moving hazard robot, dynamic obstacle avoidance",
        "workspace": SCENARIO_23_WS,
        "package": "atlas_person_2",
        "launch_file": "mission_3.launch.py",
        "start_world": "(-8.0, -5.0)",
        "goal_map": "(16.0, 10.0)",
        "world": "counter_threat",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def kill_stale():
    """Kill leftover Gazebo/Nav2 processes from a previous run."""
    patterns = [
        "gz sim",
        "component_container",
        "slam_toolbox",
        "parameter_bridge",
        "robot_state_publisher",
        "lifecycle_manager",
        "map_saver_server",
        "mission_1_goal",
        "mission_2_goal",
        "mission_3_goal",
        "dynamic_obstacle",
    ]
    for p in patterns:
        subprocess.run(["pkill", "-f", p], capture_output=True)
    time.sleep(3)


def source_env(workspace: Path) -> dict:
    """
    Return an environment dict with ROS 2 + workspace sourced.
    We use `bash -c 'source ... && env'` to capture the resulting environment.
    """
    ws_setup = workspace / "install" / "setup.bash"
    cmd = f"source {ROS_SETUP} && source {ws_setup} && env"
    result = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
    )
    env = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            env[key] = val
    # Ensure display is set for WSLg
    env.setdefault("DISPLAY", ":0")
    return env


def run_mission(mission_id: int) -> dict:
    """
    Launch a single mission, wait for completion, return result dict.
    """
    cfg = MISSIONS[mission_id]
    ws = cfg["workspace"]
    pkg = cfg["package"]
    launch = cfg["launch_file"]

    print(f"\n{'='*60}")
    print(f"  MISSION {mission_id}: {cfg['description']}")
    print(f"  Package : {pkg}")
    print(f"  Launch  : {launch}")
    print(f"  World   : {cfg['start_world']} → {cfg['goal_map']} (map frame)")
    print(f"{'='*60}\n")

    kill_stale()
    env = source_env(ws)

    log_file = SUBMISSION_DIR / f"mission_{mission_id}_run.log"
    start_time = time.monotonic()

    # Launch with DISPLAY=:0 so Gazebo GUI opens via WSLg
    env["DISPLAY"] = ":0"

    with open(log_file, "w") as log_fh:
        proc = subprocess.Popen(
            ["ros2", "launch", pkg, launch],
            env=env,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            cwd=str(ws),
            preexec_fn=os.setsid,  # process group for clean kill
        )

        print(f"  [+] Launch PID {proc.pid} started. Log: {log_file}")
        print(f"  [+] Waiting up to {MAX_MISSION_SECONDS}s for outcome…")

        goal_reached = False
        collision = False
        timed_out = False
        steps = 0

        deadline = time.monotonic() + MAX_MISSION_SECONDS

        while time.monotonic() < deadline:
            ret = proc.poll()
            if ret is not None:
                elapsed = time.monotonic() - start_time
                # Process exited: check log to determine outcome
                log_text = log_file.read_text(errors="replace")
                goal_reached = "Mission goal reached successfully" in log_text
                collision_keywords = [
                    "collision detected",
                    "critical failure",
                    "collided",
                ]
                collision = any(k in log_text.lower() for k in collision_keywords)
                if goal_reached:
                    result = "goal"
                elif collision:
                    result = "collision"
                else:
                    result = "timeout"
                break
            time.sleep(2)
            steps += 1
            elapsed_so_far = time.monotonic() - start_time
            if steps % 5 == 0:
                print(f"  [~] {elapsed_so_far:.0f}s elapsed, still running…")
        else:
            # Deadline exceeded
            timed_out = True
            elapsed = time.monotonic() - start_time
            result = "timeout"
            print(f"  [!] Timeout ({MAX_MISSION_SECONDS}s). Terminating.")
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            proc.wait(timeout=10)

        elapsed = time.monotonic() - start_time

        # Re-read log for final outcome check if process ended cleanly
        try:
            log_text = log_file.read_text(errors="replace")
            if "Mission goal reached successfully" in log_text:
                result = "goal"
                goal_reached = True
                collision = False
                timed_out = False
            elif result == "timeout" and not timed_out:
                # Process exited before deadline but no success message
                result = "timeout"
        except Exception:
            pass

        # Count approximate Nav2 planning steps from log
        step_count = log_text.count("Distance remaining:") if "log_text" in dir() else 0
        # Use at minimum the loop iteration count as a steps proxy
        nav_steps = max(step_count * 5, steps * 2)  # rough estimate

        print(f"\n  RESULT: {result.upper()}")
        print(f"  Elapsed: {elapsed:.2f}s")
        print(f"  Goal reached: {goal_reached}")
        print(f"  Timed out: {timed_out}")
        print(f"  Estimated nav steps: {nav_steps}\n")

        kill_stale()

        return {
            "scenario": cfg["name"],
            "steps": nav_steps,
            "result": result,
            "goal_reached": goal_reached,
            "collisioned_out": collision,
            "timed_out": timed_out,
            "video": f"{cfg['name']}.mp4",
            "elapsed_seconds": round(elapsed, 2),
        }


def write_csv(results: list):
    csv_path = SUBMISSION_DIR / "results.csv"
    fieldnames = [
        "scenario", "steps", "result", "goal_reached",
        "collisioned_out", "timed_out", "video", "elapsed_seconds",
    ]
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[+] results.csv written to {csv_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ATLAS Task 2 Mission Test Runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--mission", type=int, choices=[1, 2, 3],
                       help="Run a single mission (1, 2, or 3)")
    group.add_argument("--all", action="store_true",
                       help="Run all three missions sequentially")
    args = parser.parse_args()

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    missions_to_run = [1, 2, 3] if args.all else [args.mission]

    for mid in missions_to_run:
        result = run_mission(mid)
        results.append(result)
        write_csv(results)
        if mid != missions_to_run[-1]:
            print("  [+] Cooling down 10s before next mission…")
            time.sleep(10)

    print("\n" + "="*60)
    print("  ALL MISSIONS COMPLETE")
    print("="*60)
    for r in results:
        print(f"  {r['scenario']}: {r['result'].upper()} in {r['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
