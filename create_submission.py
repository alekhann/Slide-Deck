"""Create a clean submission package without virtual environment."""
import os
import zipfile
from pathlib import Path

def create_submission_package():
    """Create a ZIP file with only necessary files for submission."""
    
    # Files and folders to EXCLUDE
    exclude_patterns = [
        'env/',
        '__pycache__/',
        '.git/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'pip-log.txt',
        'pip-delete-this-directory.txt',
        '.pytest_cache/',
        '.coverage',
        'htmlcov/',
        'dist/',
        'build/',
        '*.egg-info/',
        '.vscode/',
        '.idea/',
        'extracted_figures/',  # Can be regenerated
        'extracted_images/',   # Can be regenerated
        'output/',             # Generated output
        'papers/',             # Downloaded papers (optional)
        '.DS_Store',
        'Thumbs.db',
        'create_submission.py',  # This script itself
    ]
    
    # Create ZIP file
    zip_filename = 'research_paper_to_slides_submission.zip'
    
    print(f"Creating submission package: {zip_filename}")
    print("=" * 60)
    
    # Add submission README if it exists
    if os.path.exists('SUBMISSION_README.md'):
        print("  ✓ Including SUBMISSION_README.md")
        exclude_patterns.append('SUBMISSION_README.md')  # Will be added separately as README.txt
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories from dirs list (in-place)
            dirs[:] = [d for d in dirs if not any(
                d == pattern.rstrip('/') or d.startswith(pattern.rstrip('/'))
                for pattern in exclude_patterns
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if file should be excluded
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern.endswith('/'):
                        continue  # Already handled directories
                    elif pattern.startswith('*'):
                        if file.endswith(pattern[1:]):
                            should_exclude = True
                            break
                    elif file == pattern or file_path.startswith(f'./{pattern}'):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    # Add file to ZIP
                    arcname = file_path[2:]  # Remove './' prefix
                    zipf.write(file_path, arcname)
                    print(f"  ✓ Added: {arcname}")
    
    # Get ZIP file size
    zip_size = os.path.getsize(zip_filename)
    zip_size_mb = zip_size / (1024 * 1024)
    
    print("=" * 60)
    print(f"\n✅ Submission package created successfully!")
    print(f"📦 File: {zip_filename}")
    print(f"📊 Size: {zip_size_mb:.2f} MB")
    print(f"\nThis package includes:")
    print("  • All source code")
    print("  • Configuration files")
    print("  • Documentation")
    print("  • requirements.txt")
    print("\nExcluded:")
    print("  • Virtual environment (env/)")
    print("  • Cache files (__pycache__/)")
    print("  • Generated outputs")
    print("  • Downloaded papers")
    print("\nRecipient can recreate environment with:")
    print("  python -m venv env")
    print("  env\\Scripts\\activate  (Windows)")
    print("  pip install -r requirements.txt")

if __name__ == '__main__':
    create_submission_package()
