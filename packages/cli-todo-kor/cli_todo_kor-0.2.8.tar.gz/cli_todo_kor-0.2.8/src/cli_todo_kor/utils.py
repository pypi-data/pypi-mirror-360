import json
import os
from datetime import datetime, timedelta
from platformdirs import user_data_dir
import re

APP_NAME = "cli-todo-kor"
DATA_DIR = user_data_dir(appname=APP_NAME)
HISTORY_FILE = os.path.join(DATA_DIR, 'command_history.json')

TODO_DIR = user_data_dir(appname=APP_NAME)
TODO_FILE = os.path.join(TODO_DIR, 'todos.json')

def load_todos():
    # 디렉토리가 없으면 생성
    if not os.path.exists(TODO_DIR):
        os.makedirs(TODO_DIR)
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def save_todos(todos):
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)

def _get_sorted_todos(todos_list, sort_by='priority'):
    temp_todos = [dict(item) for item in todos_list]
    for i, todo in enumerate(temp_todos):
        todo['original_index'] = i
    if sort_by == 'priority':
        priority_map = {'높음': 0, '중간': 1, '낮음': 2}
        today = datetime.now().date()
        def sort_key(x):
            overdue = 0
            due_date_val = None
            if 'due_date' in x and not x.get('completed', False):
                try:
                    due_date_obj = datetime.strptime(x['due_date'], '%Y-%m-%d').date()
                    due_date_val = due_date_obj
                    if due_date_obj < today:
                        overdue = -1
                except ValueError:
                    pass
            # 마감 기한이 없는 경우 가장 뒤로, 있는 경우 가까운 순서대로
            # overdue_sort는 마감 기한이 지난 경우를 최상단으로 정렬하기 위함
            # due_date_val is None을 통해 마감 기한 없는 항목을 뒤로 보냄
            # x['original_index']는 최종적으로 생성 순서 유지
            return (x.get('completed', False), # 미완료(False)가 완료(True)보다 먼저 오도록
                    overdue,
                    priority_map.get(x.get('priority', '중간'), 1),
                    due_date_val is None, # 마감 기한 없는 항목을 뒤로 보냄
                    due_date_val,
                    x['original_index'])
        temp_todos.sort(key=sort_key)
    elif sort_by == 'due-date':
        # 완료 여부 (미완료 먼저), 마감 기한, 생성 순서
        temp_todos.sort(key=lambda x: (x.get('completed', False), x.get('due_date') is None, x.get('due_date', '9999-99-99'), x['original_index']))
    elif sort_by == 'description':
        # 완료 여부 (미완료 먼저), 설명, 생성 순서
        temp_todos.sort(key=lambda x: (x.get('completed', False), x['description'], x['original_index']))
    elif sort_by == 'status':
        # 완료 여부 (미완료 먼저), 생성 순서
        temp_todos.sort(key=lambda x: (x['completed'], x['original_index']))
    return temp_todos

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

def get_project_version():
    pyproject_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'pyproject.toml')
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'version = "([0-9.]+)"\n', content)
            if match:
                return match.group(1)
    return "Unknown"