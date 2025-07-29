# pycopy

This tool was made as a simple python library for syncing files. It also works famously as a simple cli for doing the same thing.

### Usage as library
```python
import pycopy

pycopy.sync("path/to/directory1", "path/to/directory2")
```

To make it also delete files:
```python
import pycopy

pycopy.sync("path/to/directory1", "path/to/directory2", do_delete=True)
```

### Usage as command
First install the library as a command, usually like so:
```bash
pipx install pycopy
```

Then simply execute the command using:
```bash
pycopy "path/to/directory1" "path/to/directory2" 
```

To make it also delete files:
```bash
pycopy -d "path/to/directory1" "path/to/directory2" 
```