from datetime import datetime, timedelta

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