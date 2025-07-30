from .v3 import DetailsV3

class Details:
    """
    Entry point for versioned Details API clients.
    Usage: Details.v3
    """
    def __init__(self, authenticator):
        self.v3 = DetailsV3(authenticator)
