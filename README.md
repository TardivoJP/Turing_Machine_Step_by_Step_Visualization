# Turing Machine Step by Step Visualization
## _An educational tool for visualizing how a Turing Machine truly works_

![Hero art](https://i.imgur.com/SQ6EUeW.png)

This desktop application allows the user to customize and build their own Turing Machine in a more intuitive, direct visual manner, by using the center canvas to add new states and customize them at will. They're also able to see the tape at the top of the screen, change its symbols and where the head is currently pointing.

For the purpuses of the educational simulation, we'll assume the tape is finite with 25 slots, there's only a single initial state, and multiple transitions using the same symbol on a single state aren't allowed.

![Application screenshot](https://i.imgur.com/34Ynnu6.png)

## Usage

- Before running the application, make sure to add the symbols you want to use to the "symbols.txt" file.
- Run the application and right click the empty canvas to add a new state.

![Application screenshot](https://i.imgur.com/t6kP15x.png)

- Right click a state to set it as initial, accept state, create a new transition from it or delete it entirely.

![Application screenshot](https://i.imgur.com/t6PUCgD.png)

- If you selected to create a new transition, right click on the desired destination state and select the option, or just cancel if you change your mind.
   * You can create looping transitions that begin and end at the same state.

![Application screenshot](https://i.imgur.com/j3W3EyF.png)

- Left click the desired spot in the tape to set the head location there and change that index's symbol.
- It's possible to change the tape's symbols at any time during the simulation, to test out different outcomes.

![Application screenshot](https://i.imgur.com/zCdzqFL.png)

- Left click the simulate button to see each step of the simulation, but remember that you need an initial state for it to work.
- Left click the reset button to return the simulation steps to the initial state and clear the tape.

![Application screenshot](https://i.imgur.com/Bv10oHO.png)


## Packages used

This educational application was only made possible because of these amazing packages.

| Package | Link |
| ------ | ------ |
| PyGame | https://www.pygame.org/wiki/GettingStarted |
| PyInstaller | https://pypi.org/project/pyinstaller/ |

## Building the application

If you want to build the application yourself from the source code:

**Windows**
1. Download Python from https://www.python.org/downloads/ and install it
2. Open a terminal and run this command to install the dependencies:
```sh
pip install PyGame PyInstaller
```
3. Navigate to the source code's directory and run this command to build the application:
```sh
pyInstaller turing_visual_step_simulation.py --onefile --noconsole
```
4. Run the newly created .exe in the "dist" folder

**Linux**
1. Download and install Python using the package manager from your distro:
* Ubuntu/Debian
```sh
sudo apt install python3
```
* Fedora
```sh
sudo dnf install python3
```
* CentOS/RHEL
```sh
sudo yum install centos-release-scl
sudo yum install rh-python36
scl enable rh-python36 bash
```
* Arch
```sh
sudo pacman -S python
```
2. Download and install the Package Installer for Python (pip):
```sh
python3 get-pip.py
```
3. Download and install the dependencies:
```sh
sudo pip3 install pyinstaller pyGame
```
4. Navigate to the source code's directory and run this command to build the application:
```sh
python3 -m PyInstaller turing_visual_step_simulation.py --onefile --noconsole
```
5. Navigate to the newly created "dist" folder
6. Run this command on the main_window binary file to grant it permission to execute
```sh
chmod +x main_window
```
7. Run the application with this command:
```sh
./main_window
```

## Compatibility

This application currently runs on Windows 10 and Linux. I am looking into the possibility of adding a macOS release but I won't make any promises.