"""Constants"""

from dataclasses import dataclass


@dataclass
class SwiftyCacheEvents:
    """_summary_"""

    SWIFTY_CACHE = "SWIFTY_CACHE"
    CACHED_DATA = f"{SWIFTY_CACHE}: Cached data was get"
    CREATE_NEW_CACHE = f"{SWIFTY_CACHE}: Create new cache"
    DATA_NOT_IN_CACHE = f"{SWIFTY_CACHE}: Data not in cache"
