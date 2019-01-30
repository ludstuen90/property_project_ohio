#!/usr/bin/python
import subprocess
import sys

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = subprocess.Popen(f'''python manage.py {filename}''', shell=True)
    p.wait()
