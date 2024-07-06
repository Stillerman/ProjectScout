import os
import click
import tiktoken
import pathspec
import magic
import json

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
    return True
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

def print_directory_structure(directory, patterns, level=0, include_tokens=False, include_content=False, track_large=False, n=10, dump_file=None):
    total_tokens = 0
    indent = ' ' * 4 * level
    print(f"{indent}{os.path.basename(directory)}/")

    subindent = ' ' * 4 * (level + 1)
    large_files = []
    file_data = []

    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(root, d, patterns)]
        files = [f for f in files if not should_ignore(root, f, patterns)]
        
        for f in files:
            file_path = os.path.join(root, f)
            if is_text_file(file_path) and not is_large_file(file_path):
                content = read_file(file_path)
                token_count = count_tokens(content) if include_tokens else None
                file_type = magic.Magic(mime=True).from_file(file_path)
                
                if dump_file:
                    file_data.append({
                        "path": os.path.abspath(file_path),
                        "contents": content,
                        "type": file_type
                    })
                
                if include_tokens:
                    total_tokens += token_count
                    print(f"{subindent}{f} - {token_count} tokens")
                    if track_large:
                        large_files.append((file_path, token_count))
                else:
                    print(f"{subindent}{f}")
                
                if include_content:
                    print(f"{subindent}Contents:\n{subindent}{content}")

        for d in dirs:
            subdir_path = os.path.join(root, d)
            subdir_tokens, subdir_large_files, subdir_file_data = print_directory_structure(subdir_path, patterns, level + 1, include_tokens, include_content, track_large, n, dump_file)
            total_tokens += subdir_tokens
            if track_large:
                large_files.extend(subdir_large_files)
            if dump_file:
                file_data.extend(subdir_file_data)

        break  # Prevent os.walk from going into subdirectories again

    if include_tokens:
        print(f"{indent}Total tokens in folder: {total_tokens}")

    if track_large:
        large_files = sorted(large_files, key=lambda x: x[1], reverse=True)[:n]

    return total_tokens, large_files, file_data

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--tokens', is_flag=True, help="Include token counts for each file")
@click.option('--content', is_flag=True, help="Include contents of each file")
@click.option('--large', '-l', type=int, default=0, help="Show the top N largest files with the most tokens")
@click.option('--dump', type=click.Path(), help="Dump file information to a JSON file")
def overview(directory, tokens, content, large, dump):
    """Print the directory structure with optional token counts and contents."""
    patterns = load_gitignore_patterns(directory)
    _, large_files, file_data = print_directory_structure(directory, patterns, include_tokens=tokens, include_content=content, track_large=(large > 0), n=large, dump_file=dump)
    
    if large > 0:
        print("\nTop {} largest files with the most tokens:".format(large))
        for file_path, token_count in large_files:
            print(f"{file_path} - {token_count} tokens")
    
    if dump:
        with open(dump, 'w', encoding='utf-8') as json_file:
            json.dump(file_data, json_file, indent=4)
        print(f"File information dumped to {dump} ({len(file_data)} files)")

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.argument('pattern', type=str)
def search(directory, pattern):
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
@click.argument('file_path')
@click.argument('content', nargs=-1)
def modify(file_path, content):
    """Modify the content of a file."""
    content = ' '.join(content)
    with open(file_path, 'w') as f:
        f.write(content)
    return f"File {file_path} has been modified with content: {content}"

if __name__ == '__main__':
    cli()
