# Calculate efficiency for 2pi geometry

## Description

This pipeline is intended for the task: obtaining efficiency for 2pi geometry from efficiency for point geometry.

## Install

- copy this directory to projects
- copy efa-file with point efficiency section

## Run
- edit graph `create_2pi_efficiency.yaml` parameters:
    - "EfrFromEfaOperation" operation
        - put efa-file with point efficiency to `input_filename`,
        - put point efficiency section to `section_name`,
        - edit energy_grid,
    - "ExtendedObjectEfficiencyOperation" operation
        - put point distance from point efficiency to `distance`
        - put material formula to `material`, e.g. H2O1 ("1" is crucial)
    - "EfrUpdateFromTsvOperation" operation
        - put desirable output filename to `output_filename`,
- run efficiencies calculation:
```
python run.py projects/2pi_efficiency/create_2pi_efficiency.yaml
```

You will obtain efficiency (*.efr) for 2pi geometry in res subdirectory with filename as in `output_filename` in "EfrUpdateFromTsvOperation".
