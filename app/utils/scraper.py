import logging
import os
import ssl
from decimal import Decimal
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup, Tag

from app.constants import (
    IMAGE_SAVE_DIR,
    MAX_RETRY_ATTEMPTS,
    NEXT_PAGE_CLASS,
    PRODUCT_CLASS,
    PRODUCT_IMAGE_CLASS,
    PRODUCT_PRICE_CLASS,
    PRODUCT_TITLE_CLASS,
    RETRY_DELAY,
    TARGET_URL,
)
from app.exceptions.scraper_exceptions import (
    DataExtractionException,
    NetworkException,
    PaginationException,
    ParsingException,
    ProxyException,
    ScraperException,
)
from app.models.product import Product
from app.utils.image_downloader import download_image
from app.utils.retry_decorator import retry_async

logger = logging.getLogger(__name__)

class Scraper:
    """
    A class for scraping product information from a website.

    Attributes:
        proxy (Optional[str]): The proxy server to use for requests.
        image_save_dir (str): The directory to save downloaded images.
        ssl_context (ssl.SSLContext): A custom SSL context for requests.
    """

    def __init__(self, proxy: Optional[str] = None, image_save_dir: str = IMAGE_SAVE_DIR):
        """
        Initialize the Scraper.

        Args:
            proxy (Optional[str]): The proxy server to use for requests.
            image_save_dir (str): The directory to save downloaded images.
        """
        self.proxy = proxy
        self.image_save_dir = image_save_dir
        self.ssl_context = self._create_ssl_context()
        logger.info(f"Scraper initialized with proxy: {proxy}, image_save_dir: {image_save_dir}")

    @staticmethod
    def _create_ssl_context() -> ssl.SSLContext:
        """
        Create a custom SSL context that doesn't verify certificates.

        Returns:
            ssl.SSLContext: The custom SSL context.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    async def fetch_page(self, url: str) -> str:
        """
        Fetch the HTML content of a given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The HTML content of the page.

        Raises:
            NetworkException: If there's an error fetching the page.
        """
        logger.info(f"Fetching page: {url}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, proxy=self.proxy, timeout=10, ssl=self.ssl_context) as response:
                    response.raise_for_status()
                    content = await response.text()
                    logger.info(f"Successfully fetched page: {url}")
                    return content
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching page {url}: {str(e)}")
                raise NetworkException(f"Failed to fetch page: {str(e)}") from e

    async def parse_product(self, product_element: Tag, base_url: str) -> Optional[Product]:
        """
        Parse a product element and return a Product object.

        Args:
            product_element (Tag): The BeautifulSoup Tag containing product information.
            base_url (str): The base URL of the page.

        Returns:
            Optional[Product]: A Product object if parsing is successful, None otherwise.

        Raises:
            DataExtractionException: If there's an error parsing the product.
        """
        try:
            product_id = self._extract_product_id(product_element)
            product_title = self._extract_product_title(product_element)
            product_price = self._extract_product_price(product_element)
            product_image_url = self._extract_product_image_url(product_element, base_url)

            local_image_path = await download_image(product_image_url, self.image_save_dir)
            if not local_image_path:
                raise DataExtractionException(f"Failed to download image: {product_image_url}")

            source = self._get_source_url()

            logger.info(f"Parsed product: {product_id}, {product_title}, {product_price}, {local_image_path}")
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

    @staticmethod
    def _extract_product_id(product_element: Tag) -> str:
        """Extract the product ID from the product element."""
        product_id_element = product_element.find('a', class_='button')
        return product_id_element.get('data-product_id', '') if product_id_element else ''

    @staticmethod
    def _extract_product_title(product_element: Tag) -> str:
        """Extract the product title from the product element."""
        title_element = product_element.find('h2', class_=PRODUCT_TITLE_CLASS)
        return title_element.a.text.strip() if title_element and title_element.a else ''

    @staticmethod
    def _extract_product_price(product_element: Tag) -> Decimal:
        """Extract the product price from the product element."""
        price_element = product_element.find('span', class_=PRODUCT_PRICE_CLASS)
        if price_element:
            price_text = price_element.text.strip()
            price_value = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
            return Decimal(price_value) if price_value else Decimal('0')
        return Decimal('0')

    @staticmethod
    def _extract_product_image_url(product_element: Tag, base_url: str) -> str:
        """Extract the product image URL from the product element."""
        image_element = product_element.find('img', class_=PRODUCT_IMAGE_CLASS)
        image_url = image_element.get('data-lazy-src', '') if image_element else ''
        return urljoin(base_url, image_url)

    @staticmethod
    def _get_source_url() -> str:
        """Get the source URL from the TARGET_URL constant."""
        parsed_url = urlparse(TARGET_URL)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    @retry_async(max_attempts=MAX_RETRY_ATTEMPTS, delay=RETRY_DELAY)
    async def scrape_page(self, url: str) -> List[Product]:
        """
        Scrape a single page and return a list of Product objects.

        Args:
            url (str): The URL of the page to scrape.

        Returns:
            List[Product]: A list of Product objects scraped from the page.

        Raises:
            ParsingException: If there's an error parsing the page.
        """
        try:
            html = await self.fetch_page(url)
            soup = BeautifulSoup(html, 'html.parser')
            product_elements = soup.find_all('li', class_=PRODUCT_CLASS)

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

    @retry_async(max_attempts=MAX_RETRY_ATTEMPTS, delay=RETRY_DELAY)
    async def scrape_catalog(self, page_limit: Optional[int] = None) -> List[Product]:
        """
        Scrape the entire catalog or up to the specified page limit.

        Args:
            page_limit (Optional[int]): The maximum number of pages to scrape.

        Returns:
            List[Product]: A list of all Product objects scraped from the catalog.
        """
        url = TARGET_URL
        all_products: List[Product] = []
        page_count = 0

        logger.info(f"Starting catalog scrape with page_limit: {page_limit}")
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
        """
        Get the URL of the next page, if it exists.

        Args:
            current_url (str): The URL of the current page.
            html (str): The HTML content of the current page.

        Returns:
            Optional[str]: The URL of the next page, or None if there is no next page.

        Raises:
            PaginationException: If there's an error getting the next page URL.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            next_page = soup.select_one(f'.{NEXT_PAGE_CLASS}')
            if next_page and 'href' in next_page.attrs:
                next_url = urljoin(current_url, next_page['href'])
                logger.info(f"Found next page URL: {next_url}")
                return next_url
            logger.info("No next page found")
            return None
        except Exception as e:
            logger.error(f"Error getting next page URL: {str(e)}")
            raise PaginationException(f"Failed to get next page URL: {str(e)}") from e
