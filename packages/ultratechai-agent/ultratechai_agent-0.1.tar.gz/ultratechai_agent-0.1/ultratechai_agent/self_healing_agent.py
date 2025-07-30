
import subprocess

def analyze_and_fix(file_path):
    try:
        output = subprocess.check_output(['python3', file_path], stderr=subprocess.STDOUT)
        return "[✓] Kod problemsiz çalışır."
    except subprocess.CalledProcessError as e:
        return "[🛠] Səhv tapıldı:\n" + e.output.decode()
