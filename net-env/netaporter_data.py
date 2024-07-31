import asyncio
import random
import csv
import requests
from bs4 import BeautifulSoup
import os
import sqlite3
import logging
import time
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed to disable the warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
USER_AGENTS_FILE = 'user_agents.txt'
CSV_FILE = '/data/netaporter_urls.csv'
CHECKPOINT_FILE = 'checkpoint.txt'
DB_FILE = '_data.db'
RETRY_ATTEMPTS = 3
proxies = {
  "https": "http://your_proxy:port"
}

headers_template = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
cookies = [
    {"name": "_gcl_au", "value": "1.1.550599228.1720606510", "domain": ".net-a-porter.com", "path": "/"},
    {"name": "_bamls_usid", "value": "0483e18a-fc07-42b6-8963-8436dbcf23fa", "domain": ".net-a-porter.com", "path": "/"},
    {"name": "rmStore", "value": "dmid:9361", "domain": ".net-a-porter.com", "path": "/"},
]

def fetch_html(url, headers, cookies):
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
    response = session.get(url, headers=headers, proxies=proxies, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        logging.error(f"Failed to load page content for: {url} with status code: {response.status_code}")
        return None

def create_tables(conn):
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS product_data (
                url TEXT PRIMARY KEY,
                category TEXT,
                product_name TEXT,
                stock_type TEXT,
                brand TEXT,
                price TEXT,
                discount TEXT,
                sale_price TEXT,
                color TEXT,
                description TEXT,
                size_and_fit TEXT,
                details_and_care TEXT,
                product_code TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS error_urls (
                url TEXT PRIMARY KEY,
                error TEXT
            )
        ''')

def random_delay():
    delay = random.uniform(20, 40)  # Random delay between 20 to 40 seconds
    print(f"Delaying for {delay:.2f} seconds")
    time.sleep(delay)

async def main():
    # Read user agents
    with open(USER_AGENTS_FILE, 'r') as f:
        user_agents = [line.strip() for line in f if line.strip()]

    # Read URLs and categories from CSV
    urls = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            urls.append((row[0], row[1]))  # Assuming URLs are in the first column and categories in the second column

    # Load checkpoint index if exists
    try:
        with open(CHECKPOINT_FILE, 'r') as cf:
            checkpoint_index = int(cf.read().strip())
    except FileNotFoundError:
        checkpoint_index = 0

    conn = sqlite3.connect(DB_FILE)
    create_tables(conn)

    for idx in range(checkpoint_index, len(urls)):
        url, category = urls[idx]
        random_user_agent = random.choice(user_agents)
        headers = {**headers_template, 'User-Agent': random_user_agent}

        for attempt in range(RETRY_ATTEMPTS):
            try:
                random_delay()
                html_content = fetch_html(url, headers, cookies)
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')

                    title_tag = soup.find('p', class_='ProductInformation87__name')
                    title = title_tag.string.strip() if title_tag else 'N/A'
                    stock_div = soup.find('div', class_='SingleBadge2__badge ProductDetails87__productColourBadge')
                    stock = stock_div.text.strip() if stock_div else 'N/A'
                    brand_tag = soup.find('div', class_='ProductInformation87 ProductDetails87__productInformation')
                    brand = brand_tag.find('span').text.strip() if brand_tag else 'N/A'
                    price_div = soup.find('div', class_='PriceWithSchema10 PriceWithSchema10--sale PriceWithSchema10--details ProductDetails87__price')
                    if price_div:
                        price = price_div.find('s', class_='PriceWithSchema10__wasPrice').text.strip()
                        discount = price_div.find('div', class_='PriceWithSchema10__discount PriceWithSchema10__discount--sale PriceWithSchema10__discount--details').text.strip()
                        sale_price = price_div.find('span').text.strip()
                    else:
                        price_div2 = soup.find('div', class_='PriceWithSchema10 PriceWithSchema10--details ProductDetails87__price')
                        if price_div2:
                            price = price_div2.find('span').text.strip()
                            discount = '0'
                            sale_price = price
                        else:
                            price = 'N/A'
                            discount = 'N/A'
                            sale_price = 'N/A'
                    color_div = soup.find('div', class_='ProductDetailsColours87 ProductDetails87__colours')
                    color = color_div.find('span').text.strip() if color_div else 'N/A'
                    des_div = soup.find('div', class_='AccordionSection3', id='EDITORS_NOTES')
                    description = des_div.find('p').text.strip() if des_div else 'N/A'
                    size_div = soup.find('div', class_='AccordionSection3', id='SIZE_AND_FIT')
                    if size_div:
                        texts = [text.strip() for text in size_div.find_all(string=True, recursive=True) if text.strip()]
                        size_fit = "\n".join(texts)
                    else:
                        size_fit = 'N/A'
                    div_tag = soup.find('div', class_='AccordionSection3', id='DETAILS_AND_CARE')
                    if div_tag:
                        details_li = div_tag.find_all('li')
                        details_care = "\n".join([li.get_text(strip=True) for li in details_li])
                    else:
                        details_care = 'N/A'
                    code_div = soup.find("div", class_='PartNumber87 ProductDetails87__partNumber')
                    code = code_div.find('span', class_='PartNumber87__number').text.strip() if code_div else 'N/A'

                    with conn:
                        conn.execute('''
                            INSERT OR REPLACE INTO product_data (
                                url, category, product_name, stock_type, brand, price,
                                discount, sale_price, color, description, size_and_fit,
                                details_and_care, product_code
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (url, category, title, stock, brand, price, discount, sale_price, color, description, size_fit, details_care, code))

                    logging.info(f"Scraped product: {title}")
                    break  # Break out of retry loop if successful
                else:
                    raise ValueError(f"Failed to fetch HTML content for: {url}")

            except Exception as e:
                logging.error(f"Error scraping {url} on attempt {attempt + 1}: {e}")
                if attempt == RETRY_ATTEMPTS - 1:
                    with conn:
                        conn.execute('INSERT OR REPLACE INTO error_urls (url, error) VALUES (?, ?)', (url, str(e)))

        with open(CHECKPOINT_FILE, 'w') as cf:
            cf.write(str(idx + 1))

    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
