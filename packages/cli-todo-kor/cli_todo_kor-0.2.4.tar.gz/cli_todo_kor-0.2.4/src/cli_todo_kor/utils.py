import json
import os
from datetime import datetime, timedelta
from platformdirs import user_data_dir

APP_NAME = "cli-todo-kor"
DATA_DIR = user_data_dir(appname=APP_NAME)
HISTORY_FILE = os.path.join(DATA_DIR, 'command_history.json')

def _parse_due_date(date_str):
    if date_str is None:
        return None
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        pass
    try:
        days = int(date_str)
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime('%Y-%m-%d')
    except ValueError:
        pass
    print("경고: 유효하지 않은 날짜 형식입니다. YYYY-MM-DD 또는 숫자(X일 뒤) 형식으로 입력해주세요.")
    return None

def _parse_priority(priority_str):
    priority_map = {
        'h': '높음',
        'm': '중간',
        'l': '낮음',
        '높음': '높음',
        '중간': '중간',
        '낮음': '낮음'
    }
    return priority_map.get(priority_str.lower(), '중간')

def log_command(command, args):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    # args 객체를 딕셔너리로 변환 (직렬화 가능한 형태로)
    arg_dict = vars(args) if args else {}
    # command와 args에서 민감한 정보나 불필요한 정보 제거 (예: command 자체는 필요하지만, 내부 객체는 불필요)
    # 여기서는 command와 arg_dict를 그대로 저장하지만, 필요에 따라 필터링 로직 추가 가능

    history.append({
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'args': arg_dict
    })

    # 최신 100개 명령어만 유지
    history = history[-100:]

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def get_command_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            return []
    return history

def clear_command_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f) # 파일 내용을 비움
        print("명령어 기록이 삭제되었습니다.")
    else:
        print("삭제할 명령어 기록이 없습니다.") 