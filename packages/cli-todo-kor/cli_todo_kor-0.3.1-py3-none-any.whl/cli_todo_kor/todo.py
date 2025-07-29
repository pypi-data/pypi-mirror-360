#!/usr/bin/env python3
import argparse
import sys
from datetime import timedelta
from .core import (
    add_todo, edit_todo, complete_todo, delete_todo, 
    clear_completed_todos
)
from .display import list_todos, Colors
from .undo import pop_undo, pop_redo
from .utils import _parse_due_date, log_command, get_command_history, clear_command_history, get_project_version, load_todos

def main():
    todo_ascii_art = """
    ████████╗ ██████╗ ███████╗  ██████╗ 
    ╚══██╔══╝██╔═══██╗██╔═══██╗██╔═══██╗
       ██║   ██║   ██║██║   ██║██║   ██║
       ██║   ██║   ██║██║   ██║██║   ██║
       ██║   ╚██████╔╝███████╔╝╚██████╔╝ 
       ╚═╝    ╚═════╝ ╚═════╝   ╚═════╝  
"""
    print(f"{Colors.BOLD}{todo_ascii_art}{Colors.ENDC}")
    description_text = f"""{Colors.BOLD}{Colors.BLUE}CLI 기반 할 일 목록 관리자 (버전: {get_project_version()}){Colors.ENDC}

사용 가능한 명령어:
  add       새로운 할 일을 추가합니다.
  clear     완료된 모든 할 일을 삭제합니다.
  complete  할 일을 완료 상태로 변경합니다.
  delete    할 일을 삭제합니다.
  edit      할 일을 수정합니다.
  list      할 일 목록을 보여줍니다.
  log       실행된 명령어 기록을 보여줍니다.
  redo      마지막 실행 취소를 다시 실행합니다.
  search    키워드로 할 일을 검색합니다.
  undo      마지막 작업을 실행 취소합니다.

각 명령어의 상세 도움말: todo <명령어> -h"""

    # 약어 매핑
    alias_map = {
        "a": "add",
        "ls": "list",
        "l": "list",
        "c": "complete",
        "comp": "complete",
        "d": "delete",
        "del": "delete",
        "e": "edit",
        "s": "search",
        "clr": "clear",
        "u": "undo",
        "r": "redo",
    }

    # 유효한 명령어 목록 (약어 포함)
    valid_commands = list(alias_map.keys()) + list(alias_map.values()) + ["log"]
    valid_commands = list(set(valid_commands)) # 중복 제거

    parser = argparse.ArgumentParser(
        description=description_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help=argparse.SUPPRESS)

    # 'add' 명령어
    add_parser = subparsers.add_parser("add", help="새로운 할 일을 추가합니다. (약어: a)")
    add_parser.add_argument("description", type=str, help="추가할 할 일 내용")
    add_parser.add_argument("--due", type=str, help="마감 기한 (YYYY-MM-DD 형식)", dest="due_date")
    add_parser.add_argument(
        "--priority",
        type=str,
        choices=['h', 'm', 'l', '높음', '중간', '낮음'],
        default='m',
        metavar='PRIORITY',
        help="우선순위 (예: h, m, l 또는 높음, 중간, 낮음. 기본값: m)"
    )
    add_parser.add_argument("--tags", type=str, nargs='*', help="할 일에 추가할 태그 (예: #업무 #긴급)", dest="tags")

    # 'list' 명령어
    list_parser = subparsers.add_parser("list", help="할 일 목록을 보여줍니다. (약어: ls, l)")
    list_parser.add_argument("--status", type=str, choices=['pending', 'completed'], help="상태별로 필터링 (pending, completed)")
    list_parser.add_argument("--sort-by", type=str, choices=['priority', 'due-date', 'description', 'status'], default='priority', help="정렬 기준. 'priority'는 그룹화하여 표시(기본값), 그 외는 목록 정렬.")
    list_parser.add_argument("--tags", type=str, nargs='*', help="태그로 필터링 (예: #업무)", dest="tag_filter")

    # 'search' 명령어
    search_parser = subparsers.add_parser("search", help="키워드로 할 일을 검색합니다. (약어: s)")
    search_parser.add_argument("keyword", type=str, help="검색할 키워드")

    # 'complete' 명령어
    complete_parser = subparsers.add_parser("complete", help="할 일을 완료 상태로 변경합니다. (약어: c, comp)")
    complete_parser.add_argument("index", type=int, help="완료할 할 일의 번호")

    # 'delete' 명령어
    delete_parser = subparsers.add_parser("delete", help="할 일을 삭제합니다. (약어: d, del)")
    delete_parser.add_argument("indexes", type=int, nargs='+', help="삭제할 할 일의 번호(여러 개 가능)")

    # 'edit' 명령어
    edit_parser = subparsers.add_parser("edit", help="할 일을 수정합니다. (약어: e)")
    edit_parser.add_argument("index", type=int, help="수정할 할 일의 번호")
    edit_parser.add_argument("--desc", type=str, help="새로운 할 일 내용", dest="new_description")
    edit_parser.add_argument("--due", type=str, help="새로운 마감 기한 (YYYY-MM-DD)", dest="new_due_date")
    edit_parser.add_argument(
        "--priority",
        type=str,
        choices=['h', 'm', 'l', '높음', '중간', '낮음'],
        metavar='PRIORITY',
        help="새로운 우선순위 (예: h, m, l 또는 높음, 중간, 낮음)"
        , dest="new_priority"
    )
    edit_parser.add_argument("--tags", type=str, nargs='*', help="새로운 태그 (기존 태그를 덮어씁니다)", dest="new_tags")

    # 'clear' 명령어
    subparsers.add_parser("clear", help="완료된 모든 할 일을 삭제합니다. (약어: clr)")

    # 'undo' 명령어
    subparsers.add_parser("undo", help="마지막 작업을 실행 취소합니다. (약어: u)")
    # 'redo' 명령어
    subparsers.add_parser("redo", help="마지막 실행 취소를 다시 실행합니다. (약어: r)")

    # 'log' 명령어
    log_parser = subparsers.add_parser("log", help="실행된 명령어 기록을 보여줍니다.")
    log_parser.add_argument("--last", type=int, help="최근 N개의 명령어만 보여줍니다.")
    log_parser.add_argument("--clear", action="store_true", help="명령어 기록을 삭제합니다.")

    # sys.argv 조작 (argparse 파싱 전에)
    is_implicit_list = False
    if len(sys.argv) == 1: # todo만 입력했을 때
        # 할 일 목록이 비어있으면 도움말 출력, 아니면 'list' 명령어 삽입
        # current_todos = load_todos() # 중복 호출 제거
        # if not current_todos:
        #     parser.print_help()
        #     return # 도움말 출력 후 종료
        # else:
        sys.argv.insert(1, "list")
        is_implicit_list = True
    elif len(sys.argv) > 1:
        first_arg = sys.argv[1]
        # 첫 번째 인자가 유효한 명령어도 아니고, 옵션도 아니라면 'add' 명령어를 삽입
        if first_arg not in valid_commands and not first_arg.startswith('-'):
            sys.argv.insert(1, "add")

    # 약어 매핑 (기존 로직 유지)
    if len(sys.argv) > 1 and sys.argv[1] in alias_map:
        sys.argv[1] = alias_map[sys.argv[1]]

    args = parser.parse_args()

    # 'log' 명령어는 기록하지 않음
    # 암시적으로 'list'가 호출된 경우도 기록하지 않음
    if args.command != "log" and not (args.command == "list" and is_implicit_list):
        log_command(args.command, args)

    if args.command == "add":
        add_todo(args.description, args.due_date, args.priority, args.tags)
        list_todos()
    elif args.command == "list":
        list_todos(status_filter=args.status, sort_by=args.sort_by, tag_filter=args.tag_filter)
    elif args.command == "search":
        list_todos(search_term=args.keyword)
    elif args.command == "complete":
        complete_todo(args.index - 1)
        list_todos()
    elif args.command == "delete":
        # 여러 개 입력받으므로 각각 1 빼기
        delete_todo([i-1 for i in args.indexes])
        list_todos()
    elif args.command == "edit":
        if not any([args.new_description, args.new_due_date, args.new_priority, args.new_tags]):
            print("수정할 내용을 하나 이상 입력해야 합니다. --desc, --due, --priority, --tags 옵션을 확인하세요.")
        else:
            edit_todo(args.index - 1, args.new_description, args.new_due_date, args.new_priority, args.new_tags)
            list_todos()
    elif args.command == "clear":
        clear_completed_todos()
        list_todos()
    elif args.command == "undo":
        pop_undo()
    elif args.command == "redo":
        pop_redo()
    elif args.command == "log":
        if args.clear:
            clear_command_history()
            return
        history = get_command_history()
        if args.last:
            history = history[-args.last:]
        if not history:
            print("명령어 기록이 없습니다.")
            return
        print(f"{Colors.GRAY}─────────────── 명령어 기록 ────────────────{Colors.ENDC}")
        print()
        for entry in history:
            cmd = entry.get('command', 'N/A')
            timestamp = entry.get('timestamp', 'N/A')
            arg_dict = entry.get('args', {})
            # 'command' 키는 이미 cmd 변수에 있으므로 제외하고 출력
            display_args = {k: v for k, v in arg_dict.items() if k != 'command' and v is not None}
            arg_str = ' '.join([f"--{k} {v}" if v else f"--{k}" for k, v in display_args.items()])
            print(f"[{timestamp}] todo {cmd} {arg_str}")
        print(f"{Colors.GRAY}────────────────────────────────────{Colors.ENDC}")
        print()

if __name__ == "__main__":
    main()