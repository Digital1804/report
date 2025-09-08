from modules.configure import create_cfg_if_not_exist
from modules.report import Report
from modules.redmine_api import generate_monthly_report
from json import load
import requests

def main(CFG_PATH: str):
    with open(CFG_PATH, 'r', encoding='utf-8') as file:
        config = load(file)
    config_user    = config['user']
    config_redmine = config['redmine']

    REDMINE_URL    = config_redmine["REDMINE_URL"]
    headers = {
        'X-Redmine-API-Key': config_redmine["API_KEY"],
        'Content-Type': 'application/json'
    }

    current_user = requests.get(f'{REDMINE_URL}/users/current.json', headers=headers).json()

    user_id = current_user['user']['id']

    # Формируем отчет
    report = Report()
    generate_monthly_report(REDMINE_URL, headers, report.get_data(), user_id)

    print(report.create_odt_report(config_user["firstname"], config_user["initials"]), "сформирован")

if __name__ == "__main__":
    CFG_PATH = 'report_config.json'
    create_cfg_if_not_exist(CFG_PATH)
    main(CFG_PATH)
