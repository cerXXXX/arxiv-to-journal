"""Rebuild a committed checkout with empty caches and blocked network access."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='publication-study-clean-') as task_dir:
        task=Path(task_dir);checkout=task/'checkout';guard=task/'guard';home=task/'home'
        guard.mkdir();home.mkdir()
        (guard/'sitecustomize.py').write_text('''import sys
def deny_network(event, args):
    if event in {"socket.connect", "socket.getaddrinfo", "socket.bind"}:
        raise RuntimeError("Network disabled during clean reproduction: " + event)
sys.addaudithook(deny_network)
''')
        subprocess.run(['git','clone','--quiet','--no-local',str(ROOT),str(checkout)],check=True)
        if (checkout/'.deps').exists() or (checkout/'.venv').exists():
            raise RuntimeError('Dependency cache unexpectedly entered the repository')
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'HOME':str(home),'PYTHONPATH':str(guard),
             'HTTP_PROXY':'http://127.0.0.1:9','HTTPS_PROXY':'http://127.0.0.1:9',
             'ALL_PROXY':'http://127.0.0.1:9','NO_PROXY':'','PYTHONHASHSEED':'89217','TZ':'Pacific/Honolulu','LC_ALL':'C'}
        probe=subprocess.run([sys.executable,'-c',"import socket; socket.create_connection(('example.org',443),1)"],
                             env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if probe.returncode==0 or 'Network disabled during clean reproduction' not in probe.stderr:
            raise RuntimeError('Network guard was not activated before the build')
        start=time.monotonic()
        result=subprocess.run(['make','reproduce','PYTHON='+sys.executable],cwd=checkout,env=env,text=True,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if result.returncode:
            print(result.stdout)
            raise SystemExit(result.returncode)
        status=subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
        if status:
            raise RuntimeError('Clean reproduction changed tracked files: '+status)
        print(result.stdout)
        print(f'Clean Git clone, empty dependency cache, blocked Python sockets: PASS ({time.monotonic()-start:.2f} s)')


if __name__=='__main__':main()
