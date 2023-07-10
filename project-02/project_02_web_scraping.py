# Import Libraries

import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import logging
from sqlalchemy import create_engine
import time


def web_scraping():
    """
    This fucntion will crawl web content, return a dataframe contain information and 
    create a log for not found information
    Input:
    Output: df
    """
    ls_item_id = []
    ls_title = []
    ls_brand = []
    ls_rating = []
    ls_number_of_rating = []
    ls_price_current = []
    ls_shipping = []
    ls_image_url = []
    ls_details = []

    logging.basicConfig(filename='log_web_scraping.log', filemode= 'w')

    for i in range(1, 101):
        if i == 1:
            url = "https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48"
        else:
            url = "https://www.newegg.com/GPUs-Video-Graphics-Cards/SubCategory/ID-48/Page-" + \
                str(i)

        # Fetching content of one page
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Filter items cell
        items = soup.findAll(
            'div', attrs={'class': re.compile('item-container')})

        # Extract information
        for item in items:

            # Get item_id
            try:
                item_id = item['id']
                ls_item_id.append(item_id)
            except Exception as e:
                logging.warning(e)
                item_id = None
                continue

            # Get title
            try:
                title = item.find('a').find('img')['title']
                ls_title.append(title)
            except Exception as e:
                logging.warning(e)
                title = None
                ls_title.append(title)

            # Get branding
            try:
                brand = item.find('a', attrs={'class': re.compile(
                    'item-brand')}).find('img')['title']
                ls_brand.append(brand)
            except Exception as e:
                logging.warning(e)
                brand = None
                ls_brand.append(brand)

            # Get rating
            try:
                rating = item.find('i', attrs={'class': re.compile("rating")})[
                    'aria-label'].split()[1]
                ls_rating.append(rating)
            except Exception as e:
                logging.warning(e)
                rating = None
                ls_rating.append(rating)

            # Get number of rating
            try:
                number_of_rating = item.find(
                    "span", attrs={'class': 'item-rating-num'}).string.strip("()")
                ls_number_of_rating.append(number_of_rating)
            except Exception as e:
                logging.warning(e)
                number_of_rating = 0
                ls_number_of_rating.append(number_of_rating)

            # Get price current and convert to number
            try:
                price_current = item.find('li', attrs={'class': 'price-current'}).find(['strong']).string + \
                    items[0].find(
                        'li', attrs={'class': 'price-current'}).find(['sup']).string

                price_current = float(price_current.replace(',', ''))

                ls_price_current.append(price_current)

            except Exception as e: 
                logging.warning(e)
                price_current = 0
                ls_price_current.append(price_current)

            # Get Shipping
            try:
                shipping = item.find(
                    'li', attrs={'class': 'price-ship'}).string
                ls_shipping.append(shipping)
            except Exception as e:
                logging.warning(e)
                shipping = None
                ls_shipping.append(shipping)

            # Get image URL
            try:
                image_url = item.find('img')['src']
                ls_image_url.append(image_url)
            except Exception as e:
                logging.warning(e)
                image_url = None
                ls_image_url.append(image_url)

            # Get details of product
            dict_details = {}

            try:
                for d in item.findAll('li'):
                    if d.text.startswith('Max Resolution'):
                        dict_details["Max_Resolution"] = d.text.split(":")[1]
                    elif d.text.startswith('DisplayPort'):
                        dict_details["Display_Port"] = d.text.split(":")[1]
                    elif d.text.startswith('HDMI'):
                        dict_details["HDMI"] = d.text.split(":")[1]
                    elif d.text.startswith('DirectX'):
                        dict_details["DirectX"] = d.text.split(":")[1]
                    elif d.text.startswith('Model'):
                        dict_details["Model"] = d.text.split(":")[1]
                    else:
                        continue
            except Exception as e:
                logging.warning(e)

            ls_details.append(dict_details)

    # Create dataframe from lists

    df = pd.DataFrame(list(zip(ls_item_id, ls_title, ls_brand, ls_rating, ls_number_of_rating,
                           ls_price_current, ls_shipping, ls_image_url, ls_details)),
                      columns=['item_id', 'title', 'brand', 'rating', 'number_of_rating', 'price_current', 'shipping',
                               'image_url', 'details'])
    
    # Drop rows duplicated by item_id
    df.drop_duplicates(subset=['item_id'], keep='first', inplace=True)

    # Convert columns details to str
    df["details"] = df["details"].astype('str')

    # Calculate price shipping
    df['price_shipping'] = df['shipping'].apply(lambda x: float(x.rstrip(" Shipping").lstrip("$"))
                                                if x != 'Free Shipping' and x != 'Special Shipping' else 0)
    # Create total price
    df['total_price'] = df['price_current'] + df['price_shipping']

    # Drop columns price shipping
    df.drop(columns='price_shipping', inplace=True)

    return df


if __name__ == "__main__":

    start = time.time()

    df = web_scraping()

    # Describe dataframe
    print('Number of records: ', len(df))

    # Credentials to database connection
    hostname = "localhost"
    dbname = "db_project2"
    uname = "tanlee"
    pwd = "17012021*Th"

    # Create SQLAlchemy engine to connect to MySQL Database

    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                           .format(host=hostname, db=dbname, user=uname, pw=pwd))

    # Write dataframe to mysql database

    df.to_sql(name='products', if_exists='replace', con=engine, index=False)

    end = time.time()

    print("The time of execution is :",
      (end-start), "s")