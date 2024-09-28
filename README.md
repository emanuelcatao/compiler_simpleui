# Compiler SimpleUI

## Overview

Compiler SimpleUI is supposed to be a Python-based compiler that transposes our custom language into a format that can be executed by a GCC compiler.

## Features

- Translates custom language to GCC-compatible code
- Written in Python for ease of use and flexibility
- Supports various language constructs and syntax

## Requirements

- Python 3.x
- GCC compiler

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/compiler_simpleui.git
    ```
2. Navigate to the project directory:
    ```sh
    cd compiler_simpleui
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Write your code in the custom language.
2. Run the compiler:
    ```sh
    python compiler.py input_file.lang
    ```
3. Compile the generated code with GCC:
    ```sh
    gcc output_file.c -o output_executable
    ```
4. Run the executable:
    ```sh
    ./output_executable
    ```

## The language

The language definition can be consulted in [General Definitions](./definicao_geral_simpleui.pdf).
