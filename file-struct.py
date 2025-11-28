import os
import sys
from pathlib import Path

# Fix Windows console encoding issue
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def explore_folder_structure(root_dir, output_file='folder_struct.txt', max_files=3):
    """
    Explore and display folder structure recursively.
    
    Args:
        root_dir: Root directory to explore
        output_file: Output text file name
        max_files: Maximum number of files to display per folder (default: 3)
    """
    
    def print_tree(directory, prefix="", file_handle=None):
        """Recursively print directory tree structure."""
        try:
            entries = sorted(os.listdir(directory))
        except PermissionError:
            output = f"{prefix}[Permission Denied]"
            print(output)
            if file_handle:
                file_handle.write(output + "\n")
            return
        
        # Separate directories and files
        dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
        files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
        
        # Print directories first
        for i, dir_name in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and len(files) == 0
            connector = "└── " if is_last_dir else "├── "
            output = f"{prefix}{connector}{dir_name}/"
            
            # Safe print with encoding fallback
            try:
                print(output)
            except UnicodeEncodeError:
                print(output.encode('ascii', 'replace').decode('ascii'))
            
            if file_handle:
                file_handle.write(output + "\n")
            
            # Recursively explore subdirectory
            extension = "    " if is_last_dir else "│   "
            new_prefix = prefix + extension
            print_tree(os.path.join(directory, dir_name), new_prefix, file_handle)
        
        # Print files (limit to max_files)
        files_to_show = files[:max_files]
        remaining_files = len(files) - max_files
        
        for i, file_name in enumerate(files_to_show):
            is_last = (i == len(files_to_show) - 1) and remaining_files <= 0
            connector = "└── " if is_last else "├── "
            output = f"{prefix}{connector}{file_name}"
            
            # Safe print with encoding fallback
            try:
                print(output)
            except UnicodeEncodeError:
                print(output.encode('ascii', 'replace').decode('ascii'))
            
            if file_handle:
                file_handle.write(output + "\n")
        
        # Show remaining files count if any
        if remaining_files > 0:
            connector = "└── "
            output = f"{prefix}{connector}(... and {remaining_files} remaining)"
            
            try:
                print(output)
            except UnicodeEncodeError:
                print(output.encode('ascii', 'replace').decode('ascii'))
            
            if file_handle:
                file_handle.write(output + "\n")
    
    # Check if directory exists
    if not os.path.exists(root_dir):
        print(f"Error: Directory '{root_dir}' does not exist!")
        return
    
    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a directory!")
        return
    
    # Print header
    header = f"Folder Structure of: {os.path.abspath(root_dir)}\n{'=' * 60}"
    print(header)
    
    # Open output file and write structure
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header + "\n")
        
        # Print root directory
        root_output = f"{os.path.basename(root_dir) or root_dir}/"
        print(root_output)
        f.write(root_output + "\n")
        
        # Explore structure
        print_tree(root_dir, "", f)
    
    print(f"\n✓ Structure saved to: {output_file}")

# Example usage
if __name__ == "__main__":
    # Change to your target directory
    target_directory = "muavic-repo/data"
    
    explore_folder_structure(target_directory)