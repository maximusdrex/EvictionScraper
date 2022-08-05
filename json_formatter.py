import json

from db_prototype import EvictDBManager

db = EvictDBManager()
#output_columns = ["Case ID", "Case Number", "File Date", "Case Status", "Case Type", "Status Date", "Address", "City", "Zip", "Move Out", "Case Name"]
#f = open("output.json", "w+")
#f.write(json.dumps([{col:it for col, it in zip(output_columns, [str(i) for i in item])} for item in db.get_output()]))
#f.close()
tables = ["addresses", "transactions", "finance", "cases", "events", "hearings", "parties"]
for table in tables:
    f = open("{}.json".format(table), "w+")
    cols = [i[0] for i in db.get_table_cols(table)]
    print(cols)
    f.write(json.dumps([{col:it for col, it in zip(cols, [str(i) for i in item])} for item in db.get_table(table)]))
    f.close()