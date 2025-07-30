# The Python Interface to LINDO API.

This package requires LINDO API and a valid license key. Please refer to lindoapi/readme.html for LINDO API installation details.

## Installation for LINDO API 15

This python package can be installed with pip

For administrative users: 

```bash
> pip install lindo
```

For standard (non-administrative) users:

```bash
> pip install lindo --user
```
## Installation for LINDO API 14

This python package can be installed with pip

For administrative users: 

```bash
> pip install lindo==14.0.0
```

For standard (non-administrative) users:

```bash
> pip install lindo==14.0.0 --user
```

## Testing

A quick way to test the installation is to run
```bash
> python -m lindo_test
```

You can also try out the samples by 
```
> python samples/lp.py
```

## Possible errors due to misconfiguration

You may get the following error if your LINDOAPI_HOME environment variable is not set up.  

```
Error: Environment variable LINDOAPI_HOME should be set
```

To fix the problem follow these steps

### Using Windows
On the command line
```dos
> setx LINDOAPI_HOME "c:/lindoapi" 
```
### Using Mac or Linux
On the command line

For administrative users:
```     
$ export LINDOAPI_HOME="/opt/lindoapi"	
```    
For standard (non-administrative) users:
```    
$ export LINDOAPI_HOME="~/opt/lindoapi"	
```   
To have this variable set automatically, add the above line to your `~/.bashrc` or `~/.bash_profile` file.

## For Mac Users 
The LINDO api has two version that could be compatible with your machine osx64x86 and arm64. If you are using osx64x86 then your Python distribution must have been installed on an Intel Mac or using Rosetta, otherwise it will target arm64 .whl files when using pip. Similarly, if you are using a M1/M2 Mac when Python was installed on your machine Rosetta should have been disabled. The LINDO api supports Python 3.7-3.10 on osx64x86 and Python 3.10 on arm64. 

## How to Build Wheel and Install (for package managers)

To build the python package on any operating system first start by creating a whl file. From the top of the lindoapi-python directory run the command.

```bash
> python -m build
```

If the command is successful a new directory named `dist` is created in the lindoapi-python directory. The new directory will have a two files with extension `.whl` and `.tar.gz`. For example, if you built it on Mac OS using Python 3.10 the new directory will look like this.

```bash
├── dist
│  ├── lindo-x.y.z-cp310-cp310-macosx_10_9_universal2.whl
│  └── lindo-x.y.z.tar.gz
```

The package can now be installed locally using the command.
```bash
> pip install dist/*.whl
```


