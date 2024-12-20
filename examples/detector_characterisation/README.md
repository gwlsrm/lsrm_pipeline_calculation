# Detector Characterisation

## Characterisation with precalculated coefficients

This method uses precalculated dependencies of efficiency from detector geometry parameters. The approximated dependency coefficients are saved to json-files with names like `coeffs_{DETECTOR_GEOMETRY}_{DETECTOR_MATERIAL}_{POINT_DISTANCE}cm.json`. So this method is limited to theese detectors and point distances for characterisation.
The characterisation procedure finds the best estimates for 3 detector parameters: crystal height, crystal diameter and some filter thickness before detector (e.g. dead layer).

**For characterisation you need to have**:
- experimental efficiency of point source: efa-file (detector-source distance must be from precalculated coeffs files),
- in-file with detector initial parameters, can be created from the detector passport.
- energy grid in Lib must be set to 50-2000keV, 10 points, log.

**Run characterisation**:
- copy example yaml-config to your project directory, e.g.: `projects\detector_characterisation`,
- edit characterisation config `find_best_init_params_precalculated.yaml`: paste there names of your experimental efficiency and in- files,
- run calculation from the source code main directory:
```bash
python run.py projects\detector_characterisation\find_best_init_params_precalculated.yaml
```
for linux or
```
python run.py projects/detector_characterisation/find_best_init_params_precalculated.yaml
```
for windows.

You will see the relative maximum deviation of the calculated efficiency of the characterised detector from experimental efficiency in console output.
Characterised detector parameters will be saved to in-files you pass in yaml-config, e.g. `res/Gem15P4-70_optimized.din` in example.
