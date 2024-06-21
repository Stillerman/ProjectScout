# ProjectScout

ProjectScout is a library designed to prepare a codebase for ingestion with an LLM. It provides tools to analyze directory contents, offering insights into file structures, token counts, and more.

## Features

- **Overview:** Print the directory structure with optional token counts and file contents.
- **Search:** Search for a specific pattern within the entire project.
- **Modify:** Modify the contents of a specified file.

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/stillerman/ProjectScout
    cd ProjectScout
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Basic Commands

1. **Overview:**
    ```sh
    python cli.py overview [DIRECTORY] [OPTIONS]
    ```
    Options:
    - `--tokens` : Include token counts for each file.
    - `--content` : Include contents of each file.
    - `--large, -l [N]` : Show the top N largest files with the most tokens.
    
    Example:
    ```sh
    python cli.py overview ./my_project --tokens --content --large 5
    ```

2. **Search:**
    ```sh
    python cli.py search [DIRECTORY] [PATTERN]
    ```

    Example:
    ```sh
    python cli.py search ./my_project "TODO"
    ```

3. **Modify:**
    ```sh
    python cli.py modify [FILE_PATH] [CONTENT]
    ```

    Example:
    ```sh
    python cli.py modify ./my_project/file.txt "New content for the file."
    ```

## Detailed Description

### Token Counting
ProjectScout uses the GPT-4 tokenizer to count tokens in text files. This feature helps in identifying the token distribution across files, which is particularly useful for projects involving natural language processing and machine learning.

### Directory Structure Printing
This library can print the directory structure of a given directory. It can also include token counts for each file and display the contents of the files. This makes it easier to get an overview of the project's structure and content.

### Project Search
You can search for specific patterns within the project, making it easy to locate references to certain functions, variables, or comments across the codebase.

### File Modification
ProjectScout also includes a command to modify the contents of a specified file, allowing for quick updates and changes directly from the command line.

## Contributing
We welcome contributions! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to the existing style and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any questions or feedback, please open an issue on the GitHub repository.

---

**Enjoy using ProjectScout!** 🚀