import os

os.system("python manage.py loaddata fixtures/release/group.json")
os.system("python manage.py loaddata fixtures/release/ledger_account.json")
os.system("python manage.py loaddata fixtures/release/department.json")
os.system("python manage.py loaddata fixtures/release/site_settings.json")
os.system("python manage.py loaddata fixtures/test/user.json")
