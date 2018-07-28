<img src="images/nus.png" height=100 /><img src="images/sinapse.png" height=100 align="right"/>

# 3D Shape Recognition using Neuromorphic Tactile Sensing
This repository contains the code for my project at **SINAPSE, National University of Singapore** during May-July 2018 as a part of my research internship under the guidance of **Prof. Alcimar Soares**. I was guided by Andrei Nakagawa, Rohan Ghosh and Nipun Batra.

## Setup
Install `PCL-1.8` (Point Cloud Library) from source by following the instructions on [http://pointclouds.org/downloads/](http://pointclouds.org/downloads/).

Install necessary `Python3` modules by executing this commands
```bash
sudo pip3 install numpy tensorflow tensorflow-gpu scipy lzf seaborn
sudo apt install python-skimage # for Ubuntu 16.04
# If the above command doesn't work, you may try this
# sudo pip3 install skimage
```

Assuming that `cmake` has already been installed, build the `extract_pov` binary 
```bash
cd scripts
mkdir build && cd build
cmake .. && make && mv extract_pov ../
```

## Execution
`cd` into the `GUI` folder and execute the following command (assuming `PyQt5` has been installed and set up)
```
python3 formMain.py
```
## References
The research papers referred for this project can be found [here](references/).
