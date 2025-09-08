from datetime import datetime, timedelta
import requests

STATUSES: dict[str, int] = {
    "New"          : 1,
    "In Progress"  : 2,
    "Resolved"     : 3,
    "Pending"      : 4,
    "Closed"       : 5,
    "Rejected"     : 6,
    "Confirming"   : 7,
    "Re-opened"    : 8,
    "Testing"      : 9,
    "Wait Release" : 10,
    "Code Review"  : 11,
    "Frozen"       : 12,
    "Feedback"     : 13
}

def float_to_time(float_hours: float) -> str:
    """
    Конвертирует десятичные часы в формат ЧЧ:ММ
    """
    hours = int(float_hours)
    minutes = int(round((float_hours - hours) * 60))
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{hours}:{minutes:02d}"


def safe_get(json_obj: dict, *keys, default=""):
    cur = json_obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def get_user_issues(redmine_url: str, headers: dict[str, str], user_id: int) -> list:
    params = {
        'assigned_to_id': user_id,
        'limit': 100
    }

    response = requests.get(f'{redmine_url}/issues.json',
                          headers=headers,
                          params=params)
    return response.json().get('issues', [])


def get_time_entries(redmine_url: str, headers: dict[str, str], issue_id: int, from_date: datetime) -> list:
    response = requests.get(
        f'{redmine_url}/time_entries.json?issue_id={issue_id}&from={from_date}',
        headers=headers
    )
    return response.json().get('time_entries', [])


def generate_monthly_report(redmine_url: str,
                            headers: dict[str, str],
                            report: dict[str, list],
                            user_id: int) -> list:
    month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=28)
    from_date = month.date()
    issues = get_user_issues(redmine_url, headers, user_id)

    for issue in issues:
        issue_id = issue.get('id')
        if not issue_id:
            continue

        time_entries = get_time_entries(redmine_url, headers, issue_id, str(from_date))
        spent = sum(entry.get('hours', 0) for entry in time_entries)

        record = {
            'Наименование работы': safe_get(issue, 'project', 'name'),
            'Примечание': issue.get('subject', ''),
            'Статус': safe_get(issue, 'status', 'name'),
            'Затраченное время за отчётный период': float_to_time(round(spent, 2)) if spent > 0 else "",
            'Необходимо затратить в следующий период': "",
            'Срок завершения': issue.get('due_date', '')
        }

        status_name = record['Статус']
        if STATUSES.get(status_name) in {1, 2, 4, 7, 8, 12, 13} and spent == 0:
            report['next'].append(record)
        else:
            report['current'].append(record)


    return report
