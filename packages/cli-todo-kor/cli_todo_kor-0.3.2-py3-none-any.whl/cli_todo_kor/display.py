import re
from datetime import datetime
from .utils import load_todos, _get_sorted_todos


class Colors:
    RED = '\x1b[91m'
    GREEN = '\x1b[92m'
    YELLOW = '\x1b[93m'
    BLUE = '\x1b[94m'
    MAGENTA = '\x1b[95m'
    CYAN = '\x1b[96m'
    GRAY = '\x1b[90m'
    ENDC = '\x1b[0m'
    BOLD = '\x1b[1m'

ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
def strip_ansi_codes(s):
    return ansi_escape.sub('', s)

# 고정된 라인 너비 (조정 가능)
LINE_WIDTH = 75

def _print_section_header(header_text, color, line_width=40):
    header_text_len = len(strip_ansi_codes(header_text))
    total_dashes = line_width - header_text_len
    left_dashes = total_dashes // 2
    right_dashes = total_dashes - left_dashes
    combined_header = (
        f"{Colors.BOLD}{color}─{Colors.ENDC}" * left_dashes +
        f"{Colors.BOLD}{color}{header_text}{Colors.ENDC}" +
        f"{Colors.BOLD}{color}─{Colors.ENDC}" * right_dashes
    )
    print(combined_header)

def _print_todo_item(idx, todo, today, format_tags):
    status_text = f"{Colors.GREEN}완료{Colors.ENDC}" if todo["completed"] else f"{Colors.RED}미완료{Colors.ENDC}"
    description_color = Colors.GRAY if todo["completed"] else Colors.BOLD
    description = f"{description_color}{todo['description']}{Colors.ENDC}"
    due_date_info = ""
    if "due_date" in todo:
        try:
            due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d')
            if due_date_obj.date() == today:
                due_date_info = f" {Colors.YELLOW}(오늘 마감: {todo['due_date']}){Colors.ENDC}"
            elif due_date_obj.date() < today: # datetime.now() 대신 today 사용
                due_date_info = f" {Colors.RED}(마감 지남: {todo['due_date']}){Colors.ENDC}"
            else:
                due_date_info = f" {Colors.BLUE}(마감: {todo['due_date']}){Colors.ENDC}"
        except ValueError:
            due_date_info = f" {Colors.GRAY}(잘못된 날짜: {todo['due_date']}){Colors.ENDC}"
    tags_display = format_tags(todo.get('tags', []))

    print(f"{idx+1}. [{status_text}] {description} {tags_display}{due_date_info}")

def list_todos(status_filter=None, search_term=None, sort_by='priority', tag_filter=None):
    todos = load_todos()
    if search_term:
        todos = [t for t in todos if search_term.lower() in t['description'].lower()]
    if status_filter:
        if status_filter == 'completed':
            todos = [t for t in todos if t['completed']]
        elif status_filter == 'pending':
            todos = [t for t in todos if not t['completed']]
    
    # 태그 필터링 로직 추가
    if tag_filter:
        # tag_filter가 리스트가 아니면 리스트로 변환 (단일 태그 검색 지원)
        if not isinstance(tag_filter, list):
            tag_filter = [tag_filter]
        # 모든 지정된 태그를 포함하는 할 일만 필터링
        todos = [t for t in todos if all(tag in t.get('tags', []) for tag in tag_filter)]

    sorted_todos = _get_sorted_todos(todos, sort_by)
    if not sorted_todos:
        print("표시할 할 일이 없습니다.")
        return
    all_todos = load_todos()
    total_todos = len(all_todos)
    uncompleted_todos = sum(1 for todo in all_todos if not todo.get("completed", False))
    today_due_todos = 0
    today = datetime.now().date()
    for todo in all_todos:
        if not todo.get("completed", False) and "due_date" in todo:
            try:
                due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d').date()
                if due_date_obj == today:
                    today_due_todos += 1
            except ValueError:
                pass
    print(f"   {Colors.BLUE}  전체: {total_todos} | 미완료: {uncompleted_todos} | 오늘 마감: {today_due_todos}{Colors.ENDC}\n")
    
    priority_order = ['높음', '중간', '낮음']
    priority_map = {'높음': [], '중간': [], '낮음': []}
    overdue_todos = []
    for idx, todo in enumerate(sorted_todos):
        is_overdue = False
        if "due_date" in todo and not todo["completed"]:
            try:
                due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d').date()
                if due_date_obj < today:
                    is_overdue = True
            except ValueError:
                pass
        if is_overdue and not todo["completed"]:
            overdue_todos.append((idx, todo))
        else:
            prio = todo.get('priority', '중간')
            if prio not in priority_map:
                priority_map[prio] = []
            priority_map[prio].append((idx, todo))
    
    # 태그를 포맷하는 헬퍼 함수
    def format_tags(tags):
        if not tags:
            return ""
        return " ".join([f"{Colors.MAGENTA}#{tag}{Colors.ENDC}" for tag in tags])

    if overdue_todos:
        _print_section_header(" 마감 기한 지남 ", Colors.RED)
        for idx, todo in overdue_todos:
            _print_todo_item(idx, todo, today, format_tags)
        print()

    for i, prio in enumerate(priority_order):
        _print_section_header(f" {prio} 우선순위 ", Colors.YELLOW)
        prio_todos = priority_map[prio]
        if not prio_todos:
            print("-")
        else:
            for idx, todo in prio_todos:
                _print_todo_item(idx, todo, today, format_tags)
        print()