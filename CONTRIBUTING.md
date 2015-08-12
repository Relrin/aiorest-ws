Contributing
============

Instructions for contributors
-----------------------------

Go to [aiorest-ws](https://github.com/Relrin/aiorest-ws) project repository and press ["Fork"](https://github.com/Relrin/aiorest-ws#fork-destination-box) button on the upper-right menu of the web page.

I'm hope, that most of all, who read this "How to ..." knows how to work with GitHub.

Workflow is very simple:

>  1. Clone the aiorest-ws repository  
>  2. Make a changes in your own repository  
>  3. Make sure all tests passed  
>  4. Commit changes to own aiorest-ws clone  
>  5. Make pull request from GitHub page for your clone  

Creating your own enviroment for development
--------------------------------------------

Before starting development necessary install Python 3, pip and some packages. 

We expect you to use a python virtual environment to run our tests.  
1) Install Python 3 with pip
- Linux
```bash
wget https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz
tar xf Python-3.* 
cd Python-3.*
./configure
make
make install
pip install virtualenv
```
- Mac OS X
```bash
brew update
brew install python3
pip3 install virtualenv
```
- Windows  
Download lastest stable release of Python 3rd branch from [Python language website](https://www.python.org/) and install it.  

2) Create virtual environment via console or terminal (for more details read [official documentation](https://virtualenv.pypa.io/en/latest/) for virtualenv)

We have a several ways to create a virtual environment.

For **virtualenv** use this:
```bash
cd aiorest_ws
virtualenv --python=`which python3` venv
```
For standard python **venv**:
```bash
cd aiorest_ws
python3 -m venv venv
```
For **virtualenvwrapper**:
```bash
cd aiorest_ws
mkvirtualenv --python=`which python3` aiorest_ws
```
3) Activate your virtual environment
```bash
source bin/activate
```
P.S. For exit from the virtualenv use ```deactivate``` command.  
4) Install requirements for development from the root directory of project
```
pip install -r requirements.txt
```
5) Done! Now you can make your own changes in code. :)

Debugging
---------
For debug cases I prefer to use **pudb** in a pair with **ipython**, which already installed on the 4th step of making your own environment.
In code, when necessary pause programm and start debug with Step In/Out, paste 
```python
import pudb; pudb.set_trace()
```

Testing
-------
We have few ways to start test suites:  

1. Using make tool  
 a. In single thread use ```make test```  
 b. In parallel (4 threads) ```make test_parallel```
2. Using ```runtests.py``` script (single-threaded):
```python
python tests/runtests.py
```  

P.S. For debug cases use single thread approach.


For future pull requests
------------------------
For every part of code, which you will make as PR(=Pull Request), necessary to satisfy few conditions:  
1. All previous tests are passed.  
2. If necessary (in most situations it really does important) write test for cover your own part of code.  
3. ```make flake``` doesn't print any errors/warning.  
