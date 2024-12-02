

## Setup environment
- NOTE: the extraction process is not optimized and it is really slow, requiring approximately ***10 DAYS***, we suggest to use precomputed dataset available at [https://www.s3.eurecom.fr/datasets/datasets/applications/12:2024_12:2024_andrea_structdiff/preextracted_structs.7z](https://www.s3.eurecom.fr/datasets/datasets/applications/12:2024_12:2024_andrea_structdiff/preextracted_structs.7z) in that case download the file and extract the folders in ```2-kernel-configuration-analysis``` and ignore next steps
- `cd ./1-struct_extractor`
- Clone Linux repository `git clone https://github.com/torvalds/linux.git`

## Runing the extractor
- Command line arguments:
    - `-mt` to run make tags
    - `sj` to run extraction from editor tags
    - `-l` path to linux repository
    - `-o` output path
    - `-s` run a sample of three linux kernel versions
- Run: `python3 extract.py -mt -sj -l ./linux -o ./output`

