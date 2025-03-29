#!/usr/bin/env python3

import os
import argparse
import sys

# --- Configuration: Files/Directories/Extensions to Ignore ---
# Add directories you want to skip entirely
IGNORED_DIRS = {
    ".git",
    ".vscode",
    "__pycache__",
    "node_modules",
    "build",
    "dist",
    "venv",
    ".venv",
    "env",
    ".env",
    "target", # Rust build artifacts
    "logs",
}

# Add specific filenames you want to skip
IGNORED_FILES = {
    ".DS_Store",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
}

# Add file extensions you want to skip
IGNORED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".class", # Java bytecode
    ".o",     # Compiled object files
    ".so",    # Shared libraries
    ".dll",   # Windows dynamic link libraries
    ".exe",   # Windows executables
    ".log",
    ".lock",
    ".swp",   # Vim swap files
    ".swo",   # Vim swap files
    # Add image/binary formats if necessary
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".mp3", ".wav", ".ogg",
    ".mp4", ".avi", ".mov", ".mkv",
}
# --- End Configuration ---

def combine_files(input_dir, output_file):
    """
    Recursively finds files in input_dir, reads their content,
    and writes it to output_file with headers indicating the file path.

    Args:
        input_dir (str): The path to the directory to scan.
        output_file (str): The path to the file where combined content will be written.
    """
    abs_input_dir = os.path.abspath(input_dir)
    abs_output_file = os.path.abspath(output_file)
    processed_files = 0
    skipped_files = 0

    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(f"# Combined content from directory: {abs_input_dir}\n")
            outfile.write(f"# Output file: {abs_output_file}\n")
            outfile.write("# --- START OF COMBINED CONTENT ---\n\n")

            for dirpath, dirnames, filenames in os.walk(abs_input_dir, topdown=True):
                # --- Directory Filtering ---
                # Modify dirnames in-place to prevent os.walk from descending
                # into ignored directories.
                dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

                # Skip the root ignored directories explicitly if topdown=False was used
                # (though we use topdown=True which is more efficient)
                # current_dir_name = os.path.basename(dirpath)
                # if current_dir_name in IGNORED_DIRS:
                #     print(f"Skipping ignored directory: {dirpath}")
                #     continue

                for filename in filenames:
                    # --- File Filtering ---
                    if filename in IGNORED_FILES:
                        print(f"Skipping ignored file: {filename}")
                        skipped_files += 1
                        continue

                    _, extension = os.path.splitext(filename)
                    if extension.lower() in IGNORED_EXTENSIONS:
                        print(f"Skipping file with ignored extension: {filename}")
                        skipped_files += 1
                        continue

                    file_path = os.path.join(dirpath, filename)

                    # --- Avoid reading the output file itself ---
                    if os.path.abspath(file_path) == abs_output_file:
                        print(f"Skipping the output file itself: {file_path}")
                        skipped_files += 1
                        continue

                    relative_path = os.path.relpath(file_path, abs_input_dir)

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                            content = infile.read()

                        print(f"Processing: {relative_path}")
                        outfile.write(f"--- START FILE: {relative_path} ---\n")
                        outfile.write(content)
                        outfile.write(f"\n--- END FILE: {relative_path} ---\n\n")
                        processed_files += 1

                    except (IOError, OSError) as e:
                        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
                        skipped_files += 1
                    except Exception as e: # Catch potential unexpected errors
                        print(f"Unexpected error processing file {file_path}: {e}", file=sys.stderr)
                        skipped_files += 1


            outfile.write("# --- END OF COMBINED CONTENT ---\n")

        print(f"\nSuccessfully combined {processed_files} files into '{output_file}'.")
        if skipped_files > 0:
            print(f"Skipped {skipped_files} files (ignored, binary, or read errors).")

    except IOError as e:
        print(f"Error opening or writing to output file {output_file}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combine all text files in a directory and its subdirectories into a single output file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "input_dir",
        help="The root directory containing the files to combine."
    )
    parser.add_argument(
        "-o", "--output",
        default="combined_code.txt",
        help="The name of the output file to create."
    )

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' not found or is not a directory.", file=sys.stderr)
        sys.exit(1)

    combine_files(args.input_dir, args.output)
