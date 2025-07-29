import logging
from base64 import b64decode
from typing import Optional

import requests
from scrapy.http import HtmlResponse, Request
from scrapy import Spider
from scrapy.exceptions import IgnoreRequest
import json

from .auth import sign_request, create_auth_headers
from .config import Config
from .endpoints import API_URL
from .version import __version__
from .utils import extract_response_data
from .operations import AskPablosAPIMapValidator, create_api_payload
from .exceptions import (
    AskPablosAPIError, RateLimitError, AuthenticationError,
    BrowserRenderingError, handle_api_error
)

# Configure logger
logger = logging.getLogger('askpablos_scrapy_api')


class AskPablosAPIDownloaderMiddleware:
    """
    Scrapy middleware to route selected requests through AskPablos proxy API.

    This middleware activates **only** for requests that include:
        meta = {
            "askpablos_api_map": {
                "browser": True,          # Optional: Use headless browser
                "rotate_proxy": True,     # Optional: Use rotating proxy IP
                "wait_for_load": True,    # Optional: Wait for page load (requires browser: True)
                "screenshot": True,       # Optional: Take screenshot (requires browser: True)
                "js_strategy": "DEFAULT", # Optional: JavaScript strategy (requires browser: True)
            }
        }

    It will bypass any request that does not include the `askpablos_api_map` key or has it as an empty dict.

    Configuration (via settings.py or `custom_settings` in your spider):
        API_KEY      = "<your API key>"
        SECRET_KEY   = "<your secret key>"

    Optional settings:
        TIMEOUT = 30  # Request timeout in seconds
        MAX_RETRIES = 2  # Maximum number of retries for failed requests
    """

    def __init__(self, api_key, secret_key, config):
        """
        Initialize the middleware.

        Args:
            api_key: API key for authentication
            secret_key: Secret key for request signing
            config: Configuration object containing settings
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.config = config
        logger.debug(f"AskPablos Scrapy API initialized (version: {__version__})")

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from Scrapy crawler.

        Loads configuration from:
        1. Spider's custom_settings (if available)
        2. Project settings.py
        3. Environment variables
        """
        # Load configuration
        config = Config()
        config.load_from_settings(crawler.settings)
        config.load_from_env()

        try:
            config.validate()
        except ValueError as e:
            error_msg = f"AskPablos API configuration validation failed: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return cls(
            api_key=config.get('API_KEY'),
            secret_key=config.get('SECRET_KEY'),
            config=config
        )

    def process_request(self, request: Request, spider: Spider) -> Optional[HtmlResponse]:
        """Process a Scrapy request."""
        proxy_cfg = request.meta.get("askpablos_api_map")

        if not proxy_cfg or not isinstance(proxy_cfg, dict) or not proxy_cfg:
            return None  # Skip proxying

        try:
            # Validate and normalize the configuration
            validated_config = AskPablosAPIMapValidator.validate_config(proxy_cfg)

            # Create API payload with all the configuration
            payload = create_api_payload(
                request_url=request.url,
                request_method=request.method if hasattr(request, "method") else "GET",
                config=validated_config
            )

            # Override with default values if not specified
            if 'timeout' not in payload:
                payload['timeout'] = self.config.get('TIMEOUT')
            if 'maxRetries' not in payload:
                payload['maxRetries'] = self.config.get('RETRIES')

            # Sign the request using auth module
            request_json, signature_b64 = sign_request(payload, self.secret_key)
            headers = create_auth_headers(self.api_key, signature_b64)

            # Log sanitized payload for debugging
            logger.debug(f"AskPablos API: Sending request for URL: {request.url}")

            # Make API request using the URL from constants
            response = requests.post(
                API_URL,
                data=request_json,
                headers=headers,
                timeout=payload.get('timeout', self.config.get('TIMEOUT'))
            )

            # Handle HTTP error status codes
            if response.status_code != 200:
                response_data = extract_response_data(response)
                # Use factory function to create appropriate exception
                error = handle_api_error(response.status_code, response_data)
                spider.crawler.stats.inc_value(f"askpablos/errors/{error.__class__.__name__}")
                raise error

            # Parse response
            try:
                proxy_response = response.json()
            except (ValueError, json.JSONDecodeError):
                spider.crawler.stats.inc_value("askpablos/errors/json_decode")
                raise json.JSONDecodeError(f"AskPablos API returned invalid JSON response for {request.url}", "", 0)

            # Validate response content
            html_body = proxy_response.get("responseBody", "")
            if not html_body:
                spider.crawler.stats.inc_value("askpablos/errors/empty_response")
                raise ValueError(f"AskPablos API response missing required 'responseBody' field")

            # Handle browser rendering errors
            if validated_config.get("browser") and proxy_response.get("error"):
                error_msg = proxy_response.get("error", "Unknown browser rendering error")
                spider.crawler.stats.inc_value("askpablos/errors/browser_rendering")
                raise BrowserRenderingError(error_msg, response=proxy_response)

            body = b64decode(html_body).decode()

            updated_meta = request.meta.copy()
            updated_meta['raw_api_response'] = proxy_response

            # Add additional response data to meta
            if proxy_response.get("screenshot"):
                updated_meta['screenshot'] = b64decode(proxy_response["screenshot"])

            return HtmlResponse(
                url=request.url,
                body=body,
                encoding="utf-8",
                request=request.replace(meta=updated_meta),
                status=proxy_response.get("statusCode", 200),
                flags=["askpablos-api"]
            )

        except json.JSONDecodeError:
            raise
        except ValueError as e:
            # Configuration validation error
            spider.crawler.stats.inc_value("askpablos/errors/config_validation")
            logger.error(f"AskPablos API configuration error: {e}")
            raise IgnoreRequest(f"Invalid askpablos_api_map configuration: {e}")

        except requests.exceptions.Timeout:
            spider.crawler.stats.inc_value("askpablos/errors/timeout")
            raise TimeoutError(f"AskPablos API request timed out for URL: {request.url}")

        except requests.exceptions.ConnectionError as e:
            spider.crawler.stats.inc_value("askpablos/errors/connection")
            raise ConnectionError(f"AskPablos API connection error for URL: {request.url} - {str(e)}")

        except requests.exceptions.RequestException as e:
            spider.crawler.stats.inc_value("askpablos/errors/request")
            raise RuntimeError(f"AskPablos API request failed: {str(e)}")

        except AuthenticationError as e:
            # Critical authentication error - stop the spider immediately
            spider.crawler.stats.inc_value("askpablos/errors/authentication")
            error_msg = f"Authentication failed with AskPablos API: {str(e)}."
            logger.error(error_msg)

            # Use crawler's signal system to close the spider
            spider.crawler.engine.close_spider(spider, error_msg)

            # Raise IgnoreRequest to prevent this request from being processed further
            raise IgnoreRequest(error_msg)

        except (RateLimitError, BrowserRenderingError, AskPablosAPIError):
            raise

        except Exception as e:
            logger.error(e)
            spider.crawler.stats.inc_value("askpablos/errors/unexpected")
            raise RuntimeError(f"AskPablos API encountered an unexpected error: {str(e)}")
