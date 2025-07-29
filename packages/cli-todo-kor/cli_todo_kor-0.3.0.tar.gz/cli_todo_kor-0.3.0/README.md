# cli-todo-kor

CLI 기반 일정/할 일(todo) 관리 프로그램입니다.

## 주요 특징
- **명령어**로 할 일 추가/수정/삭제/완료/검색/정렬
- **우선순위, 마감기한, 완료여부** 등 필터링 및 정렬
- **Undo/Redo** 기능
- **컬러 출력**과 UI
- **리스트 출력**으로 최신 상태 확인
- **통계 제공** (전체/미완료/오늘 마감)

## 설치 및 실행 방법

### 1. 설치

아래 명령어 한 줄이면 바로 설치할 수 있습니다.

```bash
pip install cli-todo-kor
```

설치 후 터미널에서 아래처럼 사용하세요:

```bash
todo add "할 일 내용" --priority h --due 2024-06-30
todo list
todo complete 2
todo delete 3
todo edit 1 --desc "새로운 내용" --priority m --due 2024-07-01
todo search "키워드"
todo undo
todo redo
```

### 2. 삭제(제거)
```bash
pip uninstall cli-todo-kor
```

### 3. (참고) 파이썬 파일 직접 실행
아래 방식도 동작합니다.
```bash
python3 src/todo.py add "할 일 내용"
```

## 사용법 예시
### 할 일 추가
```bash
todo add "할 일 내용" --priority h --due 3
```

### 할 일 목록 보기
```bash
todo list
```

### 할 일 완료 처리
```bash
todo complete 2
```

### 할 일 삭제
```bash
todo delete 3
```

### 할 일 수정
```bash
todo edit 1 --desc "새로운 내용" --priority m --due 2
```

### 검색/정렬/필터
```bash
todo search "키워드"
todo list --sort-by due-date
todo list --status completed
```

### Undo/Redo
```bash
todo undo
todo redo
```

## 명령어 요약
- `add`       : 할 일 추가
- `list`      : 할 일 목록 보기
- `complete`  : 할 일 완료 처리
- `delete`    : 할 일 삭제
- `edit`      : 할 일 수정
- `search`    : 키워드로 검색
- `clear`     : 완료된 할 일 일괄 삭제
- `undo`      : 마지막 작업 취소
- `redo`      : 취소한 작업 복구
