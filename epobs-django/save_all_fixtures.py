import os
# from django.core import management
# would be nice if this worked..
# management.call_command(
#    'dumpdata', 'personnel.department', output='fixtures/release/department.json',
#    indent=2, use_natural_foreign_keys=True, use_natural_primary_keys=True)
# management.call_command(
#    'dumpdata', 'auth.group', output='fixtures/release/group.json',
#    indent=2, use_natural_foreign_keys=True, use_natural_primary_keys=True)
# management.call_command(
#    'dumpdata', 'schoolauth.school', 'schoolauth.user', 'schoolauth.userschoolmembership',
#    output='fixtures/test/user.json',
#    indent=2, use_natural_foreign_keys=True, use_natural_primary_keys=True)

os.system(
    "python manage.py dumpdata auth.group"
    + " --indent 2 --natural-foreign --natural-primary"
    + " -o fixtures/release/group.json")
os.system(
    "python manage.py dumpdata finance.fund finance.expensecategory"
    + " finance.expenseledgeraccount finance.revenuecategory finance.revenueledgeraccount"
    + " --indent 2 --natural-foreign --natural-primary"
    + " -o fixtures/release/ledger_account.json")
os.system(
    "python manage.py dumpdata personnel.department"
    + " --indent 2 --natural-foreign --natural-primary"
    + " -o fixtures/release/department.json")
os.system(
    "python manage.py dumpdata schoolauth.school schoolauth.user schoolauth.userschoolmembership"
    + " --indent 2 --natural-foreign --natural-primary"
    + " -o fixtures/test/user.json")
