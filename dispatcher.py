from db_nosql import EvictDBManager
from scraper import Scraper
from search_headless import HeadlessSearch
import sys

db = EvictDBManager()

#queries = ["2022-CVG-00{}*".format(i) for i in range(16,56)]


if __name__ == '__main__':
    update = False
    if(len(sys.argv) < 3):
        print("usage: scraper.py start end [-u] \n where start and end are case numbers in the format: YYYY-CVG-XXXXXX")
        exit()
    else:
        if(len(sys.argv) > 3):
            if (sys.argv[3] == "-u"):
                update = True
    
    starty = sys.argv[1][0:4]
    endy = sys.argv[2][0:4]
    
    if(not starty == endy):
        print("Scraping over multiple years is not yet supported")
        exit()
    
    startn = int(sys.argv[1][9:13])
    endn = int(sys.argv[2][9:13])
    if (endn < startn):
        print("End is before start!")
    
    queries = ["{}-CVG-{}*".format(starty, str(i).zfill(4)) for i in range(startn,endn+1)]
    print(queries)

    db.create_tables()

    searcher = HeadlessSearch(queries, u=update, debug=2)
    searcher.run()

    case_ids = db.get_new_cases()

    scraper = Scraper(2)

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


# Search from 2022-CVG-0016* to 2022-CVG-0049*