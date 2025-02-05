


class GummyProcessError(Exception):
    """Base exception for all errors related to the Gummy subprocess."""


class GummyAlreadyRunning(GummyProcessError):
    """Raised when trying to start Gummy when he is already running."""


class GummyNotRunning(GummyProcessError):
    """Raised when trying to utilize Gummy when he is not running."""


class GummyInitializeError(GummyProcessError):
    """Raised when Gummy fails to start properly."""


class GummyMessageError(GummyProcessError):
    """Base exception for all errors related to sending and recieving messages from the Gummy subprocess."""


class GummyMessageFailedToSend(GummyMessageError):
    """Raised when a message failed to be sent to the Gummy process."""


class InvalidGummyMessage(GummyMessageError):
    """Raised when an invalid message is sent to the Gummy process."""


class InvalidGummyOutput(GummyMessageError):
    """Raised when an invalid message is sent from the Gummy process."""


class InvalidGummyMessageChannel(GummyMessageError):
    """Raised when attempting to send a message to an invalid."""