import os
from fake_useragent import UserAgent

current_dir = os.path.dirname(os.path.realpath(__file__))

# Postgre SQL

database = "amazon_crawler"
host = "127.0.0.1"
user = "postgres"

# MongoDB

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "amazon"
MONGODB_COLLECTION = "products"

# Redis

redis_host = "127.0.0.1"
redis_port = 6379
redis_db = 0

# Request

ua = UserAgent()
hdr = {
    "User-Agent": ua.random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}
allowed_params = ["node", "rh", "page"]

# Proxies
proxies = [
    "84.54.8.191",
    "84.54.11.44",
    "84.54.8.35",
    "84.54.11.14",
    "5.182.118.190",
    "5.182.119.111",
    "5.182.119.202",
    "5.182.119.79",
    "45.90.199.222",
    "45.90.198.27",
]
proxy_user = "armen0788_gmail_com"
proxy_pass = "a472b6e950"
proxy_port = 30030

# Crawling Logic

start_file = os.path.join(current_dir, "start-urls.txt")
max_requests = 2 * 10 ** 6
max_details_per_listing = 100000

# Threads
max_threads = 7

# Logging & Storage

log_stdout = True
log_name = "crawl_log"
image_dir = "/tmp/crawl_images"
export_dir = "/tmp"
json_name = 'item_json.json'