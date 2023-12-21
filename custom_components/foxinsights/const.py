"""Constants for FoxInsights."""
from logging import getLogger, Logger

LOGGER: Logger = getLogger(__package__)

NAME = "FoxInsights"
DOMAIN = "foxinsights"
API_URL = "https://api.oilfox.io/customer-api/v1/"
ATTRIBUTION = "Data provided by " + API_URL

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

REQUEST_TIMEOUT = 10
