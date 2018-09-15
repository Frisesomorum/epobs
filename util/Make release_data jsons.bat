python csv2json.py release_data_fund.csv finance.Fund
python csv2json.py release_data_exp_cat.csv finance.ExpenseCategory
python csv2json.py release_data_rev_cat.csv finance.RevenueCategory
python csv2json.py release_data_exp_la.csv finance.ExpenseLedgerAccount
python csv2json.py release_data_rev_la.csv finance.RevenueLedgerAccount

del release_data.json

type release_data_fund.json >> release_data.json
type release_data_exp_cat.json >> release_data.json
type release_data_rev_cat.json >> release_data.json
type release_data_exp_la.json >> release_data.json
type release_data_rev_la.json >> release_data.json

move /Y release_data.json ..\epobs-django\fixtures\

del release_data_fund.json
del release_data_exp_cat.json
del release_data_rev_cat.json
del release_data_exp_la.json
del release_data_rev_la.json
