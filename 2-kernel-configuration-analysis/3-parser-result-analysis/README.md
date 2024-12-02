# Parser Output Analysis

## Description

This repository contains all the scripts that take the JSON data provided by our custom parser and parse it into formats that are better for direct analysis (CSV files).

The repository behaves like a pipeline, where certain steps rely on the results of previous ones.

The following steps are part of the pipeline:
* Filtering out anonymous structs
* Calculating the size of all structs
* * While the parser parses individual structs, it makes no attempt to calculate their size (since they can reference other structs as well)
* * **pipeline/size_calculator.py** contains an algorithm that calculates the size of all structs, for which it is possible, based on the data previously provided from the parser
* 4 different CSV stat files are generated
* * General stats file
* * * This file contains general info regarding invidual structs, such as: number of fields, number of pointers, number of ifdefs
* * Embedded structs file
* * * This CSV file presents the embedded relationships between structs
* * Ifdef CSV stats
* * * This file presents for each struct, from what ifdefs it depends, even in an inherited matter (from embedded underlying structs)
* * Ifdef per field CSV file
* * * This struct presents for each struct, which fields are dependent on which ifdef. However, this stats file is not recursive (it does not go bellow embedded structs)
* The final file to be generated is a diff stats CSV
* * This CSV file represents the differences all structs go through, in successive kernel versions

## How to Run

To run these scripts, it is only necessary to provide the path to the folder containing the output JSON files of the previous styep as so

```bash
python main.py -i <path_to_folder>
```

Run the script

```python main.py -i ../output_2/```

On a machine with 16 GBs of ram and a Intel(R) Core(TM) i7-8650U CPU @ 1.90GHz CPU the whole processing takes aproximately 2 hours.