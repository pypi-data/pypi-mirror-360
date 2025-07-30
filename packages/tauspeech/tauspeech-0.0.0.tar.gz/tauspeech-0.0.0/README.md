# TauSpeech

## Presentation

TauSpeech is a Python module for analyzing and generating articulatory trajectories using general Tau theory [1]. This is the implementation of the method described in [2]. It also contains the implementation of the baseline methods used in [2], namely the Sequential Target Approximation Model [3], and Critically Damped Oscillators [4, 5]. 

## Installation

TauSpeech is implemented with Python3. Tests have been performed with Python 3.9, so consider having a version of Python that is at least as new as Python 3.9.

Please also consider using a Python3 virtual environment during the development stage:
```bash
# create a python 3 virtual environment and activate it
$ python3 -m venv tauspeech_env
$ source tauspeech_env/bin/activate
```

You can get the source codes by cloning this repo with git
```
git clone https://git.ecdf.ed.ac.uk/belie/tauspeech.git

```

PlanArt is not yet on PyPI. You can install it locally in editable mode:
```bash
# install planart locally in editable mode
$ python3 -m pip install -e path_to_tauspeech
```

* WARNING: Please, do not modify anything in the planart folder, unless you want to modify the repository.

## Checking the software behavior
To check if everything runs as expected, run the following command:
```bash
# test if everything works as expected
$ cd path_to_tauspeech
$ pytest tests
```
It should not return any error message

## Running an articulatory analysis
The script `fit_section.py` performs analyses of EMA signals using one of the implemented curve fitting methods. To  launch it:
```bash
# run tauspeech for automatic analysis of ema signals
$ python3 path_to_tauema/scripts/fit_section.py file -o=output.h5 -m=model -sg=gaussian_filtering_order -f=fitted_curve -a=velocity_weight -mx=max_iterations -nr=number_of_run -nj=number_of_parallel_jobs p=parallel_preference  -no=model_order -v=verbosity
```

where
* file is the file containing the signal to analyse
* output.h5 is the file in which results will be written (HDF5 format)
* the option -m defines the model used for curve fitting, to choose between tau, `stam`, `sdo`, and `gcdo`
* the option -sg provides the Gaussian filtering order to smooth both the position and the velocity profile of the analyzed sensors (default is 4)
* the option -f defines the curve to which the fit is done to estimate the k-value of Tau equations (default is position)
* the option -a defines the weight applied to the velocity in the objective function (default is 0 => no velocity weight)
* the option -mx sets the number of iteration for the Nelder-Mead algorithm (default is 200).
* the option -nr sets the number of optimization runs to find the best local minimum (default is 100). Only applies for methods STAM, S-CDO, and G-CDO. 
* the option -nj sets the number of parallel runs to find the best local minimum (default is 1). Only applies for methods STAM, S-CDO, and G-CDO if nr>1.
* the option -p sets type of parallelization (either `processes` or `threads`) (default is `threads`). Only applies for methods STAM, S-CDO, and G-CDO if nr>1 and nj>1.
* the option -no sets the order of the model for STAM (default is 6). Only applies for STAM.
* the option -v defines the level of verbosity (default=0, no display of progress bar).

## Analyzing results

At the end of the analysis, results are stored in an HDF5 file. The file contains all the information to reconstruct the `Trajectory` object. For instance, to retrieve the it from the hdf5 file named `hdf5_file`:

```python
import tauspeech
Traj = tauspeech.import_solution(hdf5_file)
```

Relevant attributes of `Traj` are the following:
* `signal`: original signal
* `filtered_signal`: filtered version of the signal
* `sampling_frequency`: sampling frequency
* `parameters`: `Parameters` object containing the estimated parameters
* `movement_units`: list of the movement units, stored as `Movement` objects
* `sibling`: Other `Trajectory` object containing the generated trajectory parameters

Attributes of parameters are the following:
* `parent`: object to which the estimated parameters are assigned
* `shape`: shape parameter (kappa for Tau, time constant for STAM, and stiffness for CDO)
* `onset`: onset of command unit
* `target`: target of command unit
* `first_activation_step`: position of the first max of the activation windows (applies only for GCDO)
* `second_activation_step`: position of the second max of the activation windows (applies only for GCDO)
* `slope`: slope of the target function (applies only for STAM)
* `local_error`: final cost function (only for movement units)
* `global_error`: final cost function (only for the whole trajectory sequence)

The `Movement` class is a subclass of `Trajectory`. It contains the following additional parameters:
* `parent`: `Trajectory` object to which belong the movement units
* `indices`: start and end indices of the movement unit in relation to the signal of the whole articulatory sequence

### Examples

Examples are available to download [here](https://datashare.ed.ac.uk/handle/10283/4495). It consists of samples of the DoubleTalk corpus [6]. Files are already preprocessed and ready to be fed into TauSpeech. 

**Display the global error of the fit on the whole trajectory sequence:**
```python
print("Global error is ", Traj.parameters.global_error)
```

**Display the estimated the shape parameters of the whole trajectory sequence:** 
```python
print("Estimated shape parameters ", Traj.parameters.shape)
```

**Extract the generated sequence (by the model) and compare with the observed one:**
```python
generated_sequence = Traj.sibling.signal
observed_sequence = Traj.filtered_signal
import matplotlib.pyplot as plt
plt.figure()
plt.plot(generated_sequence)
plt.plot(observed_sequence, '--r')
```

**Compare the modeled movement unit and the observed one (e.g. the 5th), and display the shape parameter:**
```python
generated_movement = Traj.sibling.movement_units[4].signal
observed_movement = Traj.movement_units[4].signal
print("Estimated shape parameter of the 5th movement unit: ", Traj.movement_units[4].parameters.shape)
import matplotlib.pyplot as plt
plt.figure()
plt.plot(generated_movement)
plt.plot(observed_movement, '--r')
```

### Contact

For any additionnal information, please contact Benjamin Elie at benjamin.elie (at) ed.ac.uk

### License

This work is licensed under the Creative Commons Attribution 4.0 International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/.
 
## References

* [1] D. N. Lee, "Guiding movement by coupling taus", *Ecological psychology*, vol. 10, no. 3-4, pp. 221-250, 1998
* [2] B. Elie, D. N. Lee, and A. Turk, "Modeling trajectories fo human speech articulators using general Tau theory", *in prep.*
* [3] P. Birkholz, B. J. Kröger, and C. Neuschaefer-Rube, "Model-based reproduction of articulatory trajectories for consonant-vowel sequences", *IEEE Transactions on Audio, Speech, and Language Processing*, vol. 19, no. 5, pp. 1422-1433, 2010
* [4] E. Saltzman and K. G. Munhall, "A dynamical approach to gestural patterning in speech production", *Ecological psychology*, vol. 1, no. 4, pp. 333-382, 1989
* [5] B. J. Kröger, G. Schröder, and C. Opgen-Rhein, "A gesture-based dynamic model describing articulatory movement data", *The Journal of the Acoustical Society of America*, vol. 98, no. 4, pp. 1878-1889, 1995
* [6] J. M. Scobbie *et al.*, "The Edinburgh speech production facility DoubleTalk corpus", in Interspeech, 2013

