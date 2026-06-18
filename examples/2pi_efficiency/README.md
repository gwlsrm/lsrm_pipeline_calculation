# Calculate efficiency for 2pi geometry

## Description

This pipeline is intended for the task: obtaining special efficiency for 2pi geometry from efficiency for point geometry.
The 2pi special efficiency 'eff' can be used for special activity calculation like:
$$
A_{special} = \frac {N} {eff * I * t}
$$
where `A_special` -- activity in Bq/kg, `N` -- peak area, `I` -- line intensity, `t` -- time, s

Special efficiency is calculated by formula:
$$
\varepsilon_{special} = \frac {\varepsilon_0 r^2 2 \pi} {\mu(E)}
$$
where `epsilon_0` -- point efficiency, `r` -- point-detector distance, cm, `mu` -- mass att. coeff. for material, cm^2/g


## Install

- create "projects" directory in project root directory
- copy this directory to "projects"
- put efa-file with point efficiency section to "projects/2pi_efficiency"

## Run
- edit confug `create_2pi_efficiency.yaml` parameters:
    - "EfrFromEfaOperation" operation
        - put efa-file with point efficiency to `input_filename`,
        - put point efficiency section to `section_name`,
        - edit energy_grid,
    - "ExtendedObjectEfficiencyOperation" operation
        - put point distance from point efficiency to `distance`
        - put material formula to `material_formula`, e.g. H2O1 ("1" is crucial)
        - or put material as json-string to `material_json` (look in example create_2pi_efficiency.yaml)
    - "EfrUpdateFromTsvOperation" operation
        - put desirable output filename to `output_filename`,
- run efficiencies calculation from terminal (command line):
```
python run.py projects/2pi_efficiency/create_2pi_efficiency.yaml
```

You will obtain efficiency (*.efr) for 2pi geometry in res subdirectory with filename as in `output_filename` in "EfrUpdateFromTsvOperation".
