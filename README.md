# Smart Parking System

## Overview
This project is a **Smart Parking Management System** that simulates parking lot operations using MQTT communication, emulators for devices, and a GUI interface.  
It is designed as a course project following the given requirements and using only the technologies taught.

## Features
- **Three types of emulators:**
  1. **Spot Emulator** – Simulates parking spot occupancy detection.
  2. **Barrier Emulator** – Simulates parking gate opening/closing.
  3. **Button Emulator** – Simulates entry/exit button presses.
- **Data Manager App** – Collects sensor data from the MQTT broker, stores it in a SQLite database, and processes events to send alarms/warnings.
- **Main GUI App** – Displays real-time parking occupancy, barrier status, and alerts. Includes manual controls to open/close the barrier.
- **Local Database** – SQLite database for storing sensor data and alarms.
- **Auto Exit Simulation** – Every fixed interval, a random car exits, freeing a spot and opening the barrier automatically.

## System Architecture
1. **Emulators** publish simulated data to the MQTT broker.
2. **Manager** subscribes to sensor data, updates parking state, and issues control commands or alarms.
3. **GUI** visualizes parking lot status and alarms in real-time.
4. **Database** stores all events for historical analysis.

## Technologies Used
- **Python 3**
- **PyQt5** (GUI)
- **PyQtGraph** (Graph plotting)
- **SQLite3** (Database)
- **paho-mqtt** (MQTT communication)
- **Threading** (Background processes)

## How to Run
1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Run the emulators:
    ```bash
    python emulator_spots.py
    python emulator_barrier.py
    python emulator_button.py
    python emulator_exit.py
    ```
3. Run the data manager:
    ```bash
    python manager.py
    ```
4. Run the GUI:
    ```bash
    python gui.py
    ```

## Project Structure
```
SmartParking/
├── emulator_spots.py       # Simulates parking spots
├── emulator_barrier.py     # Simulates gate barrier
├── emulator_button.py      # Simulates entry/exit buttons
├── emulator_exit.py        # Simulates automatic/random exit
├── manager.py              # Data manager application
├── gui.py                  # Main GUI
├── data_acq.py             # Database handler
├── init.py                 # Configuration constants
├── agent.py                # MQTT client handler
└── parkingdata.db          # SQLite database
```

## Authors
Developed as part of a course project.

