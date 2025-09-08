from json import dumps

def create_config_file(path='cfg.json'):
    firstname, initials = input("Введите данные пользователя (Фамилия Инициалы): ").split()
    api_key = input("Введите API-ключ Redmine(https://red.eltex.loc/my/account): ").strip()
    config = {
        "redmine" : {
            "REDMINE_URL": "https://red.eltex.loc/",
            "API_KEY": api_key
        },
        "user": {
            "firstname": firstname,
            "initials": initials
        }
    }
    with open(path, 'w', encoding='utf-8') as f:
        f.write(dumps(config, ensure_ascii=False, indent=4))
    f.close()

def create_cfg_if_not_exist(CFG_PATH: str):
    try:
        open(CFG_PATH, 'r', encoding='utf-8')
    except FileNotFoundError:
        create_config_file(CFG_PATH)
    except Exception as e:
        print(f"Неизвестная ошибка при чтении/создании конфигурации: {e}")
        raise