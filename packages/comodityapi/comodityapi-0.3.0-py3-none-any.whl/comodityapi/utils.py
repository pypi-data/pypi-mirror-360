import logging
from datetime import datetime
from typing import List
from comodityapi.constants import COMMODITY_SYMBOLS, VALID_QUOTES

logger = logging.getLogger(__name__)


def validate_date(date_str: str) -> bool:
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_obj > datetime.today().date():
            logger.warning("❌ Date cannot be in the future.")
            return False
        if date_obj < datetime(1970, 1, 1).date():
            logger.warning("❌ Date cannot be before 1970-01-01.")
            return False
        return True
    except ValueError:
        logger.warning("❌ Invalid date format. Use YYYY-MM-DD.")
        return False


def validate_symbols(symbols: List[str]) -> bool:
    normalized = [s.strip().upper() for s in symbols]
    invalid = [s for s in normalized if s not in COMMODITY_SYMBOLS]
    if invalid:
        logger.warning(f"❌ Invalid commodity symbols: {invalid}")
        return False
    return True


def validate_quote(quote: str) -> bool:
    return quote.strip().upper() in VALID_QUOTES
