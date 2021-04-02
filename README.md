### Clang Function Extractor/Retriever
Introduction: this tool is used mainly to extract/retrieve all single functions under specified 
input-filepath or input-dirpath, and stores per function extracted into the single file under specified output dir.
Besides, some extra features such extracted functions abstraction and normalization are also supported.

#### Basic Usage
```text
usage: extractor.py [-h] [-f [INPUT_FILE [INPUT_FILE ...]]] [-d [INPUT_DIR]]
                    [-D OUTPUT_DIR] [--clear_output_dir] [-a]
                    [--alv ABSTRACTION_LEVEL] [-N]

A extractor used to extract all clang functions in specified file dir or c/cpp
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
  -a                    Abstract the function result extracted use the
                        specified abstraction level, default lv3.
  --alv ABSTRACTION_LEVEL
                        Specify abstraction level, default lv3.
  -N                    Normalize the function result extracted.
```

#### Basic steps in extraction
1. get all files from specified input filepaths or dir path
2. filter all files ending in (.c, .h)
3. do a function-extraction to per clang source file.
    1. remove all notes.
    2. remove all macro definitions.
    3. extract all function existing in the source file by using specified regulation, 
        and strip all empty spaces surrounding the function.
    4. store per function-extracted into different file.
#### Extra Features
1. extracted functions abstraction
    
    to extracted functions, sometimes, we want to its abstract prototype.

    e.g.
    ```cpp
    // Level 0: No abstraction.
    void avg (float arr[], int len) {
        static float sum = 0;
        unsigned int i;
        for (i = 0; i < len; i++);
            sum += arr[i];
        printf("%f %d",sum/len,validate(sum));
    }
    // Level 1: Formal parameter abstraction.
    void avg (float FPARAM[], int FPARAM) {
        static float sum = 0;
        unsigned int i;
        for (i = 0; i < FPARAM; i++)
            sum += FPARAM[i];
        printf("%f %d",sum/FPARAM,validate(sum);
    }
    // Level 2: Local variable name abstraction.
    void avg (float FPARAM[], int FPARAM) {
        static float LVAR = 0;
        unsigned int LVAR;
        for (LVAR = 0; LVAR < FPARAM; LVAR++)
         LVAR += FPARAM[LVAR];
        printf("%f %d",LVAR/FPARAM,validate(LVAR));
    }
    // Level 3: Function call abstraction.
    void avg (float FPARAM[], int FPARAM) {
        static float LVAR = 0;
        unsigned int LVAR;
        for (LVAR = 0; LVAR < FPARAM; LVAR)
            LVAR += FPARAM[LVAR];
        FUNCCALL("%f %d",LVAR/FPARAM,FUNCCALL(LVAR));
    }
    ```
    
    use this feature by add the opt '-a', and specify abstraction level by adding opt '--alv N',
    and level should in {0, 1, 2, 3}.

2. extracted functions normalization

    by removing the comments, whitespaces, tabs, and line feed characters,
    and by converting all characters into lowercase. 
    
    use this feature by add the opt '-N'