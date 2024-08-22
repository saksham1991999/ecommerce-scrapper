class ScraperException(Exception):
    """Base exception for scraper-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NetworkException(ScraperException):
    """Exception raised for network-related errors during scraping."""
    pass


class ParsingException(ScraperException):
    """Exception raised for errors during HTML parsing."""
    pass


class ProxyException(ScraperException):
    """Exception raised for errors related to proxy usage."""
    pass


class PaginationException(ScraperException):
    """Exception raised for errors during pagination handling."""
    pass


class DataExtractionException(ScraperException):
    """Exception raised for errors during data extraction from scraped content."""
    pass
