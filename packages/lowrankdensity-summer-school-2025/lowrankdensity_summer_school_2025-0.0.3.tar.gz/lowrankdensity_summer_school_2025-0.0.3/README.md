# Learn how to develop your own Python Package 📦 - Hi! PARIS Summer School 2023


In this practical research tips session hosted by the Hi! PARIS Engineering Team, you will learn how
to **build**, **test** and **publish Python packages**.

This repository contains the code of the python package that was built during the session, as well as the terminal commands used during demos. <br>

This package uses scripts from the LowRankDensity python package developed by the Hi! PARIS Engineering Team. <br>
You can find the **LowRankDensity package** here: https://github.com/hi-paris/Lowrankdensity

<br>

## Demo 1: Build your package locally 💻
### 1. Create a virtual environment with venv
Virtual environments allow you to create isolated environments for different projects, ensuring that each
project has its own set of dependencies/libraries.

```
python -m venv <venv-name>
```

This command will create a virtual environment folder in the directory you are currently in.

### 2. Activate the virtual environment
Now that you have created the virtual environment, you need to activate it using the following command.
```
path\to\venv\<venv-name>\Scripts\activate
```

### 3. Install the build library
Build is a Python packaging build frontend library. It will generate the distribution packages of our
package.
```
pip install build
```

### 4. Build your project
Run the following command in your terminal to build the distribution packages. This command will
generate a dist folder with .whl and .gz files.
```
pyproject-build
```

### 5. Install your package locally
Use pip install to install the package on your computer from the .whl file.
```
pip install ./dist/<whl-file>
```

Additional ressources:
- Virtual environments with venv: https://docs.python.org/3/tutorial/venv.html
- Packaging Python projects (setup.cfg, MANIFEST.in, pyproject.toml): https://packaging.python.org/en/latest/tutorials/packaging-projects/

<br>

## Demo 2: Test your package with pytest 🧪

### 1. Install test and code coverage packages

```
pip install pytest, pytest-cov
```
These packages should be installed in your virtual environment. You can check which packages are
already installed using pip list.


### 2. Run tests on your package with pytest
```
pytest
```
Pytest will directly identify your package’s test files if they follow pytest’s naming convention.


### 3. Run code coverage with pytest-cov
```
pytest --cov
```

**Additional ressources**:
- Pytest documentation: https://docs.pytest.org/en/7.3.x/
- Pytest-cov documentation: https://pytest-cov.readthedocs.io/en/latest/

<br>

## Demo 3: Git commands and Github ⌨️
### 1. Create a public repository on github
https://github.com/


### 2. Clone the github repository to a folder
Git clone: Download the existing source code from a remote repository
```
git clone <HTTPS-key>
```

### 3. Push modifications to your repository with git commands
Github workflow:

1. **Git status**: Check the status of your modifications. With this git command, you can track which
file/folder you’ve modified in the repository.
```
git status
```

2. **Git add**: Add changes to the staging area.
```
git add . # add all modifications to the stagging area
git add <file-directory> # chose a file/folder to add the stagging area
```

3. **Git commit**: Commit the modifications from a staging area to your local repository. Add a message
with git commit to inform other contributors what has been modified on the repository.
```
git commit -m "message"
```

4. **Git push**: Push the commited modifications to the remote repository. This will update the github
repository with the modifications you’ve made on your local repository.
```
git push
```
<br>

If there are many contributors on your projects, you can also create branches to facilitate collaborative
development.
Branches create seperate versions of the main repository. Each contributor can create their own branch,
work on their specific task, and later merge their changes back into the main branch.

```
git branch <name_branch> # create a branch
git merge main # merge modifications from remote branch to the main repository
```

<br>

**Additional ressources**:
- git branch: https://www.w3docs.com/learn-git/git-branch.html

<br>

## Demo 4: Github actions + Package publishing ♻️
Github actions can be triggered by many types of git commands. We used git push in the demo.
Everytime a contributor pushes new code onto the remote repository, github actions will build and test the
package on different operating systems.

### 1. Create an account on PyPi
PyPi is a repository of software for the Python programming language.

https://pypi.org/

### 2. Install twine
Twine allows you to publish Python packages to PyPI and other repositories.
```
pip install twine
```

### 3. Publish your package to PyPi with twine
```
twine upload dist/*
```
The package’s will be published using the information in the setup.cfg file under [metadata].
In this demo, we published a package named lowrankdensity_demo in it’s 0.0.2 version.

**Additional ressources**:
- Github actions documentation: https://docs.github.com/en/actions
- Twine: https://twine.readthedocs.io/en/stable/
- Package versoning: https://py-pkgs.org/07-releasing-versioning.html
# git-demo
