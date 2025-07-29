"""Constants"""

from dataclasses import dataclass


@dataclass
class SqlConnectionEvents:
    """_summary_"""

    SQL_CONNECTION = "SQL_CONNECTION"
    SUCCESSFULLY_COMMIT = f"{SQL_CONNECTION}: Commit succeeded, data was stored to DB"
    ERROR_WHEN_COMMIT = (
        f"{SQL_CONNECTION}: An error occurred when committing, rolled back"
    )
    ERROR_WHEN_QUERY_DATA = f"{SQL_CONNECTION}: Error when query data"
