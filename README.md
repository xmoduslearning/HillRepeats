# Hill Repeats - a sample research project

A Python project to locate and extract cycling computer information from interval training on hills (hill repeats).  Takes as input a tab-delimited activity file and the GPS locations for the start and stop positions and then outputs each interval as a CSV file and a summary as a tab-delimited file.

This is a sample Python research project used to simulate the taking over or structuring of a research software project.  This project is intentionally verbose with comments and some sub-optimal programming strategies so we can review them in class and adjust them as part of the hands-on portion of the seminar.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This is a basic Python 3 project with only standard library imports.

```
Python 3.6+
```

### Running HillRepeats.py

HillRepeats.py is a command-line script that takes an activity file and the name of a hill that this activity file contains interval training sessions for.  See the data/activities folder for sample activities.  Currently all actitivies are for a hill near UBC, which is called "ubc" in the configuration.

```
python HillRepeats.py ../data/activities/ubc_hill_repeats_2013-09-23.txt ubc
```

Note: On systems with both Python 2 and Python 3 installed, for example, macOS, you may need to call the script with "python3" instead of just "python".

To test your version use "python -V".
```
python -V
```

Calling the script with python3 explicitly.
```
python3 HillRepeats.py ../data/activities/ubc_hill_repeats_2013-09-23.txt ubc
```

After successfully running this script (from the src folder) you should see the following new files:

```
data/intervals/ubc_hill_repeats_2013-09-23.txt_interval_0.csv
data/intervals/ubc_hill_repeats_2013-09-23.txt_interval_1.csv
data/intervals/ubc_hill_repeats_2013-09-23.txt_interval_2.csv
data/intervals/ubc_hill_repeats_2013-09-23.txt_interval_3.csv
data/intervals/ubc_hill_repeats_2013-09-23.txt_summary.txt
```

The "interval" files are CSV files with the individual data points.  The "summary" file contains a set of summary metrics for all of the intervals found.

## Running the tests

A set of tests for some of the helper-functions are shown to illustrate some basic unit tests that can be built when refactoring the code.
All tests are in the "tests" folder and currently use the built-in unittester class.  To run the tests, run the tests as a Python script.

```
python test_helper_functions.py
```

All test documentation is contained within the test's .py file.

## Authors

* **Chris Kerslake** - *Initial work* - [XModusLearning](https://github.com/XModusLearning)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [SFU SciProg](http://sciprog.ca/) for inviting me to give a seminar to research students at SFU
* The template for this README.md was provided by: https://gist.github.com/PurpleBooth/109311bb0361f32d87a2/