import logging
from decimal import Decimal
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import os

import aiohttp
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
from app.utils.retry_decorator import retry_async
from app.utils.image_downloader import download_image

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, proxy: Optional[str] = None, image_save_dir: str = "storage/images"):
        self.proxy = proxy
        self.image_save_dir = image_save_dir

    async def fetch_page(self, url: str) -> str:
        """Fetch the HTML content of a given URL."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, proxy=self.proxy, timeout=10) as response:
                    response.raise_for_status()
                    return await response.text()
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching page {url}: {str(e)}")
                raise NetworkException(f"Failed to fetch page: {str(e)}") from e

    async def parse_product(self, product_element: Tag, base_url: str) -> Optional[Product]:
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
            product_image_url = image_element.get('data-lazy-src', '') if image_element else ''
            product_image_url = urljoin(base_url, product_image_url)

            # Download the image and get the local path
            local_image_path = await download_image(product_image_url, self.image_save_dir)
            if not local_image_path:
                raise DataExtractionException(f"Failed to download image: {product_image_url}")

            # Ensure the source is a valid URL
            parsed_url = urlparse(TARGET_URL)
            source = f"{parsed_url.scheme}://{parsed_url.netloc}"

            return Product(
                id=f"{source}_{product_id}",
                source=source,
                source_id=product_id,
                product_title=product_title,
                product_price=product_price,
                path_to_image=local_image_path
            )
        except (AttributeError, ValueError, KeyError) as e:
            logger.warning(f"Error parsing product: {str(e)}")
            logger.warning(f"Product element: {product_element}")
            raise DataExtractionException(f"Failed to parse product: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error parsing product: {str(e)}")
            logger.error(f"Product element: {product_element}")
            raise DataExtractionException(f"Unexpected error parsing product: {str(e)}") from e

    @retry_async(max_attempts=3, delay=5)
    async def scrape_page(self, url: str) -> List[Product]:
        """Scrape a single page and return a list of Product objects."""
        try:
            html = await self.fetch_page(url)
            soup = BeautifulSoup(html, 'html.parser')
            product_elements = soup.find_all('li', class_='product')
            
            products = []
            for element in product_elements:
                try:
                    product = await self.parse_product(element, url)
                    if product:
                        products.append(product)
                except DataExtractionException as e:
                    logger.warning(f"Skipping product due to parsing error: {str(e)}")
            
            logger.info(f"Scraped {len(products)} products from {url}")
            return products
        except ParsingException as e:
            logger.error(f"Error parsing page {url}: {str(e)}")
            raise

    @retry_async(max_attempts=3, delay=5)
    async def scrape_catalog(self, page_limit: Optional[int] = None) -> List[Product]:
        """Scrape the entire catalog or up to the specified page limit."""
        url = TARGET_URL
        all_products: List[Product] = []
        page_count = 0

        while url and (page_limit is None or page_count < page_limit):
            try:
                logger.info(f"Scraping page {page_count + 1}: {url}")
                html = await self.fetch_page(url)
                products = await self.scrape_page(url)
                all_products.extend(products)
                
                url = self.get_next_page_url(url, html)
                page_count += 1
            except (NetworkException, ParsingException, PaginationException) as e:
                logger.error(f"Error scraping page {url}: {str(e)}")
                break

        logger.info(f"Scraped {len(all_products)} products from {page_count} pages")
        return all_products

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