# BME 310 Wearable Design
This repository contains the source code for the ESP8266-based "Heatsleeve" wearable and the Python Kivy based companion app which allows users to easily view more data and access greater device capabilities.

The "Heatsleeve" is a wearable device designed as a final group project for the Biomedical Engineering Junior Design course, BME 310, at University of Arizona. It was a wearable intended to prevent heat exhaustion and heat stroke in high risk individuals, which is particularly relevant in Arizona where we regularly see summer highs of 120+ degrees F. 

This repo is organized into two primary folders, `GUI` and `Arduino`

The `GUI` folder contains two files: `heatsleeveKivy.kv` and `main.py`

- `heatsleeveKivy.kv` is the kivy file detailing the front end of this GUI. It defines three seperate screens: a landing page, a page to gain user information, and the primary dashboard of the app. It also defines several popups that allow access to more information.

- `main.py` is the backend of the app. It passes variables between screens and completes relevant calculations in order to display the most relevant information to the user. This backend is multi-threaded, meaning that there are several processes running simultaneously in parallel to optimize the speed of the display. Here we have two primary threads: the interface thread, responsible for managing user interaction with the GUI, and the serial thread, responsible for constantly reading the serial port and then updating the variables in the main thread for display. This allows the app to read continuously without hindering the user's ability to interact with it, and makes variables update more smoothly in real time.

The `Arduino` Folder is divided further into two folders, `master` and `slave`.

- `master` contains the source code to be loaded onto the device itself. This code manages the collection and transmission of data, as well as the constant updating of the device's OLED screen. This folder also contains a file of custom functions for reading the MPU6050 for this specific application, reducing the number of external dependencies

- `slave` containst the source code for the receiver device, and transmits it to the serial port so it can be read by the GUI.

## Dependencies
The Arduino portion requires the following libraries:
- `SPI.h`
- `Wire.h`
- `MAX30105.h`
- `heartrate.h` (from Sparkfun Library)
- `ESP8266WiFi.h`
- `Adafruit_TCS34725.h`
- `Adafruit_GFX.h`
- `Adafruit_SSD1306.h`

The Python Kivy Portion is dependent on:
- `kivy`
- `kivymd`
- `pyplot`
- `pyserial`
and all of those libraries' dependencies.

## Running Instructions
To run the GUI with your Heatsleeve device.
1. Enter the `GUI` directory
2. `python main.py`

The GUI will then open and you are ready to start using Heatsleeve!
