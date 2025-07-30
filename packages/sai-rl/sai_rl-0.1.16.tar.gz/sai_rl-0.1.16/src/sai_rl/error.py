class SAIError(Exception):
    """Base exception class for SAI-specific errors"""

    pass


class PackageError(SAIError):
    """Error related to package control"""

    pass


class ConfigurationError(SAIError):
    """Error related to client configuration"""

    pass


class AuthenticationError(SAIError):
    """Error related to API authentication"""

    pass


class ModelError(SAIError):
    """Error related to model operations"""

    pass


class CompetitionError(SAIError):
    """Error related to competition operations"""

    pass


class EnvironmentError(SAIError):
    """Error related to environment operations"""

    pass


class MatchError(SAIError):
    """Error related to match operations"""

    pass


class BenchmarkError(SAIError):
    """Error related to benchmark operations"""

    pass


class RecordingError(SAIError):
    """Error related to recording operations"""

    pass


class SubmissionError(SAIError):
    """Error related to submission operations"""

    pass


class NetworkError(SAIError):
    """Error related to API communication"""

    pass


class CustomCodeError(SAIError):
    """Error related to action functions"""

    pass


class SetupError(SAIError):
    """Error related to setup"""

    pass
