import json
import os
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from app.constants import (
    NEXT_PAGE_CLASS,
    PRODUCT_CLASS,
    PRODUCT_IMAGE_CLASS,
    PRODUCT_PRICE_CLASS,
    PRODUCT_TITLE_CLASS,
    TARGET_URL,
)
from app.exceptions.scraper_exceptions import DataExtractionException, NetworkException
from app.models.product import Product
from app.utils.scraper import Scraper


@pytest.fixture
def scraper():
    return Scraper()

@pytest.fixture
def sample_products():
    with open('products.json', 'r') as f:
        return json.load(f)

@pytest.mark.asyncio
@pytest.mark.parametrize("status_code,expected_exception", [
    (404, NetworkException),
    (500, NetworkException),
    (200, None)
])
async def test_fetch_page_status_codes(scraper, status_code, expected_exception):
    test_url = "http://test.com"

    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = status_code
        mock_response.text.return_value = "<html></html>"
        mock_get.return_value.__aenter__.return_value = mock_response

        if expected_exception:
            with pytest.raises(expected_exception):
                await scraper.fetch_page(test_url)
        else:
            content = await scraper.fetch_page(test_url)
            assert content == "<html></html>"

@pytest.mark.asyncio
async def test_fetch_page_network_error(scraper):
    test_url = "http://test.com"
    error_message = "Network error"

    with patch('aiohttp.ClientSession.get', side_effect=Exception(error_message)):
        with pytest.raises(NetworkException) as exc_info:
            await scraper.fetch_page(test_url)

        assert str(exc_info.value) == f"Failed to fetch page: {error_message}"

@pytest.mark.asyncio
async def test_parse_product(scraper):
    test_url = "http://test.com"
    product_id = "123"
    product_title = "Test Product"
    product_price = "10.99"
    image_url = "http://test.com/image.jpg"
    image_path = "/path/to/image.jpg"

    html = f"""
    <li class="{PRODUCT_CLASS}">
        <a class="button" data-product_id="{product_id}"></a>
        <h2 class="{PRODUCT_TITLE_CLASS}"><a>{product_title}</a></h2>
        <span class="{PRODUCT_PRICE_CLASS}">{product_price}</span>
        <img class="{PRODUCT_IMAGE_CLASS}" data-lazy-src="{image_url}">
    </li>
    """
    product_element = BeautifulSoup(html, 'html.parser').find('li', class_=PRODUCT_CLASS)

    with patch('app.utils.image_downloader.download_image', return_value=image_path):
        with patch('app.utils.scraper.TARGET_URL', 'http://test.com'):
            with patch('os.path.exists', return_value=True):
                product = await scraper.parse_product(product_element, test_url)

    assert isinstance(product, Product)
    assert product.source_id == product_id
    assert product.product_title == product_title
    assert product.product_price == float(product_price)
    assert product.path_to_image == image_path

@pytest.mark.asyncio
async def test_parse_product_error(scraper):
    test_url = "http://test.com"
    html = f"<li class='{PRODUCT_CLASS}'></li>"
    product_element = BeautifulSoup(html, 'html.parser').find('li', class_=PRODUCT_CLASS)

    with pytest.raises(DataExtractionException) as exc_info:
        await scraper.parse_product(product_element, test_url)

    assert "Failed to parse product" in str(exc_info.value)

@pytest.mark.asyncio
async def test_parse_product_missing_elements(scraper):
    test_url = "http://test.com"
    html = f"<li class='{PRODUCT_CLASS}'></li>"
    product_element = BeautifulSoup(html, 'html.parser').find('li', class_=PRODUCT_CLASS)

    with pytest.raises(DataExtractionException):
        await scraper.parse_product(product_element, test_url)

@pytest.mark.asyncio
async def test_scrape_catalog_pagination(scraper):
    with patch.object(scraper, 'fetch_page') as mock_fetch_page, \
         patch.object(scraper, 'scrape_page') as mock_scrape_page, \
         patch.object(scraper, 'get_next_page_url') as mock_get_next_page_url:

        mock_fetch_page.return_value = "<html></html>"
        mock_scrape_page.side_effect = [
            [Product(id="1", source="test.com", source_id="1", product_title="Product 1", product_price=10.0, path_to_image="/img1.jpg")],
            [Product(id="2", source="test.com", source_id="2", product_title="Product 2", product_price=20.0, path_to_image="/img2.jpg")],
            []
        ]
        mock_get_next_page_url.side_effect = ["http://test.com/page2", "http://test.com/page3", None]

        with patch('os.path.exists', return_value=True):
            products = await scraper.scrape_catalog(page_limit=None)

        assert len(products) == 2
        assert mock_fetch_page.call_count == 3
        assert mock_scrape_page.call_count == 3
        assert mock_get_next_page_url.call_count == 3

@pytest.mark.asyncio
async def test_scrape_catalog_with_page_limit(scraper):
    with patch.object(scraper, 'fetch_page') as mock_fetch_page, \
         patch.object(scraper, 'scrape_page') as mock_scrape_page, \
         patch.object(scraper, 'get_next_page_url') as mock_get_next_page_url:

        mock_fetch_page.return_value = "<html></html>"
        mock_scrape_page.side_effect = [
            [Product(id="1", source="test.com", source_id="1", product_title="Product 1", product_price=10.0, path_to_image="/img1.jpg")],
            [Product(id="2", source="test.com", source_id="2", product_title="Product 2", product_price=20.0, path_to_image="/img2.jpg")],
            [Product(id="3", source="test.com", source_id="3", product_title="Product 3", product_price=30.0, path_to_image="/img3.jpg")]
        ]
        mock_get_next_page_url.side_effect = ["http://test.com/page2", "http://test.com/page3", None]

        with patch('os.path.exists', return_value=True):
            products = await scraper.scrape_catalog(page_limit=2)

        assert len(products) == 2
        assert mock_fetch_page.call_count == 2
        assert mock_scrape_page.call_count == 2
        assert mock_get_next_page_url.call_count == 2

@pytest.mark.asyncio
async def test_scrape_catalog_empty_page(scraper):
    with patch.object(scraper, 'fetch_page') as mock_fetch_page, \
         patch.object(scraper, 'scrape_page') as mock_scrape_page, \
         patch.object(scraper, 'get_next_page_url') as mock_get_next_page_url:

        mock_fetch_page.return_value = "<html></html>"
        mock_scrape_page.return_value = []
        mock_get_next_page_url.return_value = None

        products = await scraper.scrape_catalog()

        assert len(products) == 0
        assert mock_fetch_page.call_count == 1
        assert mock_scrape_page.call_count == 1
        assert mock_get_next_page_url.call_count == 1

@pytest.mark.asyncio
async def test_parse_product_with_special_characters(scraper):
    test_url = "http://test.com"
    product_id = "123"
    product_title = "3M ESPE Adper™ Scotchbond™ Multi-Purpose Adhesive"
    product_price = "1,195.00"
    image_url = "http://test.com/image.jpg"
    image_path = "/path/to/image.jpg"

    html = f"""
    <li class="{PRODUCT_CLASS}">
        <a class="button" data-product_id="{product_id}"></a>
        <h2 class="{PRODUCT_TITLE_CLASS}"><a>{product_title}</a></h2>
        <span class="{PRODUCT_PRICE_CLASS}">{product_price}</span>
        <img class="{PRODUCT_IMAGE_CLASS}" data-lazy-src="{image_url}">
    </li>
    """
    product_element = BeautifulSoup(html, 'html.parser').find('li', class_=PRODUCT_CLASS)

    with patch('app.utils.image_downloader.download_image', return_value=image_path):
        with patch('app.utils.scraper.TARGET_URL', 'http://test.com'):
            with patch('os.path.exists', return_value=True):
                product = await scraper.parse_product(product_element, test_url)

    assert isinstance(product, Product)
    assert product.source_id == product_id
    assert product.product_title == product_title
    assert product.product_price == 1195.00
    assert product.path_to_image == image_path

@pytest.mark.asyncio
async def test_parse_product_missing_price(scraper):
    test_url = "http://test.com"
    product_id = "123"
    product_title = "Test Product"
    image_url = "http://test.com/image.jpg"

    html = f"""
    <li class="{PRODUCT_CLASS}">
        <a class="button" data-product_id="{product_id}"></a>
        <h2 class="{PRODUCT_TITLE_CLASS}"><a>{product_title}</a></h2>
        <img class="{PRODUCT_IMAGE_CLASS}" data-lazy-src="{image_url}">
    </li>
    """
    product_element = BeautifulSoup(html, 'html.parser').find('li', class_=PRODUCT_CLASS)

    with pytest.raises(DataExtractionException) as exc_info:
        await scraper.parse_product(product_element, test_url)

    assert "Failed to parse product price" in str(exc_info.value)

@pytest.mark.asyncio
async def test_scrape_page_with_sample_data(scraper, sample_products):
    html = "<html><body>"
    for product in sample_products[:5]:  # Use the first 5 products from the sample data
        html += f"""
        <li class="{PRODUCT_CLASS}">
            <a class="button" data-product_id="{product['source_id']}"></a>
            <h2 class="{PRODUCT_TITLE_CLASS}"><a>{product['product_title']}</a></h2>
            <span class="{PRODUCT_PRICE_CLASS}">{product['product_price']}</span>
            <img class="{PRODUCT_IMAGE_CLASS}" data-lazy-src="{product['path_to_image']}">
        </li>
        """
    html += "</body></html>"

    with patch.object(scraper, 'fetch_page', return_value=html), \
         patch('app.utils.image_downloader.download_image', return_value="./storage/images/test.jpg"), \
         patch('app.utils.scraper.TARGET_URL', 'https://dentalstall.com'), \
         patch('os.path.exists', return_value=True):
        products = await scraper.scrape_page(TARGET_URL)

    assert len(products) == 5
    for i, product in enumerate(products):
        assert product.source_id == sample_products[i]['source_id']
        assert product.product_title == sample_products[i]['product_title']
        assert product.product_price == float(sample_products[i]['product_price'])
        assert product.path_to_image == "./storage/images/test.jpg"

def test_get_next_page_url(scraper):
    html = f"""
    <html>
        <body>
            <a class="{NEXT_PAGE_CLASS}" href="https://dentalstall.com/shop/page/2/">Next</a>
        </body>
    </html>
    """
    with patch('app.utils.scraper.TARGET_URL', 'https://dentalstall.com/shop/'):
        next_url = scraper.get_next_page_url(html)

    assert next_url == "https://dentalstall.com/shop/page/2/"

def test_get_next_page_url_last_page(scraper):
    html = "<html><body></body></html>"
    with patch('app.utils.scraper.TARGET_URL', 'https://dentalstall.com/shop/'):
        next_url = scraper.get_next_page_url(html)

    assert next_url is None
