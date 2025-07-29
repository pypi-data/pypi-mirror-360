import os
import json
from datetime import datetime
from platformdirs import user_data_dir
from .utils import _parse_due_date, _parse_priority, load_todos, save_todos





def add_todo(description, due_date=None, priority='중간', tags=None):
    from .undo import push_undo
    push_undo()
    todos = load_todos()
    todo_item = {
        "description": description,
        "completed": False,
        "priority": _parse_priority(priority),
        "tags": tags if tags is not None else []
    }
    parsed_due_date = _parse_due_date(due_date)
    if parsed_due_date:
        todo_item["due_date"] = parsed_due_date
    todos.append(todo_item)
    save_todos(todos)
    print(f"할 일 추가: '{todo_item['description']}' (우선순위: {todo_item['priority']})")

def edit_todo(display_index, new_description=None, new_due_date=None, new_priority=None, new_tags=None):
    from .undo import push_undo
    push_undo()
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos)
    if 0 <= display_index < len(sorted_todos):
        target_todo = sorted_todos[display_index]
        original_index = target_todo['original_index']
        if new_description:
            todos[original_index]['description'] = new_description
            print(f"할 일 {display_index + 1}의 내용이 수정되었습니다.")
        if new_due_date:
            parsed_new_due_date = _parse_due_date(new_due_date)
            if parsed_new_due_date:
                todos[original_index]['due_date'] = parsed_new_due_date
                print(f"할 일 {display_index + 1}의 마감 기한이 수정되었습니다.")
        if new_priority:
            parsed_new_priority = _parse_priority(new_priority)
            if parsed_new_priority:
                todos[original_index]['priority'] = parsed_new_priority
                print(f"할 일 {display_index + 1}의 우선순위가 수정되었습니다.")
        if new_tags is not None:
            todos[original_index]['tags'] = new_tags
            print(f"할 일 {display_index + 1}의 태그가 수정되었습니다.")
        save_todos(todos)
    else:
        print("유효하지 않은 할 일 번호입니다.")

def complete_todo(display_index):
    from .undo import push_undo
    push_undo()
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos)
    if 0 <= display_index < len(sorted_todos):
        target_todo = sorted_todos[display_index]
        original_index = target_todo['original_index']
        if not todos[original_index]["completed"]:
            todos[original_index]["completed"] = True
            save_todos(todos)
            print(f"할 일 '{todos[original_index]['description']}'을(를) 완료했습니다.")
        else:
            print(f"할 일 '{todos[original_index]['description']}'은(는) 이미 완료되었습니다.")
    else:
        print("유효하지 않은 할 일 번호입니다.")

def delete_todo(display_indexes):
    from .undo import push_undo
    push_undo()
    todos = load_todos()
    sorted_todos = _get_sorted_todos(todos)
    unique_indexes = sorted(set(display_indexes), reverse=True)
    deleted = []
    invalid = []
    for display_index in unique_indexes:
        if 0 <= display_index < len(sorted_todos):
            target_todo = sorted_todos[display_index]
            original_index = target_todo['original_index']
            deleted.append(todos[original_index]['description'])
            todos.pop(original_index)
            for t in sorted_todos:
                if t['original_index'] > original_index:
                    t['original_index'] -= 1
        else:
            invalid.append(display_index+1)
    save_todos(todos)
    if deleted:
        print(f"할 일 삭제: {', '.join([f'\'{d}\'' for d in deleted])}")
    if invalid:
        print(f"유효하지 않은 할 일 번호: {', '.join(map(str, invalid))}")

def clear_completed_todos():
    from .undo import push_undo
    push_undo()
    todos = load_todos()
    initial_count = len(todos)
    todos = [todo for todo in todos if not todo['completed']]
    cleared_count = initial_count - len(todos)
    if cleared_count > 0:
        save_todos(todos)
        print(f"완료된 할 일 {cleared_count}개를 삭제했습니다.")
    else:
        print("삭제할 완료된 할 일이 없습니다.") 