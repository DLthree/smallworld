import os

def list_files_recursive(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        files = [os.path.join(root, f) for f in files if not f.startswith('.')]
        all_files.extend(files)
        # don't visit hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
    return all_files

def list_dirs(path):
    root, dirs, files = next(os.walk(path))
    return [os.path.join(root, f) for f in dirs if not f.startswith('.')]
