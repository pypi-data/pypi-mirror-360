
import psutil
import time, datetime
import threading
from tomlkit import parse, dumps, document, table, array
from os.path import join, exists
from pathlib import Path


current_directory = Path(__file__).parent
process_path = current_directory / 'process.toml'


def process_start(project_name: str, pid: int) -> None:
    if exists(process_path):
        doc = parse(open(process_path).read())
        if f'{project_name}' in doc:
            if pid not in doc.get(f'{project_name}'):
                doc.get(f'{project_name}').append(pid)
                with open(process_path, "w") as f:
                    f.write(dumps(doc))
                f.close()
        else:
            process = array()
            process.append(pid)
            doc.add(f"{project_name}", process)
            with open(process_path, "w") as f:
                f.write(dumps(doc))
            f.close()
    else:
        doc = document()
        process = array()
        process.append(pid)
        doc.add(f"{project_name}", process)
        with open(process_path, "w") as f:
            f.write(dumps(doc))
        f.close()

def process_len(project_name: str) -> int:
    if exists(process_path):
        doc = parse(open(process_path).read())
        if f'{project_name}' in doc:
            return len(doc.get(f'{project_name}'))
        else:
            return 0
    else:
        return 0

def process_stop(project_name: str) -> None:
    if exists(process_path):
        doc = parse(open(process_path).read())
        if f'{project_name}' in doc:
            process_list = doc.get(f'{project_name}')
            length = len(process_list)
            for i in range(length):
                process_check = get_process_status(process_list[i])
                if 'error' not in process_check:
                    terminate_process(process_list[i], force=True)
            del doc[f'{project_name}']
            with open(process_path, 'w') as f:
                f.write(dumps(doc))
            f.close()
        return True

def get_process_status(pid):
    try:
        process = psutil.Process(pid)
        status = {
            'pid': pid,
            'name': process.name(),
            'status': process.status(),
            'cmdline': ' '.join(process.cmdline())
        }
        return status
    except psutil.NoSuchProcess:
        return {'error': f'{pid}'}
    except psutil.AccessDenied:
        return {'error': f'{pid}'}
    except Exception as e:
        return {'error': f'{str(e)}'}

def terminate_process(pid, force=False):
    try:
        process = psutil.Process(pid)
        process.kill()
        process.wait(timeout=3)       
        return {'success': f'{pid}'}
    except psutil.NoSuchProcess:
        return {'error': f'{pid}'}
    except psutil.AccessDenied:
        return {'error': f'{pid}'}
    except psutil.TimeoutExpired:
        return {'error': f'{pid}'}
    except Exception as e:
        return {'error': f'{str(e)}'}

def monitor_workers(port, project_name):
    def monitor():
        for i in range(10):
            try:
                for conn in psutil.net_connections():
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        try:
                            process = psutil.Process(conn.pid)
                            if 'python' in process.name().lower() or 'python3' in process.name().lower():
                                children = process.children(recursive=True)
                                worker_pids = [child.pid for child in children]
                                # print(f"Main PID: {conn.pid}")
                                # print(f"Worker PIDs: {worker_pids}")
                                from bomiot_process import process
                                for pid in worker_pids:
                                    process.process_start(project_name=project_name, pid=pid)
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                time.sleep(1)
            except Exception as e:
                print(f"{e}")
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()