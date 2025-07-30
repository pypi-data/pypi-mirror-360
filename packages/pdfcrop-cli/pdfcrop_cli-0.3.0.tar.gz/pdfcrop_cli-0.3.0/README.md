# pdfcrop

An experimental alternative of TeX/pdfcrop tool

## Install from source

```shell
pip install git+https://github.com/Jordan-Haidee/pdfcrop.git
```

## Install from PyPI
```shell
pip install pdfcrop-cli
```

## Usage

```shell
$ pdfcrop.exe --help
usage: pdfcrop [-h] [OPTIONS]

╭─ options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮  
│ -h, --help              show this help message and exit                                                                                        │  
│ --input PATH, -i PATH   The input pdf file. (required)                                                                                         │  
│ --output {None}|PATH, -o {None}|PATH                                                                                                           │  
│                         The output path. (default: None)                                                                                       │  
│ --pages {None}|{[INT [INT ...]]}                                                                                                               │  
│                         The page numbers to crop. None denotes all pages. (default: None)                                                      │  
│ --margins {None}|{[INT [INT ...]]}                                                                                                             │  
│                         The margins to reserve. None denotes all 0. If one number is given, it will be applied to four borders. (default:      │  
│                         None)                                                                                                                  │  
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯ 
```

You can use `examples/example.pdf` to test whether pdfcrop works.
