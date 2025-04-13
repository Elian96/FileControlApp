import subprocess
import os

def main():
    # Paste your full Python path below
    python_path = r"C:\Program Files\Python310\python.exe"
    app_path = os.path.join(os.path.dirname(__file__), "filecontrol.py")
    
    # Use -m streamlit to run the app without needing streamlit in PATH
    subprocess.run([python_path, "-m", "streamlit", "run", app_path], shell=True)

if __name__ == "__main__":
    main()

