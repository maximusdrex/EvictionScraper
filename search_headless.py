from cmath import log
from time import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from lxml import html

from db_nosql import EvictDBManager

DEBUG_LEVEL = 1
DEBUG_FILE = "search.log"

class HeadlessSearch:
    def __init__(self, queries, debug=1, file="search.log"):
        self.queries = queries
        self.debug = debug
        self.debug_file = file
        

    
    def log(self, level, msg):
        if(self.debug >= level):
            f = open(self.debug_file, "a+")
            f.write("\n" + msg)


    def get_cases(self, query):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)

        #retry the search until cases are loaded correctly
        #TODO: find a way to make this better, at the moment sometimes searches will fail for no apparent reason
        err_flag = True
        while(err_flag):
            #Go to the smart search website
            driver.get("https://portal.cmcoh.org/CMCPORTAL/Home/Dashboard/29")
            #Search for "given query"
            element = driver.find_element(By.ID, "caseCriteria_SearchCriteria")
            element.send_keys(query)
            button = driver.find_element(By.ID, "btnSSSubmit")
            button.click()

            #Wait for 5 seconds
            #TODO: Fix the wait to actually use the webdriverwait correctly and wait for loading message to go away
            print("waiting")
            t = time()
            driver.implicitly_wait(5) #5 second wait
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.locator"))
                )
            finally:
                print(str(time() - t) + "s")
                #Save a screenshot of the webpage (for debugging purposes)
                driver.save_screenshot('search_results.png')    


            try:
                err_msg = driver.find_element(By.XPATH, '//p[text()= "There was an error while processing your request. Please try again later."]')
                print("will err")
            except:
                err_flag = False
                print("cases found")
                

        cases = []
        try:
            element = driver.find_element(By.ID, "CasesGrid")
            if(element):
                root = html.fromstring(element.get_attribute("innerHTML"))
                raw_ids = root.xpath('//a/@data-caseid')      
                for id in raw_ids:
                    Case = {
                        "ID": int(id),
                        "Name": root.xpath('//*[@data-caseid="{}"]/@title'.format(id))[0],
                        "Date": root.xpath('//*[@data-caseid="{}"]/../../td[@data-label="File Date"]/span/@title'.format(id))[0]
                    }
                    cases.append(Case)

                more_pages = False
                try:
                    nextbutton = driver.find_element(By.XPATH, '//a[@title="Go to the next page"]')
                    more_pages = not "k-state-disabled" in nextbutton.get_attribute("class")

                    while(more_pages):
                        nextbutton.click()
                        element = driver.find_element(By.ID, "CasesGrid")
                        root = html.fromstring(element.get_attribute("innerHTML"))
                        raw_ids = root.xpath('//a/@data-caseid')      
                        for id in raw_ids:
                            Case = {
                                "ID": int(id),
                                "Name": root.xpath('//*[@data-caseid="{}"]/@title'.format(id))[0],
                                "Date": root.xpath('//*[@data-caseid="{}"]/../../td[@data-label="File Date"]/span/@title'.format(id))[0]
                            }
                            cases.append(Case)
                        nextbutton = driver.find_element(By.XPATH, '//a[@title="Go to the next page"]')
                        more_pages = not "k-state-disabled" in nextbutton.get_attribute("class")
                    print(cases)
                    return cases
                except:
                    self.log(2, "no more pages")
                    return cases
            else:
                print("error")
                
        except:
            self.log(0, "error getting results")
            print("error getting results")
            #page = driver.find_element(By.XPATH, ("//body"));
            #elementSource = page.get_attribute("innerHTML");
            #text_file = open("body.html", "w")
            #n = text_file.write(elementSource)
            #text_file.close()
        finally:
            driver.quit()
        return None

    def add_results(self, cases):
        db = EvictDBManager()
        for case in cases:
            #TODO:Add a status indicator for the dispatcher
            db.add_search(case)
        self.log(2, "Added cases from search to db")
        db.commit()
        db.close()

    def add_cases(self, case_list):
        if case_list:
            if len(case_list) > 0:
                self.add_results(case_list)
                return True
        return False

    def run_query(self, case):
        if(self.add_cases(self.get_cases(case))):
            self.log(2, "\nadded: {}".format(case))
            return True
        else:
            self.log(1, "failed: {}".format(case))
            return False

    def run(self):
        self.log(1, "test")
        for case in self.queries:
            if(self.run_query(case)):
                self.log(2, "ran query succesfully")
            else:
                self.log(1, "queued query for retry")
                self.queries.append(case)
