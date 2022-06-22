# Prerequisites
## Clone the repository
```
# Create application folder, here is just a suggestion
mkdir /teststat

# Go to your development root directory
cd <YOUR_DEV_ROOT>

# Checkout the repository to TESTstat
git clone https://github.com/bahadirbasaran/TESTstat.git
```

## Workflow for virtual environment
```
# Create a virtualenv with the homebrew python
python3 -m venv venv3
 
# Activate the virtualenv
source venv3/bin/activate
 
# Install the packages inside virtualenv
pip install -r requirements.txt

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
pip install -r requirements_M1.txt
            

# Run the app
python main.py

```
