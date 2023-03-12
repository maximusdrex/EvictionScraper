################################
# Eviction Scraper: Scraper
#   Scrapes the Cleveland Municipal Courts website by making requests to its internal api and processing the responses 
#   Gathers new cases by attempting all case numbers newer than the latest in the database, then checking if they are eviction cases
# Maxwell Schaefer (mrs314@case.edu)
#################################
import requests
import re
import json

from evscraper.db_nosql import EvictDBManager

# This is the base url of all requests made by this scraper
# The RegisterOfActionsService API is not protected by captcha and is the source for all necessary info
INFO_URL = 'https://portal.cmcoh.org/app/RegisterOfActionsService/'

# The CASE_INFO object holds the structure of all relevant requests, most are similarly structured and just need the id replaced
# To make a request for one of these objects, just append the values of this object to the base url and replace the case id
CASE_INFO= {
    "CaseSummary":"CaseSummariesSlim?key={id}",
    "CombinedEvents":"CombinedEvents(\'{id}\')",
    "DispositionEvents":"DispositionEvents(\'{id}\')",
    "Parties":"Parties(\'{id}\')",
    "Hearings":"Hearings(\'{id}\')",
    "HearingNoticeHistories":"HearingNoticeHistories(\'{id}\')",
    "ServiceEvents":"ServiceEvents(\'{id}\')",
    "OtherDocuments":"OtherDocuments(\'{id}\')",
    "FinancialSummary":"FinancialSummary(\'{id}\')",
    "Conditions":"Conditions(\'{id}\')",
    "BondSettings":"BondSettings(\'{id}\')",
    "TimeStandards":"TimeStandards(\'{id}\')",
    "Charges":"Charges(\'{id}\')",
}

#This constant is how many cases it will take to decide that the final case has been reached
#There are gaps in the data since cases can be removed, I haven't encountered more than 3-4 at once
#however, I set it high as a precautionary measure. It does take time though so lowering this may speed
#up the serach process if searching is repeated often
MAX_COUNT = 100

# Scraper Class definition
class Scraper:
    def __init__(self, debug=1, file="scrape.log"):
        self.debug_level = debug
        self.debug_file = file

    def log(self, level, msg):
        if(self.debug_level >= level):
            f = open(self.debug_file, "a+")
            f.write("\n" + msg)


    def get_api_key(self, case_id):
        params = {'id': case_id}
        try:
            r = requests.get("https://portal.cmcoh.org/CMCPORTAL/ResolveWebIntent/ViewCase", params=params)
        except:
            return "err"
        id_match = re.search(r"\?id=(.*)(?:\&|\\)",r.text)
        return id_match.group(1)

    def get_info(self, case_id, data_type):
        search_url = INFO_URL + data_type.format(id=case_id)
        info_params={'mode':'portalembed', '$top':'200', '$skip':'0'}
        try:
            d = requests.get(search_url, params=info_params)
        except:
            return "err"
        if(d.text == None):
            return "NONE"
        else:
            try:
                return json.loads(d.text)
            except:
                return "NONE"

    # Search for new cases
    def search(self, start_num=0):
        db = EvictDBManager()
        if(start_num == 0):
            id = db.get_max_case()
        else:
            id = start_num
        last_id = 0
        count = 0
        while(count < MAX_COUNT):
            id+=1
            temp = self.get_info(self.get_api_key(id), CASE_INFO["CaseSummary"])
            if(temp != "NONE"):
                count = 0
                last_id = id
                try:
                    if(temp["CaseInformation"]["CaseType"]["Word"] == "CVGHE"):
                        new_case = {"ID": id, "Name": temp["CaseSummaryHeader"]["CaseNumber"], "Date": temp["CaseSummaryHeader"]["FiledOn"]}
                        print("id {} is eviction, adding {}".format(id, new_case["Name"]))
                        db.add_search(new_case, False)
                except:
                    self.log(2, "error case {}".format(id))
            else:
                count += 1
        if(last_id > 0):
            print("Final id: {}".format(last_id))
        db.commit()
    


    #TODO: split up into better functions (works for now though)
    def add_case(self, case_id):
        api_key = self.get_api_key(case_id)
        if (api_key == "err"):
            self.log(1, "Couldn't get API key")
            return False
        
        print("\n\n")
        data = {}
        for key in CASE_INFO:
            print(key)
            data[key] = self.get_info(api_key, CASE_INFO[key])
            if(data[key] == "err"):
                self.log(1, "Couldn't get data: {}".format(key))
                return False


        print("\n\n")
        Hearings_Raw = [x for x in data["CombinedEvents"]["Events"] if x["Type"]=="HearingEvent"]

        print(Hearings_Raw)
        print("\n\n")


        #Parse Hearings, extracts date/time, event type, event result, judge desc, and stores raw json
        Hearings = [{"Datetime":x["HearingTime"], "EventType":x["EventType"], "json":json.dumps(x)} for x in Hearings_Raw]
        for i in range(len(Hearings)):
            try:
                Hearings[i]["JudgeOrMagistrateDesc"] = Hearings_Raw[i]["JudgeOrMagistrateDesc"]
            except:
                Hearings[i]["JudgeOrMagistrateDesc"] = None
                print("No Judge/Magistrate")
            try:
                Hearings[i]["Result"] = Hearings_Raw[i]["Event"]["Setting"]["ResultId"]["Description"]
            except:
                Hearings[i]["Result"] = None
                print("No Result")
        
        print(Hearings)


        Events_Raw = [x for x in data["CombinedEvents"]["Events"] if x["Type"]!="HearingEvent"]
        #Parse Events   
        Events = [{"Datetime":x["TimestampCreate"][0:-4], 
                    "EventType":x["Event"]["TypeId"]["Description"]} for x in Events_Raw]
        for key in range(len(Events)):
            if len(Events[key]["EventType"]) > 128:
                Events[key]["EventType"] = Events[key]["EventType"][0:127]

        #Parse parties (not attorneys or properties)
        PartiesRaw = [x for x in data["Parties"]["Parties"] if x["ConnectionTypes"][0]=="Plaintiff" or x["ConnectionTypes"][0]=="Defendant"]
        Parties = [{"P/D":x["ConnectionTypes"][0], "Name":x["FormattedName"]} for x in PartiesRaw]
        for i in range(len(Parties)):
            try:
                Parties[i]["Address"] = PartiesRaw[i]["Addresses"][0]["AddressLine1"]
            except:
                Parties[i]["Address"] = None
                print("No Address")
            try:
                Parties[i]["Zip"] = PartiesRaw[i]["Addresses"][0]["PostalCode"]
            except:
                Parties[i]["Zip"] = None
                print("No Zip")
            try:
                Parties[i]["State"] = PartiesRaw[i]["Addresses"][0]["State"]
            except:
                Parties[i]["State"] = None
                print("No State")
            try:
                Parties[i]["City"] = PartiesRaw[i]["Addresses"][0]["City"]
            except:
                Parties[i]["City"] = None
                print("No City")

        # Parse attorneys
        Attorneys = []
        for x in data["Parties"]["Parties"]:
            if len(x["CasePartyAttorneys"]) > 0:
                for i in range(len(x["CasePartyAttorneys"])):
                    Attorneys.append({"Name":x["CasePartyAttorneys"][i]["FormattedName"], "Appointment":x["CasePartyAttorneys"][i]["Appointment"], "Client":x["FormattedName"], "P/D":x["ConnectionTypes"][0], "json":json.dumps(x["CasePartyAttorneys"][i])})

        # Parse Properties
        Properties = []
        PropertiesRaw = [x for x in data["Parties"]["Parties"] if x["ConnectionTypes"][0]=="Property Address"]
        try:
            Properties = [{"Address":x["Addresses"][0]["AddressLine1"], "P/D": "Property Address"} for x in PropertiesRaw]
            for i in range(len(Properties)):
                try:
                    Properties[i]["Zip"] = PropertiesRaw[i]["Addresses"][0]["PostalCode"]
                except:
                    Properties[i]["Zip"] = None
                    print("No Zip")
                try:
                    Properties[i]["State"] = PropertiesRaw[i]["Addresses"][0]["State"]
                except:
                    Properties[i]["State"] = None
                    print("No State")
                try:
                    Properties[i]["City"] = PropertiesRaw[i]["Addresses"][0]["City"]
                except:
                    Properties[i]["City"] = None
                    print("No City")
        except:
            Properties = []
            for Property in PropertiesRaw:
                try:
                    Properties.append({"Address":Property["Addresses"][0]["AddressLine1"], "P/D":"Property Address", "Zip":None, "City":None, "State":None})
                except:
                    Properties.append({"Address":Property["FormattedName"], "P/D":"Property Address", "Zip":None, "City":None, "State":None})

        # Parse case information
        CasesRaw = data["CaseSummary"]

        Case = {"Name": CasesRaw["CaseSummaryHeader"]["Style"].replace("\n", " "), 
                "Type": CasesRaw["CaseInformation"]["CaseType"]["Description"], 
                "Number":CasesRaw["CaseSummaryHeader"]["CaseNumber"], 
                "Status":CasesRaw["CaseInformation"]["CaseStatuses"][0]["CaseStatusId"]["Description"],
                "StatusDate":CasesRaw["CaseInformation"]["CaseStatuses"][0]["StatusDate"],
                "FileDate":CasesRaw["CaseSummaryHeader"]["FiledOn"]
                }
        try:
            Case["DispositionDate"] = CasesRaw["DispositionInformation"]["Dispositions"][0]["DispositionDate"]
            Case["Disposition"] = CasesRaw["DispositionInformation"]["Dispositions"][0]["DispositionTypeId"]["Description"]
        except:
            Case["DispositionDate"] = None
            Case["Disposition"] = None


        if(self.debug_level>2):
            f = open("{}.log".format(Case["Number"]), "w+")
            f.write(str(data["CaseSummary"]))

        Finances_Raw = [x for x in data["FinancialSummary"]["CaseFees"]]
        Finances = [{
            "Description":x["FinancialCategory"]["Description"],
            "Connection":x["Party"]["ConnectionType"],
            "Party_Name":x["Party"]["FormattedName"],
            "Balance":x["CaseFeeParty"]["Balance"],
            "Last_Viewed":x["DueDate"],
            "Assesed":x["CaseFeeParty"]["Charges"],
            "Payments":x["CaseFeeParty"]["Payments"] + x["CaseFeeParty"]["Credits"],
            "Transactions":[{
                "ID":t["TranId"],
                "Type":t["TypeKey"]["Description"],
                "Code":t["TypeKey"]["Word"],
                "Date":t["Date"],
                "Receipt":t["ReceiptNum"],
                "Chg":t["ChgAmt"] - t["PayAmt"] - t["CreditAmt"]
            } for t in x["CaseFeeParty"]["TransBalances"]["TransBalances"]]
        } for x in Finances_Raw]

        print(Finances)
        ## Add to DB

        db = EvictDBManager()

        # Add case
        print(Case)
        db.add_case(case_id, Case)

        # Add parties

        for party in Parties:
            party_id = db.add_party(party, case_id, False)
            print(party_id)
            ad = party.get("Address")
            if ad and party_id:
                db.add_address(case_id, party_id[0], party)

        print("added parties")
        for party in Attorneys: 
            party_id = db.add_party(party, case_id, True)
            ad = party.get("Address")
            if ad and party_id:
                db.add_address(case_id, party_id[0], party)

        for property in Properties:
            print(property)
            db.add_address(case_id, None, property)

        print("added attorneys")

        db.commit()

        # Add Events

        for event in Events:
            db.add_event(case_id, event)

        for hearing in Hearings:
            db.add_hearing(case_id, hearing)

        for finance in Finances:
            fin_id = db.add_fin(case_id, finance)
            if fin_id:
                print(int(fin_id[0]))
                for t in finance["Transactions"]:
                    db.add_transaction(fin_id[0], t)

        db.commit()
        db.close()
        self.log(2, "Added Case: {}".format(Case["Number"]))
        return True

if __name__=='__main__':
    scraper = Scraper(debug=3)
    scraper.search()
        