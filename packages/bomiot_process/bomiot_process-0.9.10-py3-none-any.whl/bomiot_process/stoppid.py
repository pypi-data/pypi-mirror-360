import sys
import json

def supervisor_stop():
    sys.stdout.write("READY\n")
    sys.stdout.flush()
    
    while True:
        # 读取 header
        line = sys.stdin.readline()
        if not line:
            break
            
        headers = {}
        while line.strip():
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
            line = sys.stdin.readline()
        
        # 读取 payload
        payload_len = int(headers.get('len', 0))
        payload = sys.stdin.read(payload_len)
        
        # 解析 JSON 数据
        try:
            event_data = json.loads(payload)
            
            # 获取进程信息
            process_name = event_data.get('processname', 'unknown')
            group_name = event_data.get('groupname', 'unknown')
            pid = event_data.get('pid', 0)
            event_name = event_data.get('eventname', 'unknown')
            exit_status = event_data.get('exitstatus', 0)
            
            # 如果是进程停止事件，执行特定逻辑
            if event_name == 'PROCESS_STATE_STOPPED':
                print(f"Process {process_name} (PID: {pid}) group_name {group_name} event {event_name} with exit status {exit_status}.")
                print(event_data)
                # 在这里添加你的自定义逻辑
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        sys.stdout.write("RESULT 2\nOK")
        sys.stdout.flush()

if __name__ == '__main__':
    supervisor_stop()