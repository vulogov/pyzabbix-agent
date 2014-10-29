pyzabbix-agent
==============

The `pyzabbix-agent` loadable module is a way to extend `zabbix_agentd` daemon
with Python. The main goal is to avoid costly and slow exec calls and
loading of the interpreter.

## Installation.

At this moment, I do not recommend to use this module in a production
environment. There are bugs. There are undetected issues.

* Run `./configure` script.

* Check the include path and compilation parameters in `Makefile`
and run `make`.

* Copy `python.so` to the directory defined by `LoadModulePath` in
`zabbix_agentd.conf`

* Create subdirectory `pymodules` in the directory where your
configuration file is installed

* Install the Python Zabbix modules in this directory.

* Add `LoadModule=python.so` in your `zabbix_agentd.conf`.


* Set the `PYTHONPATH` as: 

```
export PYTHONPATH=`python -c "import sys; print ':'.join(sys.path)"`
```

* Restart `zabbix_agentd`


## Zabbix Python module

This is a regular python module, where you shall define function
main(*args). All arguments passed from Zabbix to an agent, will be
passed to a main() functions as srings. The return value will be returned
to Zabbix. Only Int, Long, Float and String information types are supported as return values.

## "Special" Zabbix modules

These modules perform some special actions.

* `ZBX_startup.py` - module, which main() function will be executed during
`zabbix_agentd` startup

* `ZBX_finish.py` - module, which main() function will be executed during
`zabbix_agentd` finish

## Python interface

The following item keys are supported:

* `python.ping` - no parameters. Return 1 if embedded Python is initialized
* `python.version` - returns version of the embedded Python interpreter
* `python` - calling the Python Zabbix module. The first parameter is the
name of the module, the next parameters will be passed to the main()
function of the module.
* `python.prof` - same as `python`, but instead returning the value, returns
execution time of the module in miliseconds.
