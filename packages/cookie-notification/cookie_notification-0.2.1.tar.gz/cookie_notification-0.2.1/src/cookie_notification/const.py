from datetime import (
    datetime,
)


# Потому что нельзя просто словами написать "не скоро".
CONFIRMATION_COOKIE_EXPIRES_AT = datetime(2038, 12, 31, 0, 0, 0)
