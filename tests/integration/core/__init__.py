from requests import Response, JSONDecodeError
from typing import List, Tuple, Union, Optional
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
import traceback
import logging


def trunc(s: str, n: int) -> str: return s[:n] + "..." if len(s) > n else s
def as_list(obj: any) -> List[any]: return obj if type(obj) is list else [obj]


class TestExec:
    def __init__(self, name: str, function: callable, *args, **kwargs):
        self.name = name
        # execution
        self.function = function
        self.args = args
        self.kwargs = kwargs
        # execution data
        self.percent = None
        self.status_code = None
        self.execution = None
        # report
        self.summary = None
        self.details = None

    def __call__(self):
        return self.function(*self.args, **self.kwargs)


class TestBank:
    SHOW_DETAILS = False
    SHOW_TRACBACK = False
    LOGGING_LEVEL: int

    def __init__(self):
        logging.basicConfig(level=self.LOGGING_LEVEL)
        self.test_counter = {'ok': [], 'fail': []}

    def test_bank(
        self, name: str, function: callable, status: int = 200, *args, **kwargs
    ) -> Union[any, List[any]]:
        executions: List[List[any]] = self._prepare_exections(args)

        storage: OrderedDict[str, List[any]] = self._run_tests(
            executions, kwargs, function, name, status)

        percent = (
            int(storage['report'].count(True) / len(storage['report']) * 100))
        self.test_counter['ok' if percent == 100 else 'fail'].append(storage)

        summary: str
        details: List[str]
        summary, details = self.resume_test_executions(percent, name, storage)
        print(summary)
        if self.SHOW_DETAILS:
            for detail in details:
                print(f"  - {detail}")

        return (
            storage['responses'][0] if len(executions) == 1
            else storage['responses']
        )

    def _run_tests(
        self,
        executions: List[List[any]],
        kwargs: dict,
        function: callable,
        name: str,
        expected_status: int,
    ) -> OrderedDict:
        storage = OrderedDict({
            'report': [],
            'summary': [],
            'responses': [],
            'name': [],
            'lapse': []
        })
        for i, exec in enumerate(executions):
            sucess, resume, response, lapse = self.test_bank_iter(
                f"#{i + 1} {name}", function, expected_status, *exec, **kwargs)
            storage['report'].append(sucess)
            storage['summary'].append(resume)
            storage['responses'].append(response)
            storage['name'].append(f"#{i + 1} {name}")
            storage['lapse'].append(lapse)
        return storage

    def test_bank_iter(
        self, name: str, f: callable, expected_status: int, *args, **kwargs
    ) -> Tuple[Optional[bool], str, any, timedelta]:
        try:
            response: Response
            lapse: timedelta
            response, lapse = self.test_bank_core(f, *args, **kwargs)
            resume = (
                f"[{expected_status} = {response.status_code}] "
                f"{self.resume_test_response(response)}"
            )
            logging.debug(f"{name} > {response.json() = }")
            return (
                response.status_code == expected_status,
                resume,
                response.json(),
                lapse
            )
        except JSONDecodeError as err:
            resume = f"[{response.status_code}] ERROR: {err}"
            if self.SHOW_TRACBACK:
                print(f"-- {name[:141]:->}")
                print(f"raw response '{response.text}'")
                traceback.print_exc()
                print("-" * 148)
            return None, trunc(str(err), 90), defaultdict(lambda: None), None
        except Exception as err:
            resume = f"[UNKNOW] ERROR: {err}"
            if self.SHOW_TRACBACK:
                print(f"-- {name[:141]:->}")
                traceback.print_exc()
                print("-" * 148)
            return None, trunc(str(err), 90), defaultdict(lambda: None), None

    @staticmethod
    def test_bank_core(f: callable, *args, **kwargs) -> Tuple[any, timedelta]:
        start = datetime.now()
        response = f(*args, **kwargs)
        end = datetime.now()
        return response, end - start

    @staticmethod
    def _prepare_exections(args: List[any]) -> List[List[any]]:
        return (
            [as_list(a) for a in args[0]]
            if len(args) == 1 and isinstance(args[0], list)
            else [args]
        )

    @classmethod
    def resume_test_executions(
        cls, percent: float, name: str, storage: dict
    ) -> Tuple[str, List[str]]:
        details = []
        for report, _summary, response, _name, lapse in zip(*storage.values()):
            _percent = 100 if report else 0
            details.append(
                cls.resume_test_execution(_percent, _name, _summary, lapse))

        if len(details) == 1:
            return details[0], []

        _summary = f"with {len(storage['report'])} OPs [{percent}%]"
        summary = cls.resume_test_execution(
            percent, name, _summary, sum(storage['lapse'], timedelta()))
        return summary, details

    @classmethod
    def resume_test_execution(
        cls, percent: float, name: str, summary: str, lapse: timedelta,
    ) -> str:
        icon = cls.get_icon(percent)
        _lapse = (f"{(lapse.microseconds / 1000):.0f}ms"
                  if lapse is not None else "0ms")
        return f"{icon} {_lapse:<5} | {name} | {summary}"

    @classmethod
    def resume_test_response(cls, response: Response):
        try:
            data = response.json()
            if isinstance(data, dict):
                return f"'{trunc(cls.repr_record(data), 32)}'"
            elif isinstance(data, list):
                detail = trunc(
                    ', '.join([cls.repr_record(r) for r in data]), 32)
                return f"{len(data)} items '{detail}'"
        except JSONDecodeError:
            return f"undescribe response <{trunc(response.text, 90)}>"

    @staticmethod
    def get_icon(percent: int) -> str:
        return '✅' if percent == 100 else '❌'

    @staticmethod
    def repr_record(data: dict) -> str:
        if data.get('uid'):
            return f"{data.get('uid')[-3:]}"
        return str(data)

    def get_summary(self) -> str:
        ok = len(self.test_counter['ok'])
        fail = len(self.test_counter['fail'])
        return (
            f"  Test completed with {ok + fail} OPs: "
            f"{ok} OK and {fail} FAIL | {self.percent}% "
            f"{self.get_icon(self.percent)}"
        )

    @property
    def percent(self) -> float:
        ok = len(self.test_counter['ok'])
        fail = len(self.test_counter['fail'])
        return (ok/(ok + fail)) * 100
