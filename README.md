# auto-manage-machine

Automatically create a machine using the parameters defined in the configuration file (for now only the Virtualbox platform is implemented).

After the installation of the machine, a command defined in the configuration file will be executed, allowing a lot of possibilities (execute a remote bash file for example)
## Dependencies
[![img](https://img.shields.io/pypi/v/coloredlogs?label=coloredlogs)](https://pypi.org/project/coloredlogs/)
[![img](https://img.shields.io/pypi/v/virtualbox?label=virtualbox)](https://pypi.org/project/virtualbox/)
[![img](https://img.shields.io/pypi/v/pywin32?label=pywin32)](https://pypi.org/project/pywin32/)
   
## How to use ?
- Clone the repositories `git clone https://github.com/frnode/auto-manage-machine.git`
- Look at the [requirements](https://github.com/frnode/auto-manage-machine#requirements) for what you want to do.
- Define the different options in the [config.ini](https://github.com/frnode/auto-manage-machine/blob/dev/automanagemachine/config/config_vbox.ini) file
- Finally, start the program `python automanagemachine/run.py`

## Requirements
Tested on `Windows 10 version 1903` with `Python 3.7` 
_(The program probably works in other environments, it's up to you to try!)._ 
**Open an issue if you encounter a problem.**

- For **Virtualbox** (The only implemented for the moment)
    
    - Download Virtualbox in the desired version at this address: 
     https://download.virtualbox.org/virtualbox/ or latest version https://www.virtualbox.org/wiki/Downloads
    - `.OVA` template file in the folder `/data/ova` **(Virtualbox additions must be installed on the operating system.)**
    - Set the parameters specific to Virtualbox in the file `config/config_vbox.ini`


