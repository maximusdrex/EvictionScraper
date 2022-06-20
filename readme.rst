============================================
Cleveland Municipal Court Eviction Case Scraper
============================================

--------------------------------------------
About
--------------------------------------------

This project scrapes data from eviciton cases in Cleveland from the court website.

To get data from the website, first the the scraper searches for the unique ids of the cases, and then it uses the website's API to return the data. 
To get the ids of the cases, ``search_headless.py`` runs a headless browser to search for all cases in a range. 
To get the data for each case ``scrape_prototype.py`` mimics the AJAX calls of the court website and inserts the data into a postgresql database.

Running ``dispatcher_prototype.py`` will currently search and scrape all cases since March 2022.

--------------
TODO:
--------------
* Reverse engineer the searching API so that headless browsing is no longer necessary
* Use multithreading to scrape data to increase speed
* Run the dispatcher with arguments to specify the range of cases to check