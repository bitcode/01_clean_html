# Clean HTML Pipeline

This repository contains a script to clean and extract metadata from HTML files. The script performs the following tasks:

## Features

- Extract metadata, sections, links, code blocks, and images from HTML files.
- Skip large files and log errors.
- Handle and log skipped files for further processing.

## Usage

### Running the Script

To run the script, use the following command:

```bash
python3 main.py
```

### Directory Structure

- `main.py`: The main script to process HTML files.
- `venv/`: The virtual environment directory.

## Tools and Commands

1. **Delete All Files Except `main.py` and `venv` Directory**

This command deletes all files and directories except for `main.py` and the `venv` directory:

```bash
find . -mindepth 1 ! -regex './main.py\|./venv\(/.*\)?' -delete
```

2. **Watch and Tail Log File**

This command continuously watches and displays the last 20 lines of the `app.log` file:

```bash
watch -n 1 tail -n 20 app.log
```

3. **Multi Clip**

This alias/script copies all the contents of the current directory, gathers them under one file, and copies all the contents to the clipboard:

```bash
multi_clip -i ignore_list.txt .
```
