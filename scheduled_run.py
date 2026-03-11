import sys
import os

sys.path.insert(0, '/home/Salmaneelb/mysite')
os.chdir('/home/Salmaneelb/mysite')

from storage import init_db, save_run
from tester.runner import run_all

if __name__ == "__main__":
    init_db()
    report = run_all()
    save_run(report)
    print(f"[OK] Run terminé : {report['summary']}")
