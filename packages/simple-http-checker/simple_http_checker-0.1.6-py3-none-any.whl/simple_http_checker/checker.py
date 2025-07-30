# src/simple_http_checker/checker.py
import logging

import requests

# Get a logger for this module. The application (cli.py) will configure the handler.
log = logging.getLogger(__name__)


def check_urls(urls: list[str], timeout: int = 5) -> dict[str, str]:
    """
    Checks a list of URLs and returns their status.
    """
    log.info(f"Starting check for {len(urls)} URLs with a timeout of {timeout}s.")
    results = {}
    for url in urls:
        status = "UNKNOWN"
        try:
            log.debug(f"Checking URL: {url}")
            response = requests.get(url, timeout=timeout)
            if response.ok:
                status = f"{response.status_code} OK"
            else:
                status = f"{response.status_code} {response.reason}"
        except requests.exceptions.Timeout:
            status = "TIMEOUT"
            log.warning(f"Request to {url} timed out.")
        except requests.exceptions.ConnectionError:
            status = "CONNECTION_ERROR"
            log.warning(f"Connection error for {url}.")
        except requests.exceptions.RequestException as e:
            status = f"REQUEST_ERROR: {type(e).__name__}"
            log.error(
                f"An unexpected request error occurred for {url}: {e}", exc_info=True
            )

        results[url] = status
        log.debug(f"Checked: {url:<40} -> {status}")

    log.info("URL check finished.")
    return results
