"""
Crawls category's subcategories, extracts item urls and info from browsing page
"""

from models import ProductRecord
from helpers import make_request, log, enqueue_url, dequeue_url
from extractors import get_title, get_url, get_price, get_primary_img
from datetime import datetime
import eventlet
import bitlyshortener
from detail_extractor import crawl_to_json, save_to_mongo

requests = eventlet.import_patched("requests.__init__")
time = eventlet.import_patched("time")
import settings

crawl_time = datetime.now()
pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)


def begin_crawl():
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            page, html = make_request(line)
            count = 0
            subcategories = page.findAll(
                "a", "a-link-normal acs_tile__title-image aok-block a-text-normal"
            )
            for subcategory in subcategories:
                link = subcategory["href"]
                enqueue_url(link)
            log("Found {} subcategories on {}".format(count, line))


def fetch_listing():
    global crawl_time
    crawl_time = datetime.now()
    url = dequeue_url()
    if not url:
        log("WARNING: No URLs found in the queue. Retrying...")
        pile.spawn(fetch_listing)
        return
    try:
        page, html = make_request(url)
        item_list = page.find(
            "div", "s-main-slot s-result-list s-search-results sg-row"
        )
        items = item_list.find_all(
            "div",
            "sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20",
        )
        log("Found {} items on {}".format(len(items), url))
        for item in items[: settings.max_details_per_listing]:
            product_image = get_primary_img(item)
            if not product_image:
                log("No product image detected, skipping")
                continue
            product_title = get_title(item)
            product_url = get_url(item)
            save_to_mongo(crawl_to_json(f"https://www.amazon.com/{product_url}"))
            product_price = get_price(item)
            product = ProductRecord(
                title=product_title,
                product_url=product_url,
                listing_url=url,
                price=product_price,
                primary_img=product_image,
                crawl_time=crawl_time,
            )
            product_id = product.save()
        next_link_1 = page.find("li", "a-last")
        next_link = next_link_1.find("a")
        if next_link:
            log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
            enqueue_url(next_link["href"])
            pile.spawn(fetch_listing)
    except Exception as i:
        print(i)
        tokens_pool = ["35a1b66395e8cbed2d701d42c640c087456fbb8b"]
        shortener = bitlyshortener.Shortener(tokens=tokens_pool, max_cache_size=256)
        long_urls = url
        url = shortener.shorten_urls([long_urls])[0]
        enqueue_url(url)
        pile.spawn(fetch_listing)


if __name__ == "__main__":
    log("Seeding the URL frontier with subcategory URLs")
    begin_crawl()
    log("Beginning crawl at {}".format(crawl_time))
    [pile.spawn(fetch_listing) for _ in range(settings.max_threads)]
    pool.waitall()
