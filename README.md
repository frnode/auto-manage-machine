# auto-manage-machine

Automatically create a machine using the parameters defined in the configuration file (for now only the Virtualbox platform is implemented).

After the installation of the machine, a command defined in the configuration file will be executed, allowing a lot of possibilities (execute a remote bash file for example)
## Dependencies
[![img](https://img.shields.io/pypi/v/coloredlogs?label=coloredlogs)](https://pypi.org/project/coloredlogs/)
[![img](https://img.shields.io/pypi/v/virtualbox?label=virtualbox)](https://pypi.org/project/virtualbox/)
[![img](https://img.shields.io/pypi/v/pywin32?label=pywin32)](https://pypi.org/project/pywin32/)
   
## How to use ?
- In a first, look at the [requirements](https://github.com/frnode/auto-manage-machine#Requirements) for what you want to do.


## Requirements
Tested on **`Windows 10 version 1903`** with **`Python 3.7`** 
_(The program probably works in other environments, it's up to you to try!)._ 
**Open an issue if you encounter a problem.**

- For **Virtualbox** (The only implemented for the moment)
    
    - Download Virtualbox in the desired version at this address: 
     https://download.virtualbox.org/virtualbox/ 
    - Or latest version: https://www.virtualbox.org/wiki/Downloads
    - **`.OVA`** template file in the folder **`/data/ova`**
    - Set the parameters specific to Virtualbox in the file `config.ini` _(Below "; Only for Virtualbox")_


