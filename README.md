# IPython Notebook extension for logging progress

This extension enables logging of inputs and outputs of ipython notebook cells to the log file.

When you execute the cell, it's content and everything it prints will get printed to a specified file.

## Usage example

To activate logging you first need to download the notebook_log.py file and put it into .ipython/extensions folder:
```bash
curl https://raw.githubusercontent.com/akashin/ipython_notebook_log/master/notebook_log.py > ~/.ipython/extensions/notebook_log.py
```

Then, write this in the ipython cell of your notebook to activate logging:
```python
%load_ext notebook_log
%register_logging ~/log_file.txt
```

To activate the extension on startup add this to your ipython profile file
(by default it's located at ~/.ipython/profile_default/ipython_config.py)

```python
c.InteractiveShellApp.extensions = [
    'notebook_log'
]
```
