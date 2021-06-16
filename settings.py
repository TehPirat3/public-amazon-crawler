import os
from fake_useragent import UserAgent

current_dir = os.path.dirname(os.path.realpath(__file__))

# Database
database = "amazon_crawler"
host = "127.0.0.1"
user = "postgres"

# Redis
# redis_host = "redis-17095.c245.us-east-1-3.ec2.cloud.redislabs.com"
# redis_port = 17095
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
}


allowed_params = ["node", "rh", "page"]

# Proxies
proxies = [
    # your list of proxy IP addresses goes here
    # check out https://proxybonanza.com/?aff_id=629
    # for a quick, easy-to-use proxy service
    "196.17.78.233",
    "196.17.76.82",
    "196.17.77.68",
    "196.17.77.9",
    "196.17.76.116",
    "196.17.76.246",
    "196.17.79.174",
    "196.17.76.215",
]
proxy_user = "9cJQt1"
proxy_pass = "ted3mo"
proxy_port = "8000"

# Crawling Logic
start_file = os.path.join(current_dir, "start-urls.txt")
max_requests = 2 * 10 ** 6  # two million
max_details_per_listing = 100000

# Threads
max_threads = 8

# Logging & Storage
log_stdout = True
image_dir = "/tmp/crawl_images"
export_dir = "/tmp"
