# DiffingToolC

## Description

This is a tool for analyzing C structs and diffing them semantically.

When simply analyzing, it will a JSON structure per structure that contains the following info:
* struct name
* struct fields
* for each individual field it will contain information such as:
* * type
* * is it a pointer
* * is it an array
* * array size
* * ifdefs associated with this field

If used for diffing it will output differences such as:
* field removal
* field addition
* field change (change of type, change of size)
* field position change
* changes in ifdefs

## How to run

### Analysis mode

Analysis mode is the mode used to generate the results for the paper. It takes the result folder of the previous phase of extracting all structs per kernel version and outputs similarly structured files but with parsed structs instead. It does no diffing, only parsing of all of the extracted structs.

It requires 20 hours to complete. If you do not want to wait, use the preprocessed results contained into the dataset of stage ```1-struct_extractor``` and ignore the next command.
To run struct large-scale struct analysis simply run

```script
mkdir ../output_2
python analyze.py -i ../output -o output_2
```