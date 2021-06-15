from models import ProductRecord
from helpers import make_request, log, format_url, enqueue_url, dequeue_url
from extractors import get_title, get_url, get_price, get_primary_img
from datetime import datetime
import eventlet
requests = eventlet.import_patched('requests.__init__')
time = eventlet.import_patched('time')
import settings
crawl_time = datetime.now()
pool = eventlet.GreenPool(settings.max_threads)
pile = eventlet.GreenPile(pool)
def begin_crawl():
    # explode out all of our category start_urls into subcategories
    with open(settings.start_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip blank and commented out lines
            page, html = make_request(line)
            count = 0
            subcategories = page.findAll("a", "a-link-normal acs_tile__title-image aok-block a-text-normal")  # downward arrow graphics
            a = 0
            for subcategory in subcategories:
                # if a==2:
                #     i = subcategory.find_all("a")
                #     b = 0
                #     for link in i:
                #         if not link:
                #             continue
                #         print("====",b,link["href"])
                #
                #         link = link["href"]
                #         count += 1
                #         b += 1
                link = subcategory["href"]
                # print(f'https://www.amazon.com{link}')
                enqueue_url(link)
                a += 1
            log("Found {} subcategories on {}".format(count, line))
k = 0
def fetch_listing():
    global k
    global crawl_time
    crawl_time = datetime.now()
    url = dequeue_url()
    # print(k,url)
    k +=1
    if not url:
        log("WARNING: No URLs found in the queue. Retrying...")
        pile.spawn(fetch_listing)
        return
    try:
        page, html = make_request(url)
        # print("mtav")
        item_list = page.find("div", "s-main-slot s-result-list s-search-results sg-row")
        items = item_list.find_all("div","sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col sg-col-4-of-20")
        log("Found {} items on {}".format(len(items), url))
        for item in items[:settings.max_details_per_listing]:
            product_image = get_primary_img(item)
            if not product_image:
                log("No product image detected, skipping")
                continue
            product_title = get_title(item)
            product_url = get_url(item)
            product_price = get_price(item)
            # print("+=========++++++++++++++++++++++++++++++++++++++++++++++++++a")
            product = ProductRecord(
                title=product_title,
                product_url=product_url,
                listing_url=url,
                price=product_price,
                primary_img=product_image,
                crawl_time=crawl_time
            )
            # print(product.__dict__)
            product_id = product.save()
        # add next page to queue
        next_link_1 = page.find("li", "a-last")
        next_link = next_link_1.find('a')
        # print("==============++++++++++++++++++++++=",next_link["href"])
        if next_link:
            log(" Found 'Next' link on {}: {}".format(url, next_link["href"]))
            enqueue_url(next_link["href"])
            pile.spawn(fetch_listing)
    except Exception:
        # print(Exception)
        pass
if __name__ == '__main__':
    # if len(sys.argv) > 1 and sys.argv[1] == "start":
    log("Seeding the URL frontier with subcategory URLs")
    begin_crawl()  # put a bunch of subcategory URLs into the queue
    log("Beginning crawl at {}".format(crawl_time))
    [pile.spawn(fetch_listing) for _ in range(settings.max_threads)]
    pool.waitall()