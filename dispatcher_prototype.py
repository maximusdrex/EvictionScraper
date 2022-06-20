
from db_prototype import EvictDBManager
from scrape_prototype import Scraper
from search_headless import HeadlessSearch
import threading

class ScrapeThread (threading.Thread):
    def __init__(self, case):
        threading.Thread.__init__(self)
        self.case = case
    def run(self):
        print(self.case)
        add_case(self.case)


db = EvictDBManager()

queries = ["2022-CVG-00{}*".format(i) for i in range(16,50)]


if __name__ == '__main__':
    db.create_tables()

    #searcher = HeadlessSearch(queries, debug=2)
    #searcher.run()

    #case_ids = db.get_new_cases()
    case_ids = db.get_cases()

    scraper = Scraper(2)

    #threads = [ScrapeThread(case) for case in case_ids]
    #[t.start() for t in threads]
    #for t in threads:
    #    t.join()
    #print("Finished!!")
    #failed = [case for case in case_ids if not scraper.add_case(case)]
    #print(failed)
    failed = []
    for case in case_ids:
        try:
            success = scraper.add_case(case)
        except:
            print("{} failed".format(case))
        if(not success): 
            print("failure")
            failed.append(case)
    print(failed)
    #scraper.add_case("4221824")
    print("Finished!!")


# Search from 2022-CVG-0016* to 2022-CVG-0049*