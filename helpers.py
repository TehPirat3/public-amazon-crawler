import os
import random
from datetime import datetime
import eventlet

requests = eventlet.import_patched("requests.__init__")
time = eventlet.import_patched("time")
import redis
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import settings

num_requests = 0
use = 0
redis = redis.StrictRedis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
)

proxy = ""


def make_request(url, return_soup=True):

    global num_requests
    if num_requests >= settings.max_requests:
        raise Exception(
            "Reached the max number of requests: {}".format(settings.max_requests)
        )
    proxies = get_proxy()
    global proxy
    proxy = proxies
    try:
        request_page = requests.get(url, headers=settings.hdr, proxies=proxies)
    except RequestException:
        log("WARNING: Request for {} failed, trying again.".format(url))
        return make_request(url)
    num_requests += 1
    if request_page.status_code != 200:
        os.system('say "Got non-200 Response"')
        log("WARNING: Got a {} status code for URL: {}".format(request_page.status_code, url))
        return None
    if return_soup:
        return BeautifulSoup(request_page.text, "html.parser"), request_page.text

    return request_page


def log(msg):
    if settings.log_stdout:
        try:
            print("{}: {}".format(datetime.now(), msg))
        except UnicodeEncodeError:
            pass


def get_proxy():
    if not settings.proxies or len(settings.proxies) == 0:
        return None
    proxy_ip = random.choice(settings.proxies)
    proxy_url = "https://{user}:{passwd}@{ip}:{port}/".format(
        user=settings.proxy_user,
        passwd=settings.proxy_pass,
        ip=proxy_ip,
        port=settings.proxy_port,
    )
    return {"http": proxy_url, "https": proxy_url}


def enqueue_url(u):
    return redis.sadd("listing_url_queue", u)


def dequeue_url():
    link = redis.spop("listing_url_queue")
    if str(link).startswith("https"):
        url = str(link)
    else:
        url = link.decode("ascii")
        if url.startswith("https://amzn.to"):
            pass
        else:
            url = f" https://www.amazon.com{url}"
    return url


if __name__ == "__main__":
    request = make_request("https://api.ipify.org?format=json", return_soup=False)
    print(request.text)
