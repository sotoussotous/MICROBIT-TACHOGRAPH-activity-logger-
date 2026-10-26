# 🚛 Micro:bit Tachograph – Activity Logger

## Project Description

A tachograph simulator developed using **Python and BBC Micro:bit**.

The project demonstrates how a motion sensor can automatically detect vehicle movement and communicate with a computer.

The application provides a graphical interface for monitoring driver activities and recording their duration.

## Features

- 🚗 **DRIVING** – Records driving time.
- ☕ **BREAK** – Records rest periods.
- 🔧 **OTHER WORK** – Records other working activities.
- 🚛 **YARD MOVE** – Prevents automatic driving activation while the button is held.
- 📡 **MOTION SENSOR** – Detects movement using Micro:bit.
- 🔊 **WARNING ALARM** – Repeats while movement is detected without a selected driver.
- ⏱️ **LIVE TIMER** – Displays the duration of the current activity.
- 👤 **DRIVER SELECTION** – Supports multiple drivers.
- 📄 **ACTIVITY LOG** – Saves completed activities to a text file.

## Technologies Used

- Python 3
- Tkinter
- PySerial
- BBC Micro:bit
- Microsoft MakeCode JavaScript
- USB Serial Communication

## How It Works

1. Connect the Micro:bit to the computer using a USB cable.
2. Run the Python tachograph application.
3. Select a driver.
4. The Micro:bit detects movement and sends signals to Python.
5. A SHAKE event automatically activates DRIVING unless YARD MOVE is pressed.
6. The program records activity durations.

If movement is detected without a selected driver, a warning alarm is activated.

## Installation

1. Install Python and the PySerial library using `pip install pyserial`.
2. Download `tachograph.py` and `microbit_tachograph.js`.
3. Upload the JavaScript program to Micro:bit using Microsoft MakeCode.
4. Configure the correct COM port in the Python program.
5. Prepare the driver list file and configure the file paths if necessary.
6. Run `python tachograph.py` on Windows.

## Project Files

- **tachograph.py** – Main Python application.
- **microbit_tachograph.js** – Micro:bit motion detection and serial communication.

## Purpose

This project is an educational demonstration of driver activity monitoring, motion detection, serial communication and graphical programming.

**Note:** This is a simulation, not a certified tachograph, and must not be used as a legal driving-hours recording device.



## Project Status

Functional prototype – further development planned.
