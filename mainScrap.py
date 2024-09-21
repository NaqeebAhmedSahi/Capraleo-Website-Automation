import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import os
import time
import csv

# Define file paths
csv_file_path = 'product_data.csv'
log_file_path = 'scraped_links.txt'
image_folder = 'images'  # Folder to save downloaded images

# Ensure the image folder exists
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

def read_scraped_links():
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            return set(line.strip() for line in file)
    return set()

def log_scraped_link(link):
    with open(log_file_path, 'a') as file:
        file.write(link + '\n')

def download_image(image_url, image_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()
        with open(os.path.join(image_folder, image_name), 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return os.path.join(image_folder, image_name)
    except Exception as e:
        print(f"Failed to download image from {image_url}. Error: {e}")
        return 'N/A'


def scrape_product_data(driver, writer):
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract data using BeautifulSoup
        category = soup.find(class_='single-product-category')
        title = soup.find(class_='product_title entry-title')
        price_element = soup.find(class_='woocommerce-Price-amount')
        sku_wrapper = soup.find(class_='sku_wrapper')
        sku = soup.find(class_='sku')
        description_div = soup.find('div', id='tab-description')
        size = soup.find(class_='woocommerce-product-attributes-item__value')
        image_tag = soup.find('img', class_='wp-post-image')  # Extract image with this class

        # Extract text with default values if elements are not found
        category_text = category.get_text(strip=True) if category else 'N/A'
        title_text = title.get_text(strip=True) if title else 'N/A'
        
        if price_element:
            price_currency = price_element.find(class_='woocommerce-Price-currencySymbol').get_text(strip=True) if price_element.find(class_='woocommerce-Price-currencySymbol') else 'N/A'
            price_value = price_element.find('bdi').get_text(strip=True) if price_element.find('bdi') else 'N/A'
            price_text = f"{price_currency} {price_value}"
        else:
            price_text = 'N/A'
        
        sku_combined = f"{sku_wrapper.get_text(strip=True)} {sku.get_text(strip=True)}" if sku_wrapper and sku else 'N/A'
        description_text = description_div.find('p').get_text(strip=True) if description_div and description_div.find('p') else 'N/A'
        size_text = size.get_text(strip=True) if size else 'N/A'
        
        # Extract image URL and download the image
        if image_tag:
            image_url = image_tag['src']
            image_name = image_url.split('/')[-1]
            image_path = download_image(image_url, image_name)
        else:
            image_path = 'N/A'

        # Write the data to the CSV file
        writer.writerow([category_text, title_text, price_text, sku_combined, description_text, size_text, image_path])
        print(f"Data saved: Category: {category_text}, Title: {title_text}, Price: {price_text}, SKU Combined: {sku_combined}, Description: {description_text}, Size: {size_text}, Image: {image_path}")
        
    except Exception as e:
        print(f"Failed to scrape product data. Error: {e}")

try:
    with uc.Chrome() as driver:
        print("Driver initialized successfully.")

        driver.get("https://capraleo.com/product-category/general/dermatology/")
        print("Opened the webpage.")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "products.columns-4")))
        print("Products are fully loaded.")

        scraped_links = read_scraped_links()

        li_elements = driver.find_elements(By.CSS_SELECTOR, ".products.columns-4 li")
        product_links = [li.find_element(By.TAG_NAME, 'a').get_attribute('href') for li in li_elements if li.find_element(By.TAG_NAME, 'a')]

        if not product_links:
            print("No product links found.")
        else:
            print(f"Found {len(product_links)} product links.")

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Category', 'Title', 'Price', 'SKU Combined', 'Description', 'Size', 'Image Path'])

            for link in product_links:
                if link in scraped_links:
                    print(f"Link already scraped: {link}")
                    continue
                
                try:
                    print(f"Processing link: {link}")
                    driver.get(link)
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    print(f"Opened product page: {link}")
                    
                    scrape_product_data(driver, writer)
                    log_scraped_link(link)
                    
                    time.sleep(2)  # Adjust the sleep time as needed

                except Exception as e:
                    print(f"Failed to process link: {link}. Error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
