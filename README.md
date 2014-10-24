pyzabbix-agent
==============

pyzabbix-agent loadable module is a way to extend zabbix_agentd daemon
with Python. The main goal is to avoid costly and slow exec calls and
loading of the interpreter

1. Installation.

At this moment, I do not recommend to use this module in a production
environment. There are bugs. There are undetected issues. 

First you have to do is to modify MAIN_PYTHON_LIB in python.c and
point it to your actual Python dynamic library. This module will
pre-load Python library during the startup. This is necessary for the
Python dynamic modules.

Next, check the include path and compilation parameters in Makefile
and run male

Copy python.so to the directory defined by LoadModulePath in
zabbix_agentd.conf

Create subdirectory pymodules in the directory where your
configuration file is installed

Install python zabbix modules in this directory.

Add LoadModule=python.so in your zabbix_agentd.conf

Restart zabbix_agentd

2. Zabbix python module

Is a regular python module, where you shall define function
main(*args). All arguments passed from Zabbix to an agent, will be
passed to a main() functions as srings. Return value will be returned
to Zabbix. Only Int, Long and String supported as return values.

3. "Special" zabbix modules

ZBX_startup.py - module, which main() function will be executed during
zabbix_agentd startup

ZBX_finish.py - module, which main() function will be executed during
zabbix_agentd finish
