from cgc.commands.exceptions import ResponseException


class BillingCommandException(ResponseException):
    pass


class NoCostsFound(BillingCommandException):
    def __init__(self) -> None:
        super().__init__("No costs found in your namespace for current month.")


class NoInvoiceFoundForSelectedMonth(BillingCommandException):
    def __init__(self, year: int, month: int) -> None:
        super().__init__(f"No invoice found for {month}.{year}.")


class NoVolumeStopEvents(BillingCommandException):
    def __init__(self) -> None:
        super().__init__("No volume stop events to list.")


class NoResourceStopEvents(BillingCommandException):
    def __init__(self) -> None:
        super().__init__("No resource stop events to list.")
