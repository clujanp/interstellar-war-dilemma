import logging
from time import time


# EXTEND: add methods to logger
class CustomRootLogger(logging.RootLogger):
    init_checkpoint = None
    last_checkpoint = 0
    init_checkpoint_custom = {}
    last_checkpoint_custom = {}

    def start_stopwatch(self, name: str = None) -> None:
        if not name:
            self.init_checkpoint = time()
            self.last_checkpoint = time()
        else:
            self.init_checkpoint_custom[name] = time()
            self.last_checkpoint_custom[name] = time()

    def set_checkpoint_stopwatch(self, name: str = None) -> None:
        if not name:
            self.last_checkpoint = time()
        else:
            self.last_checkpoint_custom[name] = time()

    def checkpoint_stopwatch(
        self,
        message: str = None,
        log_level: int = logging.DEBUG,
        relative: bool = True,
        name: str = None
    ) -> float:
        """milliseconds stopwatch.

        Args:
            message (str, optional): send message in log method.
                Defaults to None.
            log_level (int, optional): log level. Defaults to logging.DEBUG.
            relative (bool, optional): relative to last checkpoint.
                Defaults to True.

        Returns:
            int: time catched in milliseconds.
        """
        assert (self.init_checkpoint
                or self.init_checkpoint_custom.get(name, None)), (
            "run start_stopwatch before end_stopwatch")
        assert not message or (message and log_level in logging._levelToName)
        current_time = time()
        # CASES: for is relative and is named
        if relative and not name:
            reference_checkpoint = self.last_checkpoint
        elif relative:
            reference_checkpoint = self.last_checkpoint_custom.get(
                name, self.last_checkpoint)
        elif name:
            reference_checkpoint = self.init_checkpoint_custom.get(
                name, self.init_checkpoint)
        else:
            reference_checkpoint = self.init_checkpoint
        # CALCULATE: time of milliseconds
        ms = (time() - reference_checkpoint)*1000
        # update last checkpoint
        if not name:
            self.last_checkpoint = current_time
        else:
            self.last_checkpoint_custom[name] = current_time
        if message:
            self.log(log_level, message.format(ms=ms))
        return ms

    def stop_stopwatch(
        self,
        message: str = None,
        log_level: int = logging.DEBUG,
        name: str = None
    ) -> int:
        return self.checkpoint_stopwatch(
            message=message,
            log_level=log_level,
            relative=False,
            name=name
        )
