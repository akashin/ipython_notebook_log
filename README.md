# IPython Notebook extension that enables logging on inputs/outputs of cells to log file

## Usage example

Write this in the ipython cell to activate logging:
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
