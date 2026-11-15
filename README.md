# ATLAS: Autonomous Navigation & Simulation with NavRep

**Course:** CS359: Artificial Intelligence for Robotics  
**Institution:** Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat  
**Department:** Computer Science & Engineering  
**Project Repository:** [https://github.com/DhruvPathak2406/ATLAS](https://github.com/DhruvPathak2406/ATLAS)  
**Upstream Reference:** [ETH Zurich ASL - NavRep](https://github.com/ethz-asl/navrep)

---

## 1. Project Overview

**ATLAS** is our team's implementation, benchmark analysis, and custom scenario development project built on top of **NavRep**—an open-source research framework developed by the Autonomous Systems Lab (ASL) at ETH Zurich for unsupervised-learning-assisted Reinforcement Learning (RL) in dynamic human environments.

The core objective of this project is to simulate, evaluate, and extend intelligent robot navigation and dynamic obstacle avoidance in crowded spaces (such as shopping malls, hospitals, and warehouses).

### Project Scope & Deliverables
1. **Task 1 — Environment Setup & Documentation:** Clone, configure, resolve legacy dependency issues, and execute the NavRep simulation stack, documented through this `README.md`.
2. **Task 2 — Benchmark Scenario Testing:** Execute all pre-built simulation environments (`NavRepTrain`, `NavRepTest`, `SOADRL`, `Pfeiffer`) and analyze robot trajectory planning and collision avoidance behavior.
3. **Task 3 — Custom Real-World Simulation Scenarios:** Design and implement custom maps with modified robot start/goal coordinates and dynamic pedestrian flows (e.g., an autonomous shopping mall guidance/bag-carrying assistant robot).

### Team Members

* **Member 1:** Dhruv Pathak - U24CS018
* **Member 2:** Khushboo - U24CS038
* **Member 3:** Sneha Kumari - U24CS046
* **Member 4:** Meet - U24CS063
* **Member 5:** Drashti  - U24CS067

---

## 2. Operating System Details

* **Operating System:** Ubuntu 20.04 LTS (Focal Fossa) *(Recommended for Python 3.6 + OpenAI Gym 0.15.7 compatibility)*
* **Architecture:** x86_64

---

## 3. Software Requirements & Dependencies

NavRep relies on specific legacy versions of Python and reinforcement learning libraries:

* **Python:** `Python 3.6` (Required due to `gym==0.15.7` and `keras==2.3.1` constraints)
* **Virtual Environment:** `virtualenv`
* **Core Python Libraries:**
  * `gym==0.15.7`
  * `keras==2.3.1`
  * `tensorflow` (v1.15 / v2.x compatible with Keras 2.3.1)
  * `torch` (PyTorch for Transformer / VAE-LSTM models)
  * `pyglet==1.5.27` (for 2D LiDAR & crowd rendering)
  * `numpy`, `scipy`, `matplotlib`, `opencv-python`, `pyyaml`
* **ROS Dependencies (Optional for full ROS node integration):**
  * `rospy`, `rosbag`, `tf`, `tf2_ros` (installed via `rospypi`)

---

## 4. Installation Steps & Commands

### Step 1: Install System Prerequisites & Python 3.6
On Ubuntu 20.04 LTS, install Python 3.6 via the `deadsnakes` PPA along with `virtualenv`:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.6 python3.6-dev build-essential cmake git
sudo apt-get install -y virtualenv python3-virtualenv
```

### Step 2: Clone the Project Repository
```bash
git clone [https://github.com/DhruvPathak2406/ATLAS.git](https://github.com/DhruvPathak2406/ATLAS.git)
cd ATLAS
```

### Step 3: Create & Activate Virtual Environment
```bash
virtualenv ~/navrepvenv --python=python3.6
source ~/navrepvenv/bin/activate
```

### Step 4: Install Dependencies & NavRep Package
```bash
# Upgrade pip inside the virtual environment
pip install --upgrade pip setuptools wheel

# Install exact compatible versions of Gym and Keras
pip install gym==0.15.7 keras==2.3.1

# Install ROS Python packages without full ROS desktop installation
pip install --extra-index-url [https://rospypi.github.io/simple/](https://rospypi.github.io/simple/) rospy rosbag tf tf2_ros

# Install remaining repository dependencies and link package in editable mode
pip install -r requirements.txt
pip install -e .
```

---

## 5. Code & Configuration Modifications

To ensure smooth execution on modern Ubuntu systems without full ROS Melodic installations, the following configurations were applied:

1. **Pinned Legacy RL Packages:** Explicitly enforced `gym==0.15.7` and `keras==2.3.1` prior to running `requirements.txt` to prevent breaking API changes in `gym.envs.classic_control` and `pyglet`.
2. **Standalone `rospy` Setup:** Used the `rospypi` wheel index (`https://rospypi.github.io/simple/`) to satisfy ROS message and transform dependencies (`tf`, `tf2_ros`) inside the isolated `virtualenv`.
3. **Display Export for Pyglet Rendering:** Configured local X11 display forwarding (`export DISPLAY=:0`) to ensure simulation windows render reliably.

---

## 6. Challenges, Errors & Solutions

| # | Challenge / Error Encountered | Root Cause | Solution / Fix |
|---|---|---|---|
| **1** | `ModuleNotFoundError: No module named 'navrep'` | Repository root was not registered in the active `virtualenv` site-packages. | Executed `pip install -e .` from the root repository directory. |
| **2** | `AttributeError` / rendering crashes in OpenAI Gym | Newer Gym versions (`>=0.21`) break compatibility with NavRep's custom 2D LiDAR ring environments. | Pinned `gym==0.15.7` as specified in upstream documentation. |
| **3** | `No module named 'rospy'` or `'tf2_ros'` | Running standalone Python without sourcing a system-wide ROS workspace. | Installed lightweight ROS Python wheels via `--extra-index-url https://rospypi.github.io/simple/`. |
| **4** | `pyglet.canvas.xlib.NoSuchDisplayException` | Headless terminal or missing X-server display variable during `--render` calls. | Exported `DISPLAY=:0` locally or prefixed commands with `xvfb-run -s "-screen 0 1024x768x24"`. |

---

## 7. Execution & Running Simulation Scenarios

Always ensure your virtual environment is activated before running any simulation script:
```bash
source ~/navrepvenv/bin/activate
```

### A. Interactive Manual Control Test
Launch the base training environment and control the robot manually (`W`, `A`, `S`, `D` keys to steer; `Shift` to speed up):
```bash
python -m navrep.envs.navreptrainenv
```

### B. Testing Pre-Trained Navigation Models
Evaluate pre-trained models (located in `~/navrep/models/`) inside the test environment with live rendering:
```bash
python -m navrep.scripts.cross_test_navreptrain_in_ianenv --backend VAE_LSTM --encoding V_ONLY --render
```
*Supported `--backend` flags include:* `VAE_LSTM`, `VAE1D_LSTM`, `VAELSTM`, `GPT`, `GPT1D`, `E2E`.

### C. Dataset Generation & Model Training Pipeline
To reproduce the Visual (`V`) and Memory (`M`) representation datasets:
```bash
# 1. Generate VAE dataset (add --render to visualize)
python -m navrep.scripts.make_vae_dataset --environment navreptrain --render

# 2. Generate RNN dataset and train Memory model
python -m navrep.scripts.make_rnn_dataset --environment navreptrain
python -m navrep.scripts.train_rnn --environment navreptrain
```
