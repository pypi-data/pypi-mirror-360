from typing import Optional


class Config:
    def __init__(
        self,
        max_report_length: Optional[int] = 50,
        ignore_functions: bool = False,
        ignore_manual: bool = False,
        ignore_tracebacks: bool = False,
    ) -> None:
        """Configuration of the core Eulogy logging functionality

        Parameters
        ----------
        max_report_length : int, optional
            Set a limit to the number of reported events being stored, covering
            both manual logs and function call traces, implemented as a deque,
            by default 50
        ignore_functions : bool
            Prevent decorated functions from being reported, by default False
        ignore_manual : bool
            Prevent manual messages being reported, by default False
        ignore_tracebacks : bool
            Prevent *handled* error tracebacks from appearing in the report, by
            default False
        """
        self.max_report_length = max_report_length
        self.ignore_functions = ignore_functions
        self.ignore_manual = ignore_manual
        self.ignore_tracebacks = ignore_tracebacks
