# SPICE data quicklook in PyQt5 / PyQtGraph

This graphical user interface (GUI) allows you to have a quick look in the SPICE data (provide level 2 '.fits' files in input). You will be able to navigate dynamically in the data thanks to sliders which update the maps I(x,y) ; I(lambda,y), the curve I(lambda) and more.

Also, you can draw a gaussian fit on the profile I(lambda) and generate the maps related to the gaussian parameters.

## - Documentation

`docs/user_manual/user_documentation.pdf`

## - Installation

### 0) If you don't already have a python3/pip3 environment:

`sudo apt-get install build-essential libssl-dev libffi-dev python-dev`  
`sudo apt install python3-pip`  

Optional: install and run a virtual env (an IDE like Pycharm would be also fine)   
`sudo apt-get install python3-venv`  
`python3 -m venv env`  
`. env/bin/activate`  

### A - Using official package
`pip install spiceitup`

### B - Manually from project
#### B.1) Install the requirements  
`pip install -r requirements.txt`  
**Think to upgrade numpy to > 1.20 for nanpercentile usage.** (Then reboot your IDE)  
`pip install numpy --upgrade`

#### B.2) Run the app  
`python3 run.py` or use an IDE like pycharm (which will install the requirements automatically), open this folder as a project and run `run.py`

#### B.3) Troubleshooting
Error known: **"qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found. [...] Aborted (core dumped)"**  
In this case, try to do: `sudo apt-get install --reinstall libxcb-xinerama0`

#### B.4) For developers
- See docs/code_conventions.txt before adding some codes  
- Watch logs with `watch tail logs/debug.log` or `logs/show_debug_console.sh`  
