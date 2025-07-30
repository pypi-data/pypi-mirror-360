from cgc.commands.exceptions import ResponseException


class JobCommandException(ResponseException):
    pass


class NoJobsToList(JobCommandException):
    def __init__(self) -> None:
        super().__init__("No jobs to list.")
