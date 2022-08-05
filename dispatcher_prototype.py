from db_nosql import EvictDBManager
from scrape_prototype import Scraper
from search_headless import HeadlessSearch

db = EvictDBManager()

queries = ["2022-CVG-00{}*".format(i) for i in range(16,56)]


if __name__ == '__main__':
    db.create_tables()

    #searcher = HeadlessSearch(queries, debug=2)
    #searcher.run()

    case_ids = db.get_new_cases()
    #case_ids = db.get_cases()

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
        success = None
        #try:
        success = scraper.add_case(case)
        #except:
        #    print("{} failed".format(case))
        #if(not success):
        #    print("failure")
        #    failed.append(case)
    print(failed)
    print("Finished!!")


# Search from 2022-CVG-0016* to 2022-CVG-0049*