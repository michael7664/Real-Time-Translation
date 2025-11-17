#!/usr/bin/env python3
import sys
import os
import subprocess

def main():
    source_lang = sys.argv[1] if len(sys.argv) > 1 else "it"
    target_lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    output_folder = sys.argv[3] if len(sys.argv) > 3 else ""
    
    print(f"🚀 GUI Backend starting: {source_lang} → {target_lang}")
    if output_folder:
        print(f"📁 Output folder: {output_folder}")
    else:
        print("📁 Using default output location")
    print(f"📁 Current directory: {os.getcwd()}")
    sys.stdout.flush()
    
    # Use the standalone translator directly
    standalone_script = "standalone_translator.py"
    
    if not os.path.exists(standalone_script):
        print(f"❌ Standalone translator not found: {standalone_script}")
        return 1
    
    print(f"✅ Found standalone translator: {standalone_script}")
    sys.stdout.flush()
    
    # Run the standalone translator with real-time output
    try:
        # Pass through any arguments including output folder
        cmd = [sys.executable, standalone_script, source_lang, target_lang]
        if output_folder:
            cmd.append(output_folder)
            
        print(f"▶️  Running: {' '.join(cmd)}")
        sys.stdout.flush()
        
        # Run the process with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,  # Line buffered
            encoding='utf-8',
            errors='replace'
        )
        
        # Read output line by line in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                sys.stdout.flush()
        
        return process.returncode
        
    except KeyboardInterrupt:
        print("\n🛑 GUI Backend stopped by user")
        sys.stdout.flush()
        return 0
    except Exception as e:
        print(f"❌ Failed to run standalone translator: {e}")
        sys.stdout.flush()
        return 1

if __name__ == "__main__":
    sys.exit(main())