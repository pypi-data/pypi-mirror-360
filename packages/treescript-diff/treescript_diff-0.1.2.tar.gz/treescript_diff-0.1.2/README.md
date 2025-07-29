# TreeScript Diff
Quickly, find the differences between two TreeScript files!

## Introduction
A Command Line app for comparing TreeScript files, similar to `git diff`.
- Both files must be correctly formatted TreeScript
- Diff output options are provided

## Usage
This package expects two input files, both must be valid TreeScript.

```bash
treescript-diff [options] <file1> <file2>
```

The first file is considered the original, the second file is updated TreeScript.

The program 

### Default Diff Output
The program will return the additions and removals in this structure:
1. newly added files separated by newline character
2. blank line
3. removed files separated by newline character

### Additions Only
To print only added files.

Use the option: `--added` or `-a`

```bash
treescript-diff -a <file1> <file2>
```

### Removals Only
To print only removed files.

Use the option: `--removed` or `-r`

```bash
treescript-diff -r <file1> <file2>
```
