from html.parser import HTMLParser

htmlparser = HTMLParser()


def get_title(item):
    title = item.find("h2", "a-size-mini a-spacing-none a-color-base s-line-clamp-4")
    if title:
        # return htmlparser.unescape(title.text.encode("utf-8"))
        return title.text
    else:
        return "<missing product title>"


def get_url(item):
    link = item.find("a", "a-link-normal s-no-outline")
    if link:
        print(link["href"])
        return link["href"]
    else:
        return "<missing product url>"


def get_price(item):
    price = item.find("span", "a-offscreen")
    if price:
        print(price.text)
        return price.text
    return None


def get_primary_img(item):
    thumb = item.find("img", "s-image")
    if thumb:
        src = thumb["src"]
        p1 = src.split("/")
        p2 = p1[-1].split(".")
        base = p2[0]
        ext = p2[-1]
        return "/".join(p1[:-1]) + "/" + base + "." + ext
    return None
