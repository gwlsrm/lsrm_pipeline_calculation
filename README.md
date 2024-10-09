# Monte-Carlo calculation pipeline (with lsrm calculation modules)

## Install

- download code
- copy Lib directory from LSRM EffMaker or NuclideMaster+ to the code root directory
- copy calculation libraries from LSRM EffMaker (response.dll, physspec.dll, ...) or NuclideMaster+ (tccfcalc.dll) to the code root directory
- install python and project dependencies (`python -m pip install -r requirements.txt`)


## Run

- create computation graph in yaml-file (use any from examples/ as a template) in project directory
- copy or create input files for graph to project directory
- run graph:
```
python3 run.py project/project_name/graph_name.yaml
```
