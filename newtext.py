import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def test_pagination(link):
    """Test pagination functionality for a given link."""
    try:
        # Initialize the Chrome driver
        with uc.Chrome() as driver:
            print(f"Opening link: {link}")

            # Initialize page number
            page_number = 1

            while True:
                # Construct the URL for the current page
                page_url = f"{link}/page/{page_number}/"
                driver.get(page_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "products.columns-4")))

                # Find all product links on the current page
                li_elements = driver.find_elements(By.CSS_SELECTOR, ".products.columns-4 li")
                product_links = [li.find_element(By.TAG_NAME, 'a').get_attribute('href') for li in li_elements if li.find_element(By.TAG_NAME, 'a')]

                if not product_links:
                    print(f"No product links found on page {page_number}.")
                    break  # Exit loop if no products are found on this page
                else:
                    print(f"Found {len(product_links)} product links on page {page_number}.")

                # Check if there's a next page
                try:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    next_page = soup.find('a', class_='next page-numbers')
                    if not next_page:
                        print(f"No more pages found. Ending pagination check.")
                        break  # Exit loop if no more pages are found
                    else:
                        print(f"Moving to next page: {page_number + 1}")
                        page_number += 1
                except Exception as e:
                    print(f"Error checking for additional pages: {e}")
                    break  # Exit loop if there's an error checking for next page

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_link = "https://capraleo.com/product-category/general"
    test_pagination(test_link)
