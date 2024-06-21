import os
import click
import tiktoken
import pathspec

# Initialize the tokenizer for GPT-4
enc = tiktoken.encoding_for_model("gpt-4")

def count_tokens(text):
    tokens = enc.encode(text)
    return len(tokens)

def load_gitignore_patterns(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    if not os.path.exists(gitignore_path):
        return pathspec.PathSpec.from_lines('gitwildmatch', [])
    
    with open(gitignore_path, 'r') as f:
        lines = f.readlines()
    
    return pathspec.PathSpec.from_lines('gitwildmatch', lines)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def print_structure(directory):
    """Print the directory structure."""
    patterns = load_gitignore_patterns(directory)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored files and directories
        dirs[:] = [d for d in dirs if not patterns.match_file(os.path.join(root, d))]
        files = [f for f in files if not patterns.match_file(os.path.join(root, f))]
        
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def print_tokens(directory):
    """Print the directory structure with token counts."""
    patterns = load_gitignore_patterns(directory)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored files and directories
        dirs[:] = [d for d in dirs if not patterns.match_file(os.path.join(root, d))]
        files = [f for f in files if not patterns.match_file(os.path.join(root, f))]

        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        folder_token_count = 0
        print(f"{indent}{os.path.basename(root)}/")

        subindent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                token_count = count_tokens(content)
                folder_token_count += token_count
                print(f"{subindent}{f} - {token_count} tokens")

        print(f"{indent}Total tokens in folder: {folder_token_count}")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def print_all(directory):
    """Print the folder structure and file contents."""
    patterns = load_gitignore_patterns(directory)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored files and directories
        dirs[:] = [d for d in dirs if not patterns.match_file(os.path.join(root, d))]
        files = [f for f in files if not patterns.match_file(os.path.join(root, f))]

        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")

        subindent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            print(f"{subindent}{f}")
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"{subindent}Contents:\n{subindent}{content}")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.argument('pattern', type=str)
def search_project(directory, pattern):
    """Search for a pattern in the entire project."""
    patterns = load_gitignore_patterns(directory)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored files and directories
        dirs[:] = [d for d in dirs if not patterns.match_file(os.path.join(root, d))]
        files = [f for f in files if not patterns.match_file(os.path.join(root, f))]

        for f in files:
            file_path = os.path.join(root, f)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if pattern in content:
                    print(f"Found in {file_path}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('content', type=str)
def modify_file(file_path, content):
    """Modify a file with new content."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Modified {file_path}")

if __name__ == '__main__':
    cli()