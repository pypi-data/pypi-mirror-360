import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

# reset color after each print
init(autoreset=True)

"""
    @params:
        code -> int
        url -> str
"""
def colorize(code, url):
    if isinstance(code, int):
        if 200 <= code < 300:
            return f"{Fore.GREEN}[{code}]{Style.RESET_ALL} {url}"
        elif 300 <= code < 400:
            return f"{Fore.YELLOW}[{code}]{Style.RESET_ALL} {url}"
        elif 400 <= code < 600:
            return f"{Fore.RED}[{code}]{Style.RESET_ALL} {url}"
    return f"{Fore.MAGENTA}[ERR]{Style.RESET_ALL} {url}"


"""
    @params:
        url -> str
    @output:
        status_string -> str
    @description:
        Hits the URL and check for the status code
"""
def fetch_url_status(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        return colorize(response.status_code, url)
    except requests.exceptions.RequestException as e:
        return colorize("ERR", f"{url} ({str(e)})")

def check_urls(urls, max_workers=10):
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Dictionary comprehension
        future_to_url = {executor.submit(fetch_url_status, url): url for url in urls}
        """
            future_to_url = {
                Future: 'https://something.com',
                Future: 'https://example.com',
            }
        """
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
    return results
            