from .v1 import DeliveryV1

class Delivery:
    """
    Entry point for versioned Delivery API clients.
    Usage: Delivery.v1
    """
    def __init__(self, authenticator):
        self.v1 = DeliveryV1(authenticator)
