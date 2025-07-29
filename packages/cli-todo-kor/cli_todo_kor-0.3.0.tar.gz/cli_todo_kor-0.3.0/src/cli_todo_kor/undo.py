import os
import json

UNDO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', '.todos_undo.json')
REDO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', '.todos_redo.json')

def push_undo():
    from .utils import load_todos
    todos = load_todos()
    undo_stack = []
    if os.path.exists(UNDO_FILE):
        with open(UNDO_FILE, 'r', encoding='utf-8') as f:
            try:
                undo_stack = json.load(f)
            except json.JSONDecodeError:
                undo_stack = []
    undo_stack.append(todos)
    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)

def pop_undo():
    from .utils import load_todos, save_todos
    from .display import list_todos
    
    if not os.path.exists(UNDO_FILE):
        print('실행 취소할 작업이 없습니다.')
        return
    with open(UNDO_FILE, 'r', encoding='utf-8') as f:
        try:
            undo_stack = json.load(f)
        except json.JSONDecodeError:
            undo_stack = []
    if not undo_stack:
        print('실행 취소할 작업이 없습니다.')
        return
    current = load_todos()
    last = undo_stack.pop()
    # redo에 현재 상태 push
    redo_stack = []
    if os.path.exists(REDO_FILE):
        with open(REDO_FILE, 'r', encoding='utf-8') as f:
            try:
                redo_stack = json.load(f)
            except json.JSONDecodeError:
                redo_stack = []
    redo_stack.append(current)
    with open(REDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(redo_stack, f, indent=4, ensure_ascii=False)
    # undo pop한 상태로 복원
    save_todos(last)
    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)
    print('마지막 작업을 실행 취소했습니다.')
    list_todos()

def pop_redo():
    from .utils import load_todos, save_todos
    from .display import list_todos
    
    if not os.path.exists(REDO_FILE):
        print('다시 실행할 작업이 없습니다.')
        return
    with open(REDO_FILE, 'r', encoding='utf-8') as f:
        try:
            redo_stack = json.load(f)
        except json.JSONDecodeError:
            redo_stack = []
    if not redo_stack:
        print('다시 실행할 작업이 없습니다.')
        return
    current = load_todos()
    last = redo_stack.pop()
    # undo에 현재 상태 push
    undo_stack = []
    if os.path.exists(UNDO_FILE):
        with open(UNDO_FILE, 'r', encoding='utf-8') as f:
            try:
                undo_stack = json.load(f)
            except json.JSONDecodeError:
                undo_stack = []
    undo_stack.append(current)
    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)
    # redo pop한 상태로 복원
    save_todos(last)
    with open(REDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(redo_stack, f, indent=4, ensure_ascii=False)
    print('마지막 실행 취소를 다시 실행했습니다.')
    list_todos() 