============================================
Cleveland Municipal Court Eviction Case Scraper
============================================

--------------------------------------------
About
--------------------------------------------

This project scrapes data from eviciton cases in Cleveland from the court website.

To get data from the website, first the the scraper searches for the unique ids of the cases, and then it uses the website's API to return the data. 
To get the ids of the cases, ``search_headless.py`` runs a headless browser to search for all cases in a range. 
To get the data for each case ``scraper.py`` mimics the AJAX calls of the court website and inserts the data into a postgresql database.

Running ``dispatcher.py start end [-u]`` will currently search and scrape all cases between the start and end cases. The arguments should be in the format "YYYY-CVG-XXXXXX" and at the moment they both must be in the same year. Add the flag -u at the end to update the data, if the flag is not provided any cases already added will be skipped over, with the flag cases already added will be overwritten.

--------------
TODO:
--------------
* Reverse engineer the searching API so that headless browsing is no longer necessary
* Use multithreading to scrape data to increase speed
* Run the dispatcher with arguments to specify the range of cases to check