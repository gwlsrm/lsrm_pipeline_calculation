# Task "efficiency of gamma registration for variable distances"

## Description

This pipeline is intended for the task: obtaining efficiencies (efa-file), that can be used in measurements with variable distances.

## Install

- copy this directory to projects
- copy or create input file for physspec.dll or physspec.so (physspec_input.json, can be obtained after run PhysSpec.exe)
- copy or create response output file (response_output.csv, can be obtained after run response.exe)

## Run
1. Calculate efficiencies
- edit graph `01_calc_efficiencies_for_dist.yaml` parameters: input_filename for "SetEffMakerDistanceOperation" operation, `input_response_filename` for "AppspecEfficiencyInputOperation"
- run efficiencies calculation:
```
python run.py projects/effmaker_distance_calc/01_calc_efficiencies_for_dist.yaml
```

You will obtain efficiencies (*.efr) in res subdirectory.

2. Calculate maximum error
- run graph `python run.py projects/effmaker_distance_calc/02_interpolate_efficiency_by_dist.yaml`
- max error will be in `res/max_error.tsv`

3. Create result efa
- edit graph `03_create_result_efa.yaml` parameters:
    set `distance_error` parameter from `res/max_error.tsv`.
- run graph `python run.py projects/effmaker_distance_calc/03_create_result_efa.yaml`
- `efficiency.efa` will be in project directory (projects/effmaker_distance_calc/)
