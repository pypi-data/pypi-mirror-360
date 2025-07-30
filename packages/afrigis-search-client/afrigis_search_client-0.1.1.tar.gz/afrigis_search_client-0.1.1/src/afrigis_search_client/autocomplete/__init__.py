from .v3 import AutocompleteV3

class Autocomplete:
    """
    Entry point for versioned Autocomplete API clients.
    Usage: Autocomplete.v3
    """
    def __init__(self, authenticator):
        self.v3 = AutocompleteV3(authenticator)
