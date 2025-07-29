import os
import json
from .config import UNDO_FILE, REDO_FILE

def push_undo(todos):
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

def pop_undo(current_todos):
    if not os.path.exists(UNDO_FILE):
        print('실행 취소할 작업이 없습니다.')
        return None
    with open(UNDO_FILE, 'r', encoding='utf-8') as f:
        try:
            undo_stack = json.load(f)
        except json.JSONDecodeError:
            undo_stack = []
    if not undo_stack:
        print('실행 취소할 작업이 없습니다.')
        return None
    
    last_todos = undo_stack.pop()
    push_redo(current_todos)

    with open(UNDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(undo_stack, f, indent=4, ensure_ascii=False)
    
    print('마지막 작업을 실행 취소했습니다.')
    return last_todos

def push_redo(todos):
    redo_stack = []
    if os.path.exists(REDO_FILE):
        with open(REDO_FILE, 'r', encoding='utf-8') as f:
            try:
                redo_stack = json.load(f)
            except json.JSONDecodeError:
                redo_stack = []
    redo_stack.append(todos)
    with open(REDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(redo_stack, f, indent=4, ensure_ascii=False)

def pop_redo(current_todos):
    if not os.path.exists(REDO_FILE):
        print('다시 실행할 작업이 없습니다.')
        return None
    with open(REDO_FILE, 'r', encoding='utf-8') as f:
        try:
            redo_stack = json.load(f)
        except json.JSONDecodeError:
            redo_stack = []
    if not redo_stack:
        print('다시 실행할 작업이 없습니다.')
        return None

    last_todos = redo_stack.pop()
    push_undo(current_todos)

    with open(REDO_FILE, 'w', encoding='utf-8') as f:
        json.dump(redo_stack, f, indent=4, ensure_ascii=False)

    print('마지막 실행 취소를 다시 실행했습니다.')
    return last_todos