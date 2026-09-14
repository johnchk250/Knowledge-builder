"""Launch one fresh CHP server instance and retire a verified orphan from an earlier UI session."""
import json
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT=Path(__file__).resolve().parent.parent
URL='http://127.0.0.1:8765/api/bootstrap'


def _bootstrap():
    try:
        with urllib.request.urlopen(URL,timeout=.8) as response:
            data=json.load(response)
        return data if isinstance(data,dict) and isinstance(data.get('settings'),dict) and isinstance(data.get('token'),str) else None
    except (OSError,ValueError,urllib.error.URLError):
        return None


def _listener_pid():
    if os.name!='nt': return None
    script="(Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)"
    try:
        value=subprocess.check_output(['powershell','-NoProfile','-Command',script],text=True,encoding='utf-8',errors='replace',timeout=5).strip()
        return int(value) if value else None
    except (OSError,ValueError,subprocess.SubprocessError):
        return None


def _is_chp_process(pid):
    if not pid or pid==os.getpid(): return False
    if os.name=='nt':
        script=f'(Get-CimInstance Win32_Process -Filter "ProcessId={pid}" -ErrorAction SilentlyContinue).CommandLine'
        try: command=subprocess.check_output(['powershell','-NoProfile','-Command',script],text=True,encoding='utf-8',errors='replace',timeout=5).lower()
        except (OSError,subprocess.SubprocessError): return False
    else:
        try: command=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace').lower()
        except OSError: return False
    return '-m chp.server' in command or '-m chp.launcher' in command


def stop_orphan():
    if not _bootstrap(): return
    pid=None
    marker=ROOT/'data'/'server.pid'
    try: pid=int(marker.read_text('ascii').strip())
    except (OSError,ValueError): pass
    if not _is_chp_process(pid): pid=_listener_pid()
    if not _is_chp_process(pid):
        raise RuntimeError('Port 8765 is occupied by a CHP-like server that cannot be safely identified. Close it before starting another instance.')
    try: os.kill(pid,signal.SIGTERM)
    except ProcessLookupError: return
    except OSError as exc: raise RuntimeError(f'Could not stop the previous CHP server process {pid}.') from exc
    deadline=time.monotonic()+6
    while time.monotonic()<deadline:
        if not _bootstrap(): return
        time.sleep(.15)
    raise RuntimeError(f'Previous CHP server process {pid} did not stop.')


def main():
    stop_orphan()
    from .server import main as server_main
    server_main()


if __name__=='__main__': main()
