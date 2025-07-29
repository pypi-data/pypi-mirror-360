import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

RETRY_TOTAL = 4
ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
FORCE_LIST = (429, 500, 502, 503, 504)
BACKOFF_FACTOR = 4
MAX_WORKERS = 44

_session = None

def create_session(total= RETRY_TOTAL, allowed_methods=ALLOWED_METHODS, status_forcelist=FORCE_LIST, backoff_factor = BACKOFF_FACTOR):
    session = requests.Session()
    retries = Retry(total=total, allowed_methods=allowed_methods, status_forcelist=status_forcelist, backoff_factor=backoff_factor)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_session():
    global _session
    if _session is None:
        _session = create_session()
        print('create_session')
    return _session

def request_with_retry(method, url, session=None, **kwargs):
    session = session or get_session()

    try:
        response = session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(e)
        return {}

def parallel_fetch(func, batches, *args, max_workers=MAX_WORKERS, tokens=None, **kwargs):
    results = []

    with ThreadPoolExecutor(max_workers=min(max_workers, len(batches))) as executor:
        futures = {
            executor.submit(
                func,
                batch,
                *((tokens[i % len(tokens)],) + args if tokens else args),
                **kwargs
            ): None for i, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    results.extend(result)
            except Exception as e:
                print(e)

    return results