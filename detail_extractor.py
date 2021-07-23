"""
Extracts details of product, creates json file and saves it to MongoDB document
"""

import json
import logging
import datetime
import sys


import helpers
import models_mongoDB
import settings

logging.basicConfig(filename=settings.log_name, filemode="a", level=logging.DEBUG)


def get_id(soup):
    try:
        id_code = soup.find("input", {"id": "all-offers-display-params"})["data-asin"]
    except Exception as exc:
        logging.exception(exc)
        id_code = None
    return id_code


def get_title(soup):
    try:
        title = soup.find("span", "a-size-large").text.strip()
    except Exception as exc:
        logging.exception(exc)
        title = None
    return {"title": title}


def get_features(soup):
    try:
        feature_section = soup.find("ul", "a-unordered-list a-vertical a-spacing-mini")
        details = [
            detail.text.strip
            for detail in feature_section.find_all("span", "a-list-item")
        ]
        features = ",".join(details)
    except Exception as exc:
        logging.exception(exc)
        features = None
    return {"features": features}


def get_color(soup):
    return {"color": get_item_specific(soup)["item_specific"].get("Color")}


def get_item_input_id(soup):
    try:
        item_input_id = get_id(soup)
    except Exception as exc:
        logging.exception(exc)
        item_input_id = None
    return {"item_input_id": item_input_id}


def get_attributes(soup):
    try:
        section = soup.find("div", {"id": "twister_feature_div"}).find_all(
            "div", "a-row"
        )
        attributes = dict()
        for types in section:
            label = types.find("label").text.strip().rstrip(":")
            name = types.find("span").text.strip()
            attributes[label] = name

    except Exception as exc:
        logging.exception(exc)
        attributes = None
    return {"attributes": attributes}


def get_item_specific(soup):
    try:
        keys = []
        values = []
        item_specifics = soup.find("table", "a-spacing-micro", "a-normal")
        for tr in item_specifics.find_all("tr"):
            keys.append(tr.find_all("td")[0].text.strip("\n"))
            values.append(tr.find_all("td")[1].text.strip("\n"))
        item_specific = dict(zip(keys, values))
    except Exception as exc:
        logging.exception(exc)
        item_specific = None
    return {"item_specific": item_specific}


def get_brand(soup):
    brand = get_item_specific(soup)["item_specific"].get("Brand")
    return {"brand": brand}


def get_images(soup):
    try:
        images = soup.find("div", {"id": "altImages"})
        links = [image["src"] for image in images.find_all("img", src=True)]
    except Exception as exc:
        logging.exception(exc)
        links = None
    return {"all_images": links}


def get_categories(soup):
    try:
        category_section = soup.find("ul", {"a-unordered-list"})
        count = 0
        categories = []
        for category in category_section.find_all(
            "a", "a-link-normal a-color-tertiary"
        ):
            temp_dict = dict()
            temp_dict["index"] = count
            temp_dict["name"] = category.text.replace("\n", "").strip()
            categories.append(temp_dict)
            count += 1
    except Exception as exc:
        logging.exception(exc)
        categories = None
    return {"categories": categories}


def get_category_id(soup):
    try:
        category_id = (
            soup.find("ul", {"a-unordered-list"})
            .find_all("a", "a-link-normal a-color-tertiary")[-1]["href"]
            .split("=")[-1]
        )
    except Exception as exc:
        logging.exception(exc)
        category_id = None
    return {"category_id": category_id}


def get_variations(soup):
    try:
        section = soup.find("div", {"id": "twister_feature_div"})
        var = section.find_all("div", {"class": "a-section"})
        variations = list()
        for variation in var[1:]:
            label = variation.find("label").text.strip().rstrip(":")
            names = [name.text.strip() for name in variation.find_all("p")]
            asins = [
                asin["data-defaultasin"]
                if asin["data-defaultasin"] != ""
                else asin["data-dp-url"].split("/")[2]
                for asin in variation.find_all("li")
            ]
            for data in zip(names, asins):
                temp_dict = dict()
                temp_dict["attributes"] = dict()
                temp_dict["attributes"][label] = data[0]
                temp_dict["item_input_id"] = data[1]
                variations.append(temp_dict)
    except Exception as exc:
        logging.exception(exc)
        variations = None
    return {"variations": variations}


def get_order_min_qty(soup):
    try:
        quantity = (
            soup.find("div", {"id": "selectQuantity"})
            .find("span", "a-dropdown-prompt")
            .text.strip()
        )
    except Exception as exc:
        logging.exception(exc)
        quantity = None
    return {"order_min_qty": quantity}


def get_shipping_message(soup):
    try:
        shipping_message = " ".join(
            soup.find("span", {"id": "upsell-message"}).text.replace("\n", " ").split()
        )
    except Exception as exc:
        logging.exception(exc)
        shipping_message = None
    return {"shipping_message": shipping_message}


def get_sold_by(soup):
    try:
        sold_by = soup.find("a", {"id": "sellerProfileTriggerId"}).text
    except Exception as exc:
        logging.exception(exc)
        sold_by = None
    return {"sold_by": sold_by}


def get_sold_by_seller_id(soup):
    try:
        sold_by_seller_id = soup.find(
            "input", {"id": "attach-preselected-merchant-id"}
        )["value"]
    except Exception as exc:
        logging.exception(exc)
        sold_by_seller_id = None
    return {"sold_by_seller_id": sold_by_seller_id}


def get_deal_of_the_day(soup):
    try:
        deals = soup.find("td", {"id": "priceblock_dealprice_lbl"}).text
        if deals.startswith("Deal of the Day"):
            deal_of_the_day = True
        else:
            deal_of_the_day = False
    except Exception as exc:
        logging.exception(exc)
        deal_of_the_day = False
    return {"deal_of_the_day": deal_of_the_day}


def get_shipping_price(soup):
    try:
        shipping_price_text = (
            soup.find("div", {"id": "mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE"})
            .find("span")
            .text.strip()
        )
        if shipping_price_text.startswith("FREE"):
            shipping_price = 0
        else:
            shipping_price = shipping_price_text
    except Exception as exc:
        logging.exception(exc)
        shipping_price = None
    return {"shipping_price": shipping_price}


def get_store_name(soup):
    try:
        store_name = soup.find("span", {"class": "tabular-buybox-text"}).text.strip()
    except Exception as exc:
        logging.exception(exc)
        store_name = None
    return {"store_name": store_name}


def get_manufacturer(soup):
    try:
        detail_label = [
            name.text.strip("\n")
            for name in soup.find("table", "prodDetTable").find_all("th")
        ]
        detail_value = [
            value.text.strip("\n")
            for value in soup.find("table", "prodDetTable").find_all("td")
        ]
        manufacturer = [
            item[1]
            for item in zip(detail_label, detail_value)
            if item[0] == "Manufacturer"
        ]
    except Exception as exc:
        logging.exception(exc)
        manufacturer = None
    return {"manufacturer": manufacturer}


def get_related_asins(soup):
    try:
        related_asins = soup.find("div", {"id": "sp_detail2"})
        related_asins = (
            related_asins["data-a-carousel-options"]
            .split("[")[1]
            .split("]")[0]
            .replace('"', "")
            .split(",")
        )
    except Exception as exc:
        logging.exception(exc)
        related_asins = None
    return {"related_asins": related_asins}


def get_price(soup):
    try:
        price = soup.find("span", "a-size-medium", "a-color-price").text.strip()
    except Exception as exc:
        logging.exception(exc)
        price = None
    return {"price": price}


def get_response_received():
    try:
        response_received = str(datetime.datetime.now())
    except Exception as exc:
        logging.exception(exc)
        response_received = None
    return {"response_received": response_received}


def get_before_deal_price(soup):
    try:
        before_deal_price = soup.find("span", "priceBlockStrikePriceString").text
    except Exception as exc:
        logging.exception(exc)
        before_deal_price = None
    return {"before_deal_price": before_deal_price}


def crawl_to_json(url):
    soup, html = helpers.make_request(url)
    proxy = helpers.proxy
    product_dict = dict()
    product_id = get_id(soup)
    if product_id is None:
        print("Retrying again...")
        sys.setrecursionlimit(40)
        return crawl_to_json(url)
    product_dict[product_id] = dict()
    time_now = datetime.datetime.now()
    product_dict[product_id].update(get_shipping_message(soup))
    product_dict[product_id].update(get_features(soup))
    product_dict[product_id].update(get_color(soup))
    product_dict[product_id].update(get_sold_by(soup))
    product_dict[product_id].update(get_item_input_id(soup))
    product_dict[product_id].update(get_attributes(soup))
    product_dict[product_id].update({"id": product_id})
    product_dict[product_id].update(get_shipping_price(soup))
    product_dict[product_id].update(get_title(soup))
    product_dict[product_id].update(get_sold_by_seller_id(soup))
    product_dict[product_id].update(get_related_asins(soup))
    product_dict[product_id].update(get_store_name(soup))
    product_dict[product_id].update(get_deal_of_the_day(soup))
    product_dict[product_id].update(get_item_specific(soup))
    product_dict[product_id].update(get_price(soup))
    product_dict[product_id].update(get_brand(soup))
    product_dict[product_id].update(get_response_received())
    product_dict[product_id].update({"proxy": proxy})
    product_dict[product_id].update(get_categories(soup))
    product_dict[product_id].update(get_manufacturer(soup))
    product_dict[product_id].update(get_images(soup))
    product_dict[product_id].update({"start_request": str(time_now)})
    product_dict[product_id].update(get_variations(soup))
    product_dict[product_id].update({"url": url})
    product_dict[product_id].update(get_before_deal_price(soup))
    product_dict[product_id].update(get_category_id(soup))
    product_dict[product_id].update(get_order_min_qty(soup))
    product_json = json.dumps(product_dict, indent=4)
    print(product_json)
    save_to_json(product_json)
    return product_json


def save_to_mongo(product_json):
    models_mongoDB.products.insert_one(json.loads(product_json))

def save_to_json(product_json):
    with open(settings.json_name, 'a') as file:
        file.write(product_json)


if __name__ == "__main__":
    item_code = input("Please input the product code: ").strip()
    amazon_url = f"https://www.amazon.com/dp/{item_code}"
    print("Starting the crawl...")
    data_json = crawl_to_json(amazon_url)
    print("Saving into database...")
    save_to_mongo(data_json)
    print("Saving to json file")
    save_to_json(data_json)
