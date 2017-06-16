# Boomslang XML

A simple XML editor created using Python and wxPython. 

This project requires the following:

 - Python 3.5+
 - [wxPython 4+](https://pypi.python.org/pypi/wxPython/4.0.0a3)
 - [lxml](https://pypi.python.org/pypi/lxml/)
 
This project has been tested on Windows 7, Mac OSX Sierra, and Xubuntu 16.04

# Roadmap

The following are features that I'd like to add soon:

 - Allow adding multiline strings in a friendly way
 - View raw XML and be able to edit it
 - Add packaging
 
**Long term goals**:

 - Plugins
 - Diff tool
 
# Known Bugs

 - Nodes cannot have spaces in their names. Not sure if this is fixable yet without doing some research
 - Top level nodes with values aren't editable when expanded to show their children
 - Cannot delete attributes
 - When multiple XML files are open, the current directory isn't saved correctly which can make opening/saving files confusing
