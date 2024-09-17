import init  # noqa: F401
from unittest import TestCase
from os import environ
from time import sleep
from app.application.logging import logger, DEBUG


class TestInfraestructureLoggingCustomLogger(TestCase):
    def test_logging_stopwatch(self):
        # OVERRYDE: environment variable LOGGING_LEVEL
        environ['LOGGING_LEVEL'] = 'DEBUG'

        excepted_delay_1_in_ms = 100
        excepted_delay_2_in_ms = 200
        excepted_delay_3_in_ms = 200

        expected_delay_msg = "Must return the expected time catched"

        logger.setLevel(DEBUG)
        logger.start_stopwatch()
        sleep(excepted_delay_1_in_ms / 1000)
        chkpnt_1 = logger.checkpoint_stopwatch(
            message="Checkpoint 1 {ms} ms")

        sleep(excepted_delay_2_in_ms / 1000 / 4)

        logger.start_stopwatch(name='named')
        sleep(excepted_delay_2_in_ms / 1000 / 4)
        chkpnt_named_1 = logger.checkpoint_stopwatch(
            message="Checkpoint named 1 {ms} ms", name='named')
        sleep(excepted_delay_2_in_ms / 1000 / 2)
        chkpnt_named_2 = logger.checkpoint_stopwatch(
            message="Checkpoint named 2 {ms} ms", name='named')

        chkpnt_2 = logger.checkpoint_stopwatch(
            message="Checkpoint 2 {ms} ms")
        sleep(excepted_delay_3_in_ms / 1000)
        chkpnt_3 = logger.checkpoint_stopwatch(
            message="Checkpoint 3 {ms} ms")
        chkpnt_final = logger.stop_stopwatch(
            message="Checkpoint final {ms} ms")

        assert chkpnt_1 >= excepted_delay_1_in_ms, expected_delay_msg
        assert chkpnt_named_1 >= excepted_delay_2_in_ms/4, expected_delay_msg
        assert chkpnt_named_2 >= excepted_delay_2_in_ms/2, expected_delay_msg
        assert chkpnt_2 >= excepted_delay_2_in_ms, expected_delay_msg
        assert chkpnt_3 >= excepted_delay_3_in_ms, expected_delay_msg
        assert chkpnt_final >= sum([
                excepted_delay_1_in_ms,
                excepted_delay_2_in_ms,
                excepted_delay_3_in_ms
            ]), expected_delay_msg
