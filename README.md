### Clang Function Extractor
Introduction: this tool is used mainly to extract all single functions under specified 
input-filepath or input-dirpath, and stores per function extracted into the single file.

#### Basic Usage
```text
usage: extractor.py [-h] [-f [INPUT_FILE [INPUT_FILE ...]]] [-d [INPUT_DIR]]
                    [-D OUTPUT_DIR] [--clear_output_dir]

A parser used to extract all clang functions in specified file dir or c/cpp
files.

optional arguments:
  -h, --help            show this help message and exit
  -f [INPUT_FILE [INPUT_FILE ...]], --input_files [INPUT_FILE [INPUT_FILE ...]]
                        Specifies which files will be used to extract.
  -d [INPUT_DIR], --input_dir [INPUT_DIR]
                        Specifies which dir will be used to extract.
  -D OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Specifies the dir at which all extracted results would
                        be stored.
  --clear_output_dir    Means if clear all files under output dir before
                        extract.
```

#### Basic steps in extraction
1. get all files to specified input filepaths or dir path
2. filter all files ending in (.c, .h)
3. do a function-extraction to per clang source file.
    1. remove all notes.
    2. remove all macro definitions.
    3. extract all function existing in the source file by using specified regulation, 
        and strip all empty spaces surrounding the function.
