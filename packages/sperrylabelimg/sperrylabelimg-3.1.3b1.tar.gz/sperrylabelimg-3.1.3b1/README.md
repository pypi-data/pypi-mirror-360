# customLabelImg


## Setup

download this repository

```
cd existing_repo
git remote add origin https://gitlab.com/bGerma/customlabelimg.git
git branch -M main
git push -uf origin main
```

install labelimg ***in a virtual environment*** so that it doesn't get confused with your normal version

```
(.venv) ~\User> pip install labelimg
```

Then, go into this file in your virtual environment folder and make these changes:

`.\venv\Lib\site-packages\libs\stringBundle.py`

Changes:

Go to the class StringBundle, go inside its __init__ method, find the initialization of the id_to_message
attribute and add this to it:

```
self.id_to_message = {
    "openMultipleDirs": "Open Multiple\nDirs",
    "setWriteDir": "Set Write Dir"
}
```

Now, you should be able to run any version of the script in the project directory
