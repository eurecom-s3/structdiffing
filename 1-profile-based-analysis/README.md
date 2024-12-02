# Profile based analysis
- Inside ```./1-profile-based-analysis```
- Download the dataset from [https://www.s3.eurecom.fr/datasets/datasets/applications/12:2024_12:2024_andrea_structdiff/profiles_dataset.tar](https://www.s3.eurecom.fr/datasets/datasets/applications/12:2024_12:2024_andrea_structdiff/profiles_dataset.tar)
- Extract it in a directory called ```dataset```

## Run the analysis
- Run the tool to generate diffings among profiles (it requires 30/40 minutes,
  you can run the three commands in parallel in three different shells)
    - ```./profile_differ.py -no-beta -lnx ./dataset/debian/```
    - ```./profile_differ.py -no-beta -xnu ./dataset/macOS/```
    - ```./profile_differ.py -no-beta -win ./dataset/windows/```

- To run data analysis run ```./analysis.py``` from the virtual environment, results will be print on the screen and two PDF files will be generated.
