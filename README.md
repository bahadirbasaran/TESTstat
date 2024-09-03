# Prerequisites
## Clone the repository
```
# Create application folder, here is just a suggestion
mkdir /teststat

# Go to your development root directory
cd <YOUR_DEV_ROOT>

# Checkout the repository to TESTstat
git clone https://gitlab.ripe.net/rnd/teststat.git

brew install python@3.9 
```

## Workflow for virtual environment
```
# Create a virtualenv with the homebrew python
python3.9 -m venv venv
 
# Activate the virtualenv
source venv/bin/activate
 
# Install the packages inside virtualenv
pip install -r requirements/gui.txt

# Run the app
python main.py
```


## Workflow for virtual environment for M1 chip 
```
# Create a virtualenv with the homebrew python
/opt/homebrew/bin/python3.9 -m venv --system-site-packages teststat_venv

# Install PyQT with homebrew 
brew install pyqt@5
 
# Activate the virtualenv
source teststat_venv/bin/activate
 
# Install the packages inside virtualenv
pip install -r requirements/gui_M1.txt

# Run the app
python main.py
```

## Containerized workflow

The GitLab Docker [build image](.gitlab/Dockerfile) installs a Python 3.9 virtual environment with all requirements and can be used locally.

```sh
docker build -t teststat -f .gitlab/Dockerfile .
docker run -v "$(pwd)":/src -it teststat
```
