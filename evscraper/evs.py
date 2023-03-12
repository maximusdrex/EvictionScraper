################################
# Eviction Scraper: Dispatcher
#   Runs the search and scraping functions of the scraper
# Maxwell Schaefer (mrs314@case.edu)
#################################

from evscraper.db_nosql import EvictDBManager
from evscraper.scraper import Scraper
import sys

db = EvictDBManager()


# Holds case_ids of cases that need to be scraped
# The dispatcher sends the first object in the queue to the scraper when it needs another case
# The searcher adds new cases to the queue
# This functionality is TODO, search and scrape will be seperated into parallel tasks via multi-threading
queue = []

def run():
    db.create_tables()
    # Create the Scraper object
    scraper = Scraper(2)
    
    if(len(sys.argv) > 1):
        try:
            case = int(sys.argv[1])
        except ValueError:
            case = 0
        # Search starting at number specified in command-line arguments
        scraper.search(start_num=case)
    else:
        # Search all new cases for evictions
        scraper.search()

    # Scrape any new cases added to the db
    case_ids = db.get_new_cases()
    print(len(case_ids))

    # Cases that failed to scrape are added to the failure list
    # This list will be used to make further attempts at these cases in future versions
    failed = []
    for case in case_ids:
        success = None
        try:
            success = scraper.add_case(case)
        except:
            print("{} failed".format(case))
        if(not success):
            print("failure")
            failed.append(case)
    print(failed)
    print("Finished")

if __name__ == '__main__':
    run()