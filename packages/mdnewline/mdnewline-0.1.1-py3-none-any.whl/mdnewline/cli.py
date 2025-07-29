import argparse
import sys
import shutil
from pathlib import Path
from .processor import process_markdown


def create_backup(file_path: Path) -> None:
    """Create a backup of the original file."""
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    shutil.copy2(file_path, backup_path)


def main():
    """Main entry point for the mdnewline CLI."""
    parser = argparse.ArgumentParser(
        description='Process markdown files to add line breaks after sentences'
    )
    parser.add_argument('file', help='Markdown file to process')
    parser.add_argument('-w', '--write', action='store_true',
                        help='Write changes back to the file (creates .bak backup)')
    parser.add_argument('-n', '--no-backup', action='store_true',
                        help='Do not create backup file when using -w flag')
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    
    # Check if file exists
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process the markdown
    processed_content = process_markdown(content)
    
    # Output or write back
    if args.write:
        try:
            # Create backup if requested
            if not args.no_backup:
                create_backup(file_path)
            
            # Write processed content back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            print(f"File '{args.file}' has been processed and updated")
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Output to stdout
        print(processed_content, end='')


if __name__ == '__main__':
    main()