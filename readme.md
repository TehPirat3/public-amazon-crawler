# Amazon Category Crawler and Product Detail Extractor
amazon.com crawler written in python with following features:

 * simultaneous requests and multithreading, number of threads can be changed from settings.py
 * rotates proxy servers from proxy pool
 * uses Redis to queue URL for requests, so the process can be continued if the run stops
 * logs progress and warning conditions to a file for later analysis
 * in case a page link is not responding or is detected for bot usage, bitlyshortener api is used to shorten the link to get rid of tailing parameters and request is retried. 



## Getting it Setup
To run for a single item code, e.g. "B07Y91T141"

    python detail_extractor.py

To run on a category of items

    python crawler.py


`settings.py` has configurations for the followings:

 * **Database Name, Host and User** - Connection information for storing products in a postgres database (stores data taken from browsing page)
 * **Redis Host, Port and Database** - Connection information for storing the URL queue in redis
 * **Proxy List as well as User, Password and Port** - Connection information for your list of proxy servers
 * **MongoDB Server, Port, DB name and Collection** - Connection information for storing product details in a mongodb document
 * **Start file information** - Path for a .txt file which contains links of categories
 * **Headers and Random User-Agent** - Updates headers with new random User-Agent for each request
 * **Number of threads, limit of requests and entries per listing** - Can be configured to meet the needs of scraping logic

The fields that are stored for each product from browsing page are the following:

 * title
 * product_url *(URL for the detail page)*
 * listing_url *(URL of the subcategory listing page we found this product on)*
 * price
 * primary_img *(the URL to the full-size primary product image)*
 * crawl_time *(the timestamp of when the crawl began)*

The fields that are stored for each product from product page are the following:
 * Item id *(Unique for each item in Amazon)*
 * Shipping Message
 * Item Features
 * Item Color
 * Seller Name 
 * Item Input Id
 * Item attributes
 * Shipping Price
 * Item Title
 * Seller Id *(Id of a seller found in Amazon)*
 * Related products' asins
 * Store Name
 * Deal of the day *(True or False flag)*
 * Item Specific information
 * Price
 * Brand
 * Response Received *(Time when request was received)*
 * Proxy *(Proxy ip address)*
 * Categories *(Categories under which item is located)*
 * Manufacturer 
 * Images *(All images of product)*
 * Start Request *(Time when the request was sent)
 * Get variations *(Item attribute variations)*
 * URL
 * Before Deal Price *(Applicable if the item's price is discounted, otherwise returns 'None')*
 * Category Id *(Subcategory id)*
 * Order min qty *(Minimum quantity to order the item)*

## How it Works

    python crawler.py 

This runs a function that crawls subcategories of a category URLs stored in the `start-urls.txt` file. Each of these subcategory URLs is placed in the redis queue that holds the frontier listing URLs to be crawled.

Then the program takes number of threads defined in `settings.max_threads` and each one of those threads pops a listing URL from the queue, makes a request to it and then stores the products found on the listing page. Also takes the "next page" URL and puts that in the queue.


## Known Limitations
Amazon uses different styles of markup depending on the category and product type, thus some category items can not be found using the lookup in extractors. 

Proxy servers are public which sometimes slows down the requests.

Received HTML is checked and if it misses crucial information request is retried for number of times defined in `sys.setrecursionlimit` argument. 