import logging
from decimal import Decimal
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from app.constants import TARGET_URL
from app.exceptions.scraper_exceptions import (
    ScraperException,
    NetworkException,
    ParsingException,
    ProxyException,
    PaginationException,
    DataExtractionException
)
from app.models.product import Product

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, proxy: Optional[str] = None):
        self.session = requests.Session()
        if proxy:
            try:
                self.session.proxies = {"http": proxy, "https": proxy}
            except Exception as e:
                raise ProxyException(f"Failed to set proxy: {str(e)}") from e

    def fetch_page(self, url: str) -> str:
        """Fetch the HTML content of a given URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page {url}: {str(e)}")
            raise NetworkException(f"Failed to fetch page: {str(e)}") from e

    def parse_product(self, product_element: Tag) -> Optional[Product]:
        """Parse a product element and return a Product object."""
        try:
            product_id = product_element.find('a', class_='button')
            product_id = product_id.get('data-product_id', '') if product_id else ''

            title_element = product_element.find('h2', class_='woo-loop-product__title')
            product_title = title_element.a.text.strip() if title_element and title_element.a else ''

            price_element = product_element.find('span', class_='woocommerce-Price-amount')
            product_price = Decimal('0')
            if price_element:
                price_text = price_element.text.strip()
                price_value = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                product_price = Decimal(price_value) if price_value else Decimal('0')

            image_element = product_element.find('img', class_='attachment-woocommerce_thumbnail')
            product_image = image_element.get('data-lazy-src', '') if image_element else ''

            return Product.create(
                source=TARGET_URL,
                source_id=product_id,
                product_title=product_title,
                product_price=product_price,
                path_to_image=product_image
            )
        except (AttributeError, ValueError, KeyError) as e:
            logger.warning(f"Error parsing product: {str(e)}")
            raise DataExtractionException(f"Failed to parse product: {str(e)}") from e

    def scrape_page(self, url: str) -> List[Product]:
        """Scrape a single page and return a list of Product objects."""
        try:
            html = self.fetch_page(url)
            soup = BeautifulSoup(html, 'html.parser')
            product_elements = soup.find_all('li', class_='product')
            
            products = []
            for element in product_elements:
                try:
                    product = self.parse_product(element)
                    if product:
                        products.append(product)
                except DataExtractionException as e:
                    logger.warning(f"Skipping product due to parsing error: {str(e)}")
            
            logger.info(f"Scraped {len(products)} products from {url}")
            return products
        except ParsingException as e:
            logger.error(f"Error parsing page {url}: {str(e)}")
            raise

    def get_next_page_url(self, current_url: str, html: str) -> Optional[str]:
        """Get the URL of the next page, if it exists."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            next_page = soup.select_one('.next.page-numbers')
            if next_page and 'href' in next_page.attrs:
                return urljoin(current_url, next_page['href'])
            return None
        except Exception as e:
            raise PaginationException(f"Failed to get next page URL: {str(e)}") from e

    def scrape_catalog(self, page_limit: Optional[int] = None) -> List[Product]:
        """Scrape the entire catalog or up to the specified page limit."""
        url = TARGET_URL
        all_products: List[Product] = []
        page_count = 0

        while url and (page_limit is None or page_count < page_limit):
            try:
                logger.info(f"Scraping page {page_count + 1}: {url}")
                html = self.fetch_page(url)
                products = self.scrape_page(url)
                all_products.extend(products)
                
                url = self.get_next_page_url(url, html)
                page_count += 1
            except (NetworkException, ParsingException, PaginationException) as e:
                logger.error(f"Error scraping page {url}: {str(e)}")
                break

        logger.info(f"Scraped {len(all_products)} products from {page_count} pages")
        return all_products


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        scraper = Scraper()
        products = scraper.scrape_catalog(page_limit=5)
        
        logger.info(f"Total products scraped: {len(products)}")
        for product in products[:5]:  # Print details of first 5 products
            logger.info(f"Product ID: {product.id}")
            logger.info(f"Title: {product.product_title}")
            logger.info(f"Price: ${product.product_price}")
            logger.info(f"Image: {product.path_to_image}")
            logger.info("---")
    except ScraperException as e:
        logger.error(f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    main()
