import os
import click
import tiktoken
import pathspec
import magic

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

def is_text_file(file_path):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type.startswith('text')

def is_large_file(file_path):
    return os.path.getsize(file_path) > 1 * 1024 * 1024  # 1 MB

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

@click.group()
def cli():
    pass

def should_ignore(root, path, patterns):
    """Helper function to determine if a path should be ignored based on .gitignore patterns."""
    relative_path = os.path.relpath(os.path.join(root, path), start=root)
    return patterns.match_file(relative_path)

def print_directory_structure(directory, patterns, level=0, track_large=False, n=10):
    total_tokens = 0
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(directory)}/")

    subindent = ' ' * 4 * (level + 1)
    large_files = []

    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(root, d, patterns)]
        files = [f for f in files if not should_ignore(root, f, patterns)]
        
        for f in files:
            file_path = os.path.join(root, f)
            if is_text_file(file_path) and not is_large_file(file_path):
                content = read_file(file_path)
                token_count = count_tokens(content)
                total_tokens += token_count
                print(f"{subindent}{f} - {token_count} tokens")
                if track_large:
                    large_files.append((file_path, token_count))

        for d in dirs:
            subdir_path = os.path.join(root, d)
            subdir_tokens, subdir_large_files = print_directory_structure(subdir_path, patterns, level + 1, track_large, n)
            total_tokens += subdir_tokens
            if track_large:
                large_files.extend(subdir_large_files)

        break  # Prevent os.walk from going into subdirectories again

    print(f"{indent}Total tokens in folder: {total_tokens}")

    if track_large:
        large_files = sorted(large_files, key=lambda x: x[1], reverse=True)[:n]

    return total_tokens, large_files

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--large', '-l', type=int, default=0, help="Show the top N largest files with the most tokens")
def print_tokens(directory, large):
    """Print the directory structure with token counts."""
    patterns = load_gitignore_patterns(directory)
    _, large_files = print_directory_structure(directory, patterns, track_large=(large > 0), n=large)
    
    if large > 0:
        print("\nTop {} largest files with the most tokens:".format(large))
        for file_path, token_count in large_files:
            print(f"{file_path} - {token_count} tokens")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def print_structure(directory):
    """Print the directory structure."""
    patterns = load_gitignore_patterns(directory)
    print_filtered_structure(directory, patterns)

def print_filtered_structure(directory, patterns, level=0):
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(directory)}/")
    
    subindent = ' ' * 4 * (level + 1)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories and files
        dirs[:] = [d for d in dirs if not should_ignore(root, d, patterns)]
        files = [f for f in files if not should_ignore(root, f, patterns)]

        for f in files:
            file_path = os.path.join(root, f)
            if is_text_file(file_path) and not is_large_file(file_path):
                print(f"{subindent}{f}")

        for d in dirs:
            print_filtered_structure(os.path.join(root, d), patterns, level + 1)
        
        break  # Prevent os.walk from going into subdirectories again

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def print_all(directory):
    """Print the folder structure and file contents."""
    patterns = load_gitignore_patterns(directory)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories and files
        dirs[:] = [d for d in dirs if not should_ignore(root, d, patterns)]
        files = [f for f in files if not should_ignore(root, f, patterns)]

        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")

        subindent = ' ' * 4 * (level + 1)
        for f in files:
            file_path = os.path.join(root, f)
            if is_text_file(file_path) and not is_large_file(file_path):
                print(f"{file_path}")
                content = read_file(file_path)
                print(f"{subindent}Contents:\n{subindent}{content}")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.argument('pattern', type=str)
def search_project(directory, pattern):
    """Search for a pattern in the entire project."""
    patterns = load_gitignore_patterns(directory)
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories and files
        dirs[:] = [d for d in dirs if not should_ignore(root, d, patterns)]
        files = [f for f in files if not should_ignore(root, f, patterns)]

        for f in files:
            file_path = os.path.join(root, f)
            if is_text_file(file_path) and not is_large_file(file_path):
                content = read_file(file_path)
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
