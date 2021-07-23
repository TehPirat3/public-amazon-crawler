import logging


import settings


logging.basicConfig(filename=settings.log_name, filemode="a", level=logging.DEBUG)


def get_title(item):
    try:
        title = item.find(
            "h2", "a-size-mini a-spacing-none a-color-base s-line-clamp-4"
        )
        if title:
            return title.text
        else:
            return "<missing product title>"
    except Exception as exc:
        logging.exception(exc)


def get_url(item):
    try:
        link = item.find("a", "a-link-normal s-no-outline")
        if link:
            return link["href"]
        else:
            return "<missing product url>"
    except Exception as exc:
        logging.exception(exc)


def get_price(item):
    try:
        price = item.find("span", "a-offscreen")
        if price:
            return price.text
        return "Nan="
    except Exception as exc:
        logging.exception(exc)


def get_primary_img(item):
    try:
        thumb = item.find("img", "s-image")
        if thumb:
            src = thumb["src"]
            p1 = src.split("/")
            p2 = p1[-1].split(".")
            base = p2[0]
            ext = p2[-1]
            return "/".join(p1[:-1]) + "/" + base + "." + ext
        return "Non"
    except Exception as exc:
        logging.exception(exc)
