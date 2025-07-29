import json
import requests
import re
from typing import Any, Callable, Dict, Tuple, List, Union
from typeguard import typechecked
from clyp.ErrorHandling import ClypRuntimeError


@typechecked
class Response:
    """
    A wrapper class for HTTP responses.
    """

    def __init__(self, content: str) -> None:
        """
        Initialize the Response object.

        :param content: The content of the HTTP response as a string.
        """
        self._content: str = content

    def json(self) -> Dict[str, Any]:
        """
        Convert the JSON response content to a Python dictionary.

        :return: Parsed JSON content as a dictionary.
        :raises RuntimeError: If JSON decoding fails.
        """
        try:
            return json.loads(self._content)
        except json.JSONDecodeError as e:
            raise ClypRuntimeError(f"Failed to decode JSON: {e}") from e

    def content(self) -> str:
        """
        Get the raw content of the response.

        :return: The raw content as a string.
        """
        return self._content

    def text(self) -> str:
        """
        Get the response content as text.

        :return: The content as a string.
        """
        return str(self._content)


@typechecked
def fetch(url: str, timeout: int = 10) -> Response:
    """
    Fetch the content from a given URL.

    :param url: The URL to fetch.
    :param timeout: Timeout for the request in seconds (default is 10).
    :return: A Response object containing the fetched content.
    :raises RuntimeError: If the request fails.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return Response(response.text)
    except requests.RequestException as e:
        raise ClypRuntimeError(f"Failed to fetch {url}: {e}") from e


@typechecked
def is_empty(value: Any) -> bool:
    """
    Check if a value is empty.

    :param value: The value to check.
    :return: True if the value is empty, False otherwise.
    """
    if value is None:
        return True
    if isinstance(value, (str, list, dict, set, tuple)):
        return len(value) == 0
    return False


@typechecked
def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.

    :param text: The input string to slugify.
    :return: A slugified version of the input string.
    """
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(
        r"-+", "-", text
    )  # Replace multiple consecutive dashes with a single dash
    return text.strip("-")  # Remove leading and trailing dashes


@typechecked
def toString(value: Any) -> str:
    """
    Converts a value to its string representation.
    """
    return str(value)


@typechecked
def read_file(file_path: str, *args: Any, **kwargs: Any) -> str:
    """
    Read the content of a file.

    :param file_path: The path to the file.
    :return: The content of the file as a string.
    :raises RuntimeError: If the file cannot be read.
    """
    try:
        with open(file_path, *args, **kwargs) as file:
            return file.read()
    except IOError as e:
        raise ClypRuntimeError(f"Failed to read file {file_path}: {e}") from e


@typechecked
def write_file(file_path: str, content: str, *args: Any, **kwargs: Any) -> None:
    """
    Write content to a file.

    :param file_path: The path to the file.
    :param content: The content to write to the file.
    :raises RuntimeError: If the file cannot be written.
    """
    try:
        with open(file_path, "w", *args, **kwargs) as file:
            file.write(content)
    except IOError as e:
        raise ClypRuntimeError(f"Failed to write to file {file_path}: {e}") from e


@typechecked
def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to cache the results of a function based on its arguments.

    :param func: The function to be memoized.
    :return: A wrapper function that caches results.
    """
    cache: Dict[Tuple[Any, ...], Any] = {}

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


@typechecked
def time_it(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to measure the execution time of a function.

    :param func: The function to be timed.
    :return: A wrapper function that prints the execution time.
    """
    import time

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result

    return wrapper


@typechecked
def is_prime(n: int) -> bool:
    """
    Check if a number is prime.

    :param n: The number to check.
    :return: True if the number is prime, False otherwise.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


@typechecked
def to_roman_numerals(num: int) -> str:
    """
    Convert an integer to a Roman numeral.

    :param num: The integer to convert.
    :return: The Roman numeral representation of the integer.
    :raises ClypRuntimeError: If the number is out of range (1-3999).
    """
    if not (1 <= num <= 3999):
        raise ClypRuntimeError("Number must be between 1 and 3999")

    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]

    roman_numeral = ""
    for i in range(len(val)):
        while num >= val[i]:
            roman_numeral += syms[i]
            num -= val[i]

    return roman_numeral


@typechecked
def chance(percentage: Any) -> bool:
    """
    Determine if an event occurs based on a given percentage chance.

    :param percentage: The chance of the event occurring (0-100). Can be a float or a string like '25%'.
    :return: True if the event occurs, False otherwise.
    :raises ValueError: If the percentage is not valid.
    """
    if isinstance(percentage, str):
        if percentage.endswith("%"):
            percentage = percentage[:-1]
        try:
            percentage = float(percentage)
        except ValueError:
            raise ValueError(
                "Invalid percentage format. Must be a number or a string like '25%'."
            )

    if not (0 <= percentage <= 100):
        raise ValueError("Percentage must be between 0 and 100")

    import random

    return random.random() < (percentage / 100)


@typechecked
def duration(seconds: int) -> Callable[[Callable[[], None]], None]:
    """
    Execute a given function repeatedly for a specified duration in seconds.

    :param seconds: The duration in seconds.
    :return: A callable that accepts a function to execute.
    """
    if not isinstance(seconds, int) or seconds < 0:
        raise ValueError("Duration must be a non-negative integer")

    def wrapper(func: Callable[[], None]) -> None:
        import time

        start_time = time.time()
        while time.time() - start_time < seconds:
            func()

    return wrapper


@typechecked
def retry_with_cooldown(
    function: Callable[..., Any],
    retries: int = 3,
    cooldown: int = 1,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Retry a function with a specified number of retries and cooldown period.

    :param function: The function to retry.
    :param retries: Number of retries (default is 3).
    :param cooldown: Cooldown period in seconds between retries (default is 1).
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    :return: The result of the function if successful.
    :raises RuntimeError: If all retries fail.
    """
    import time

    if retries < 1:
        raise ValueError("Retries must be at least 1")
    if cooldown < 0:
        raise ValueError("Cooldown must be non-negative")

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries:
                time.sleep(cooldown)
            else:
                raise RuntimeError(
                    f"Function failed after {retries} attempts: {last_exception}"
                ) from last_exception


@typechecked
def throttle(
    function: Callable[..., Any], limit: int = 1, period: int = 1
) -> Callable[..., Any]:
    """
    Throttle a function to limit its execution rate.

    :param function: The function to throttle.
    :param limit: Maximum number of calls allowed in the period (default is 1).
    :param period: Time period in seconds for the limit (default is 1).
    :return: A throttled version of the function.
    """
    import time
    from collections import deque

    if limit < 1:
        raise ValueError("Limit must be at least 1")
    if period <= 0:
        raise ValueError("Period must be greater than 0")

    timestamps = deque()

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_time = time.time()
        while timestamps and timestamps[0] < current_time - period:
            timestamps.popleft()

        if len(timestamps) < limit:
            timestamps.append(current_time)
            return function(*args, **kwargs)
        else:
            raise RuntimeError("Function call limit exceeded. Try again later.")

    return wrapper


@typechecked
def flatten(list_of_lists: List[List[Any]]) -> List[Any]:
    """
    Flatten a list of lists into a single list.

    :param list_of_lists: A list containing other lists.
    :return: A flattened list containing all elements.
    """
    return [item for sublist in list_of_lists for item in sublist]


def chunk(items: List[Any], size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.

    :param items: The list of items to chunk.
    :param size: The size of each chunk.
    :return: A list of chunks.
    """
    if not isinstance(items, list):
        raise ValueError("Items must be a list")
    if not isinstance(size, int) or size <= 0:
        raise ValueError("Size must be a positive integer")

    return [items[i : i + size] for i in range(0, len(items), size)]


def benchmark(func: Callable[[], Any], iterations: int = 1000) -> float:
    """
    Benchmark a function by measuring its execution time over a number of iterations.

    :param func: The function to benchmark.
    :param iterations: The number of iterations to run (default is 1000).
    :return: The average execution time in seconds.
    """
    import time

    if not callable(func):
        raise ValueError("Function must be callable")
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("Iterations must be a positive integer")

    start_time = time.time()
    for _ in range(iterations):
        func()
    end_time = time.time()

    return (end_time - start_time) / iterations


@typechecked
def cache(
    ttl: Union[int, str, float],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Cache the result of a function for a specified time-to-live (TTL).

    :param ttl: Time-to-live in seconds (can be an int, float, or string like '5s').
    :return: A decorator that caches the function's result.
    """
    import time
    from functools import wraps

    if isinstance(ttl, str):
        units = {
            "s": 1,
            "sec": 1,
            "secs": 1,
            "seconds": 1,
            "m": 60,
            "min": 60,
            "mins": 60,
            "minutes": 60,
            "h": 3600,
            "hr": 3600,
            "hrs": 3600,
            "hours": 3600,
            "d": 86400,
            "day": 86400,
            "days": 86400,
            "w": 604800,
            "wk": 604800,
            "wks": 604800,
            "weeks": 604800,
            "y": 31536000,
            "yr": 31536000,
            "yrs": 31536000,
            "years": 31536000,
        }
        match = re.match(r"^(\d+(?:\.\d+)?)\s*(\w+)$", ttl.strip())
        if match:
            value, unit = match.groups()
            if unit in units:
                ttl = float(value) * units[unit]
            else:
                raise ValueError(f"Unsupported time unit: {unit}")
        else:
            raise ValueError("TTL must be a number followed by a valid time unit")

    if not isinstance(ttl, (int, float)) or ttl <= 0:
        raise ValueError("TTL must be a positive number")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache_data: Dict[Tuple[Any, ...], Tuple[Any, float]] = {}

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, frozenset(kwargs.items()))
            current_time = time.time()
            if key in cache_data:
                value, timestamp = cache_data[key]
                if current_time - timestamp < ttl:
                    return value
            value = func(*args, **kwargs)
            cache_data[key] = (value, current_time)
            return value

        return wrapper

    return decorator


@typechecked
def trace(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to trace the execution of a function, printing its arguments and return value.

    :param func: The function to trace.
    :return: A wrapper function that prints the trace information.
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result

    return wrapper


@typechecked
def ping(host: str, timeout: int = 1) -> Union[float, bool]:
    """
    Ping a host to check if it is reachable.

    :param host: The hostname or IP address to ping.
    :param timeout: Timeout for the ping in seconds (default is 1).
    :return: True if the host is reachable, False otherwise.
    :raises RuntimeError: If the ping command fails.
    """
    import subprocess

    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        match = re.search(r"time=(\d+\.\d+) ms", output)
        if match:
            return float(match.group(1))
        return False
    except subprocess.CalledProcessError as e:
        raise ClypRuntimeError(f"Ping failed for {host}: {e.output}") from e


@typechecked
def random_choice_weighted(choices: List[Tuple[Any, float]]) -> Any:
    """
    Randomly select an item from a list of choices with associated weights.

    :param choices: A list of tuples where each tuple contains an item and its weight.
    :return: A randomly selected item based on the weights.
    :raises ValueError: If the total weight is zero or negative.
    """
    import random

    if not choices:
        raise ValueError("Choices list cannot be empty")

    total_weight = sum(weight for _, weight in choices)
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")

    rand_val = random.uniform(0, total_weight)
    cumulative_weight = 0.0
    for item, weight in choices:
        cumulative_weight += weight
        if rand_val < cumulative_weight:
            return item

    return None
