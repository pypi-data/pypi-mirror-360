from datetime import datetime
from core import load_todos, _get_sorted_todos

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

def list_todos(status_filter=None, search_term=None, sort_by='priority'):
    todos = load_todos()
    if search_term:
        todos = [t for t in todos if search_term.lower() in t['description'].lower()]
    if status_filter:
        if status_filter == 'completed':
            todos = [t for t in todos if t['completed']]
        elif status_filter == 'pending':
            todos = [t for t in todos if not t['completed']]
    sorted_todos = _get_sorted_todos(todos, sort_by)
    if not sorted_todos:
        print("표시할 할 일이 없습니다.")
        return
    todo_ascii_art = """
████████╗ ██████╗ ██████╗   ██████╗ 
╚══██╔══╝██╔═══██╗██╔═══██╗██╔═══██╗
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ╚██████╔╝██████╔╝ ╚██████╔╝
   ╚═╝    ╚═════╝ ╚═════╝   ╚═════╝ 
"""
    print(f"{Colors.BOLD}{Colors.BLUE}{todo_ascii_art}{Colors.ENDC}")
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
    print(f"{Colors.GRAY}  전체: {total_todos} | 미완료: {uncompleted_todos} | 오늘 마감: {today_due_todos}{Colors.ENDC}\n")
    today = datetime.now().date()
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
    if overdue_todos:
        header_text = f" 마감 기한 지남 "
        header_text_len = len(header_text)
        line_width = 40
        total_dashes = line_width - header_text_len
        left_dashes = total_dashes // 2
        right_dashes = total_dashes - left_dashes
        combined_header = (
            f"{Colors.BOLD}{Colors.RED}─{Colors.ENDC}" * left_dashes +
            f"{Colors.BOLD}{Colors.RED}{header_text}{Colors.ENDC}" +
            f"{Colors.BOLD}{Colors.RED}─{Colors.ENDC}" * right_dashes
        )
        print(combined_header)
        for idx, todo in overdue_todos:
            status_icon = f"{Colors.RED}✗{Colors.ENDC}"
            status_text = f"{Colors.RED}마감 지남{Colors.ENDC}"
            description = f"{Colors.BOLD}{Colors.RED}{todo['description']}{Colors.ENDC}"
            due_date_info = ""
            if "due_date" in todo:
                try:
                    due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d')
                    if due_date_obj.date() == today:
                        due_date_info = f" {Colors.YELLOW}(오늘 마감: {todo['due_date']}){Colors.ENDC}"
                    elif due_date_obj < datetime.now():
                        due_date_info = f" {Colors.RED}(마감: {todo['due_date']}){Colors.ENDC}"
                    else:
                        due_date_info = f" {Colors.BLUE}(마감: {todo['due_date']}){Colors.ENDC}"
                except ValueError:
                    due_date_info = f" {Colors.GRAY}(잘못된 날짜: {todo['due_date']}){Colors.ENDC}"
            print(f"{idx+1}. {status_icon} [{status_text}] {description}{due_date_info}")
        print()
    for i, prio in enumerate(priority_order):
        header_text = f" {prio} 우선순위 "
        header_text_len = len(header_text)
        line_width = 40
        total_dashes = line_width - header_text_len
        left_dashes = total_dashes // 2
        right_dashes = total_dashes - left_dashes
        combined_header = (
            f"{Colors.BOLD}{Colors.YELLOW}─{Colors.ENDC}" * left_dashes +
            f"{Colors.BOLD}{Colors.YELLOW}{header_text}{Colors.ENDC}" +
            f"{Colors.BOLD}{Colors.YELLOW}─{Colors.ENDC}" * right_dashes
        )
        print(combined_header)
        prio_todos = priority_map[prio]
        if not prio_todos:
            print("-")
        else:
            for idx, todo in prio_todos:
                status_icon = f"{Colors.GREEN}✓{Colors.ENDC}" if todo["completed"] else f"{Colors.RED}✗{Colors.ENDC}"
                status_text = f"{Colors.GRAY}완료{Colors.ENDC}" if todo["completed"] else f"{Colors.YELLOW}미완료{Colors.ENDC}"
                priority_color = {
                    '높음': Colors.RED,
                    '중간': Colors.CYAN,
                    '낮음': Colors.GREEN
                }.get(prio, Colors.CYAN)
                priority_str = f"{priority_color}{prio}{Colors.ENDC}"
                description_color = Colors.GRAY if todo["completed"] else Colors.BOLD
                description = f"{description_color}{todo['description']}{Colors.ENDC}"
                due_date_info = ""
                if "due_date" in todo:
                    try:
                        due_date_obj = datetime.strptime(todo['due_date'], '%Y-%m-%d')
                        if due_date_obj.date() == today:
                            due_date_info = f" {Colors.YELLOW}(오늘 마감: {todo['due_date']}){Colors.ENDC}"
                        elif due_date_obj < datetime.now():
                            due_date_info = f" {Colors.RED}(마감 지남: {todo['due_date']}){Colors.ENDC}"
                        else:
                            due_date_info = f" {Colors.BLUE}(마감: {todo['due_date']}){Colors.ENDC}"
                    except ValueError:
                        due_date_info = f" {Colors.GRAY}(잘못된 날짜: {todo['due_date']}){Colors.ENDC}"
                print(f"{idx+1}. {status_icon} [{status_text}] {description}{due_date_info}")
        print() 