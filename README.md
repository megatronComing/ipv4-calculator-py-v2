This script searches subnets by required host numbers from a given ipv4 network ID with subnet length.
Compared to project ipv4-calculator-py, this version is more efficient, and it supports GUI.

# Rum from command line
## Prerequisites
setting the path of python.exe & pip.exe to the PATH environment variable is highly recommended
required modules:
- tabulate
- ipaddress
<br>install the above modules by commands:
- pip install ipaddress
- pip install tabulate
## Command
Run the following command from the cmd window:<br>
python find_subnet_v21.py IP_ADDR/SUBNETMASK_LEN HOSTS1 HOSTS2  HOSTS3 HOSTS4<br>
e.g. python find_subnet_v21.py 192.168.1.0/24 59 15 7 2 29<br>
![image](https://github.com/megatronComing/ipv4-calculator-py-v2/assets/114308295/256fea70-9bf7-4582-9f97-36e63673d672)

# GUI mode
## Prerequisites
setting the path of python.exe & pip.exe to the PATH environment variable is highly recommended<br>
required modules:<br>
- tabulate
- ipaddress
- pyqt5
install the above modules by commands:
pip install ipaddress
pip install tabulate
pip install pyqt5
## Command
Run the following command from the cmd window:
  python subnetter_gui.py

![image](https://github.com/megatronComing/ipv4-calculator-py-v2/assets/114308295/5160649e-f484-4ac9-99d1-bb9412367878)


