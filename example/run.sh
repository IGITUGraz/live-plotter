#!/usr/bin/env bash

# This script runs both the files simulation.py and plot.py separately.
# The idea is that you can start/stop plotting while the simulation continues to run independently


# The following line is needed to put the `liveplotter` python package in the PYTHONPATH so it can be
# accessed from `simulation.py` and `plot.py`. If the package was installed using setup.py, this is not needed.
export PYTHONPATH=..:$PYTHONPATH

python -u plot.py &
python -u simulation.py &
