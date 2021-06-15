from models import ProductRecord
from helpers import make_request, log, enqueue_url, dequeue_url
from extractors import get_title, get_url, get_price, get_primary_img
from datetime import datetime
import eventlet

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
                "div", "bxc-grid__container bxc-grid__container--width-1500"
            )

            for subcategory in subcategories:
                all_a = subcategory.find_all("a")
                for a_tag in all_a:
                    try:
                        link = a_tag["href"]
                        count += 1
                        enqueue_url(link)
                        break
                    except:
                        continue
            log("Found {} subcategories on {}".format(count, line))


def fetch_listing():
    global crawl_time
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
            product_price = get_price(item)
            product = ProductRecord(
                title=product_title,
                product_url=product_url,
                listing_url=url,
                price=product_price,
                primary_img=product_image,
                crawl_time=datetime.now(),
            )
            product_id = product.save()
            # download_image(product_image, product_id)

        # add next page to queue
        next_link = page.find("li", "a-last")
        next_page = next_link.find("a")
        new_link = next_page["href"]
        # if next_link:
        log(" Found 'Next' link on {}: {}".format(url, new_link))
        enqueue_url(new_link)
        a = pile.spawn(fetch_listing)
        print(a)
    except Exception as exp:
        log(exp)


if __name__ == "__main__":
    # if len(sys.argv) > 1 and sys.argv[1] == "start":
    log("Seeding the URL frontier with subcategory URLs")
    begin_crawl()  # put a bunch of subcategory URLs into the queue
    log("Beginning crawl at {}".format(crawl_time))
    [pile.spawn(fetch_listing) for _ in range(settings.max_threads)]
    pool.waitall()
