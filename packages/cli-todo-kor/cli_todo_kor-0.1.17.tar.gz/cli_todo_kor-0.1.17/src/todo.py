#!/usr/bin/env python3
import argparse
import sys
from datetime import timedelta
from core import (
    add_todo, edit_todo, complete_todo, delete_todo, 
    clear_completed_todos, load_todos
)
from display import list_todos
from undo import pop_undo, pop_redo
from utils import _parse_due_date

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

def main():
    todo_ascii_art = """
████████╗ ██████╗ ██████╗   ██████╗ 
╚══██╔══╝██╔═══██╗██╔═══██╗██╔═══██╗
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ██║   ██║██║   ██║██║   ██║
   ██║   ╚██████╔╝██████╔╝ ╚██████╔╝
   ╚═╝    ╚═════╝ ╚═════╝   ╚═════╝ 
"""
    description_text = f"{Colors.BOLD}{Colors.BLUE}{todo_ascii_art}{Colors.ENDC}\n\nCLI 기반 할 일 목록 관리자 (버전: 0.1.17) 사용 가능한 명령어:\n  add       새로운 할 일을 추가합니다.\n  list      할 일 목록을 보여줍니다.\n  complete  할 일을 완료 상태로 변경합니다.\n  delete    할 일을 삭제합니다.\n  edit      할 일을 수정합니다.\n  search    키워드로 할 일을 검색합니다.\n  clear     완료된 모든 할 일을 삭제합니다.\n  undo      마지막 작업을 실행 취소합니다.\n  redo      마지막 실행 취소를 다시 실행합니다.\n\n각 명령어의 상세 도움말: todo <명령어> -h"

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

    # sys.argv를 직접 파싱하여 약어 처리
    if len(sys.argv) > 1 and sys.argv[1] in alias_map:
        sys.argv[1] = alias_map[sys.argv[1]]

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

    # 'list' 명령어
    list_parser = subparsers.add_parser("list", help="할 일 목록을 보여줍니다. (약어: ls, l)")
    list_parser.add_argument("--status", type=str, choices=['pending', 'completed'], help="상태별로 필터링 (pending, completed)")
    list_parser.add_argument("--sort-by", type=str, choices=['priority', 'due-date', 'description', 'status'], default='priority', help="정렬 기준. 'priority'는 그룹화하여 표시(기본값), 그 외는 목록 정렬.")

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

    # 'clear' 명령어
    subparsers.add_parser("clear", help="완료된 모든 할 일을 삭제합니다. (약어: clr)")
    # 'undo' 명령어
    subparsers.add_parser("undo", help="마지막 작업을 실행 취소합니다. (약어: u)")
    # 'redo' 명령어
    subparsers.add_parser("redo", help="마지막 실행 취소를 다시 실행합니다. (약어: r)")

    
    args = parser.parse_args()

    # 명령어 없이 문자열만 입력한 경우 자동 add 처리
    if args.command is None:
        # sys.argv에서 스크립트명 제외 후 인자만 추출
        extra_args = sys.argv[1:]
        if len(extra_args) == 1:
            add_todo(extra_args[0])
            list_todos()
            return
        parser.print_help()
        return

    if args.command == "add":
        add_todo(args.description, args.due_date, args.priority)
        list_todos()
    elif args.command == "list":
        list_todos(status_filter=args.status, sort_by=args.sort_by)
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
        if not any([args.new_description, args.new_due_date, args.new_priority]):
            print("수정할 내용을 하나 이상 입력해야 합니다. --desc, --due, --priority 옵션을 확인하세요.")
        else:
            edit_todo(args.index - 1, args.new_description, args.new_due_date, args.new_priority)
            list_todos()
    elif args.command == "clear":
        clear_completed_todos()
        list_todos()
    elif args.command == "undo":
        pop_undo()
    elif args.command == "redo":
        pop_redo()

if __name__ == "__main__":
    main()