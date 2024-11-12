# Monte-Carlo calculation pipeline (with lsrm calculation modules)

## Install

- download code
- copy Lib directory from LSRM EffMaker or NuclideMaster+ (or both) to the code root directory
- copy calculation libraries from LSRM EffMaker (response.dll, physspec.dll, ... or *.so in linux) or NuclideMaster+ (tccfcalc.dll or libtccfcalc.so) to the code root directory
- install python and project dependencies (`python -m pip install -r requirements.txt`)


## Run

- create computation graph in yaml-file (use any from `examples/` as a template) in `project` directory
- copy or create input files for the graph to the project directory
- run graph:
```
python3 run.py project/project_name/graph_name.yaml
```

It's a good idea to create a new directory for every your project in `project` directory.


## Operations

All operations are in `operations/` directory, one file -- one operation. Every operation has a description in its own file (doc-string). Also you can find the operation's input parameters in its `__init__` method.
