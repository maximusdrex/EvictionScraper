import json
import os

MIN_CASE_START =  4000000

class EvictDBManager:
    transactions = 1

    def __init__(self):
        self.searches = {"case_id": [], "case_num": [], "file_date": [], "status": []}
        self.cases = {"case_id": [], "file_date": [], "case_number": [], "case_name": [], "case_type":[], "disp_status":[], "disp_date":[]}
        self.events = {"id":[], "case_id": [], "docket_item_text":[], "docket_item_date": []}
        self.hearings = {"id": [], "case_id": [], "event_type":[], "jud_officer":[], "event_date":[], "result":[]}
        self.parties = {"party_id":[], "case_id":[], "is_attorney":[], "name":[], "type":[]}
        self.addresses = {"id":[], "party_id": [], "case_id":[], "address":[], "city":[], "state":[], "zip":[], "type":[]}
        self.finances = {"id":[], "party_id":[], "case_id":[], "amount_owed":[], "type":[], "payment_date":[], "balance":[], "payment_desc":[]}
        self.files = {
            "searches": ("output/searches.json", self.searches), 
            "cases": ("output/cases.json", self.cases), 
            "events": ("output/events.json", self.events),
            "hearings": ("output/hearings.json", self.hearings),
            "parties": ("output/parties.json", self.parties),
            "addresses": ("output/addresses.json", self.addresses),
            "finances": ("output/finances.json", self.finances)
        }
        self.create_tables()
        self.load()
        transactions = 1

    # automatically save every 50 transactions
    def transact(self):
        self.transactions += 1
        if(self.transactions % 50 == 0):
            self.commit()

    def close(self):
        for t in self.files:
            file = self.files[t][0]
            f = open(file, "a+")
            f.close()

    def commit(self):
        for t in self.files:
            file = self.files[t][0]
            f = open(file, "w+")
            f.write(json.dumps(self.files[t][1]))
            f.close()
    
    def load(self):
        for t in self.files:
            file = self.files[t][0]
            try:
                r = open(file, "r")
                try:
                    table = json.load(r)
                except:
                    print("file \"{}\" empty".format(file))
                    table = {}
                    for key in self.files[t][1]:
                        table[key] = []
                for key in self.files[t][1]:
                    self.files[t][1][key] = table[key]
                r.close()
            except FileNotFoundError:
                print("No file yet")

    def create_tables(self):
        try:
            os.mkdir("output")
        except FileExistsError: 
            print("Directory \"output\" already exists")
        for t in self.files:
            file = self.files[t][0]
            f = open(file, "a+")
            f.close()

    def add_search(self, case, u):
        self.transact()
        if(not u):
            if (case["ID"] not in self.searches["case_id"]):
                search = {"case_id": case["ID"], "case_num": case["Name"], "file_date": case["Date"], "status": "S"}
                for key in search:
                    self.searches[key].append(search[key])
        else:
            if (case["ID"] in self.searches["case_id"]):
                i = self.searches["case_id"].index(case["ID"])
                for key in self.searches:
                    del self.searches[key][i]
            search = {"case_id": case["ID"], "case_num": case["Name"], "file_date": case["Date"], "status": "S"}
            for key in search:
                self.searches[key].append(search[key])

        
    def add_party(self, party, case_id, attorney):
        idn = 0
        if(len(self.parties["party_id"]) > 0):
            idn = max(self.parties["party_id"]) + 1
        party = {"party_id": idn, "case_id": case_id, "is_attorney": attorney, "name": party["Name"], "type": party["P/D"]}
        for key in party:
            self.parties[key].append(party[key])
        return (idn, )

    def add_address(self, case_id, party_id, party):
        idn = 0
        if(len(self.addresses["id"]) > 0):
            idn = max(self.addresses["id"]) + 1
        address = {"id": idn, "party_id": party_id, "case_id":case_id, "address":party["Address"], "city":party["City"], "state":party["State"], "zip":party["Zip"], "type":party["P/D"]}
        for key in address:
            self.addresses[key].append(address[key])

    def add_case(self, case_id, case_obj):
        self.transact()
        case = {"case_id":  case_id, "file_date": case_obj["FileDate"], "case_number": case_obj["Number"], "case_name": case_obj["Name"], "case_type":case_obj["Type"], "disp_status":case_obj["Disposition"], "disp_date":case_obj["DispositionDate"]}
        for key in case:
            self.cases[key].append(case[key])

    def add_event(self, case_id, event):
        idn = 0
        if(len(self.events["id"]) > 0):
            idn = max(self.events["id"]) + 1
        event = {"id":idn, "case_id": case_id, "docket_item_text":event["EventType"], "docket_item_date": event["Datetime"]}
        for key in event:
            self.events[key].append(event[key])

    def add_hearing(self, case_id, hearing):
        idn = 0
        if(len(self.hearings["id"]) > 0):
            idn = max(self.hearings["id"]) + 1
        hearing = {"id": idn, "case_id": case_id, "event_type": hearing["EventType"], "jud_officer":hearing["JudgeOrMagistrateDesc"], "event_date":hearing["Datetime"], "result":hearing["Result"]}
        for key in hearing:
            self.hearings[key].append(hearing[key])

    def add_fin(self, case_id, fin):
        idn = 0
        if(len(self.finances["id"]) > 0):
            idn = max(self.finances["id"]) + 1
        pid = None
        for i, v in enumerate(self.parties["name"]):
            if(v == fin["Party_Name"] and self.parties["case_id"][i] == case_id):
                pid = self.parties["party_id"][i]
        finance = {"id":idn, "party_id":pid, "case_id":case_id, "amount_owed":fin["Assesed"], "type":fin["Connection"], "payment_date":["Last_Viewed"], "balance":fin["Balance"], "payment_desc":fin["Description"]}
        for key in finance:
            self.finances[key].append(finance[key])
        return (idn, )

    def add_transaction(self, fin_id, transaction):
        return True

    def get_searches(self):
        return self.searches["case_id"]

    def get_new_cases(self):
        print(self.searches["case_id"])
        return [x for x in self.get_searches() if x not in self.get_cases()]

    def get_cases(self):
        return self.cases["case_id"]

    def drop_tables(self):
        self.searches = {"case_id": [], "case_num": [], "file_date": [], "status": []}
        self.cases = {"case_id": [], "file_date": [], "case_number": [], "case_name": [], "case_type":[], "disp_status":[], "disp_date":[]}
        self.events = {"id":[], "case_id": [], "docket_item_text":[], "docket_item_date": []}
        self.hearings = {"id": [], "case_id": [], "event_type":[], "jud_officer":[], "event_date":[], "result":[]}
        self.parties = {"party_id":[], "case_id":[], "is_attorney":[], "name":[], "type":[]}
        self.addresses = {"id":[], "party_id": [], "case_id":[], "address":[], "city":[], "state":[], "zip":[], "type":[]}
        self.finances = {"id":[], "party_id":[], "case_id":[], "amount_owed":[], "type":[], "payment_date":[], "balance":[], "payment_desc":[]}

    def get_output(self):
        pass

    def get_table_cols(self, table):
        pass
    
    def get_table(self, table):
        pass

    def get_max_case(self):
        if(len(self.searches["case_id"]) > 0):
            return max(self.searches["case_id"])
        else:
            return MIN_CASE_START

if __name__ == '__main__':
    db = EvictDBManager()
    db.create_tables()
