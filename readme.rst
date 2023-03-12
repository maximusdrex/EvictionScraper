============================================
Cleveland Municipal Court Eviction Case Scraper
============================================

--------------------------------------------
About
--------------------------------------------

This project scrapes data from eviciton cases in Cleveland from the court website.

To get data from the website, first the the scraper searches for the unique ids of the cases, and then it uses the website's API to return the data. 

--------------
Usage
--------------

If pip is installed, run pip install dist/evscraper-0.1.1-py3-none-any.whl. Then, the command ``evs`` will be installed. 
Run ``evs`` with no arguments to continue the scraper from the last case it scraped. Run with a case id after the command "``evs case_id``" to start searching at the specified id.

To build any changes, run python -m build (if build is installed), and then reinstall the .whl file.

To run without installing, simply run ``evs.py``.

--------------
TODO:
--------------
[x] Reverse engineer the searching API so that headless browsing is no longer necessary

[] Retry failed case scrapes

[] Increasing logging readability

[] Use multithreading to scrape data to increase speed

[] Handle user input during scrape to allow pausing/resuming
