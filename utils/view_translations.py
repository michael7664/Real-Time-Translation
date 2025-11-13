import os
import glob
from datetime import datetime

def view_translations():
    """View all saved translation files"""
    translation_files = glob.glob("translations_*.txt")
    
    if not translation_files:
        print("No translation files found!")
        return
    
    print("Available translation files:")
    for i, file in enumerate(sorted(translation_files, reverse=True)):
        file_time = os.path.getmtime(file)
        file_date = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {file} (created: {file_date})")
    
    if translation_files:
        choice = input("\nEnter file number to view (or Enter for latest): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(translation_files):
            selected_file = translation_files[int(choice) - 1]
        else:
            selected_file = translation_files[0]  # Latest file
        
        print(f"\n{'='*80}")
        print(f"VIEWING: {selected_file}")
        print(f"{'='*80}")
        
        with open(selected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)

if __name__ == "__main__":
    view_translations()