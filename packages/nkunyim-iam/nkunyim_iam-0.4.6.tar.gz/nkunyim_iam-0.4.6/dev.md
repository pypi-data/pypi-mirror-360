# Developer Notes

## Virtual Environment
- sudo apt install python3.12-venv


## Required Packages
- sudo python3.12 -m venv /home/enoch/devspace/env/package
- source /home/enoch/devspace/env/package/bin/activate
- sudo chmod -R a+rwx /home/enoch/devspace/env/package
- pip install --upgrade pip
- pip install --upgrade build twine


## NkunyimUtil Dependencies
- sudo python3.12 -m venv /home/enoch/devspace/env/nkunyim
- source /home/enoch/devspace/env/nkunyim/bin/activate
- sudo chmod -R a+rwx /home/enoch/devspace/env/nkunyim
- pip install --upgrade pip
- pip install --upgrade Django requests cryptography djangorestframework
- pip install --upgrade pyyaml ua-parser user-agents
- pip install --upgrade pyjwt
- pip freeze > requirements.txt


### Select Project
- cd /home/enoch/devspace/dev/nkunyim_iam
- source /home/enoch/devspace/env/package/bin/activate

## Build Package
- python3 -m build


## Upload Package
- python3 -m twine upload dist/*