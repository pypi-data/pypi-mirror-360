from __future__ import annotations

import hashlib
import traceback
from collections import namedtuple
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from functools import wraps
from threading import Lock
from typing import TYPE_CHECKING, Any, Callable, Generator, cast
from uuid import uuid4

import pytest
from _pytest.compat import is_generator

if TYPE_CHECKING:
    from datetime import timedelta
    from types import TracebackType
    from typing import Dict, List, Literal, Optional, Set, Type, Union
    from uuid import UUID

    from _pytest.config import Config
    from _pytest.nodes import Item
    from _pytest.reports import TestReport
    from _pytest.runner import CallInfo

TestExecutionResultDetail = namedtuple(
    "TestExecutionResultDetail", ["type", "message", "trace"]
)


class TestExecutionResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    XPASS = "XPASS"
    XFAIL = "XFAIL"
    ABORT = "ABORT"
    ERROR = "ERROR"


class TestExecution:
    def __init__(self, title: Optional[str] = None):
        self._id: UUID = uuid4()

        if title:
            self.title = title

        self.start_time: Optional[datetime] = None
        self.stop_time: Optional[datetime] = None
        self.result: Optional[TestExecutionResult] = None
        self.result_detail: Optional[TestExecutionResultDetail] = None
        self.reason: Optional[str] = None

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def id_hex(self) -> str:
        return self._id.hex

    @property
    def id_bytes(self) -> bytes:
        return self._id.bytes

    def start(self) -> None:
        if self.is_inited:
            self.start_time = datetime.now()

    def stop(self) -> None:
        if self.is_started:
            self.stop_time = datetime.now()

    def abort(self, stop: bool = True) -> None:
        if self.is_started:
            self.result = TestExecutionResult.ABORT

            if stop:
                self.stop()

    def update_start_time(self, value: datetime) -> None:
        if self.is_started:
            self.start_time = value

    def update_stop_time(self, value: datetime) -> None:
        if self.is_stopped and value > self.start_time:
            self.stop_time = value

    @property
    def is_inited(self) -> bool:
        return self.start_time is None and self.stop_time is None

    @property
    def is_started(self) -> bool:
        return self.start_time is not None and self.stop_time is None

    @property
    def is_stopped(self) -> bool:
        return self.start_time is not None and self.stop_time is not None

    @property
    def duration(self) -> Optional[timedelta]:
        if self.is_stopped:
            return self.stop_time - self.start_time

    @property
    def duration_str(self) -> Optional[str]:
        if self.is_stopped:
            return str(self.duration)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.is_stopped:
            return self.duration.total_seconds()

    def update_result_from_exception(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
        stop: bool = False,
    ) -> None:
        if not self.is_started:
            return

        if exc_val is None:
            self.result = TestExecutionResult.PASS
        else:
            if isinstance(exc_val, (AssertionError, pytest.fail.Exception)):
                self.result = TestExecutionResult.FAIL
            elif isinstance(exc_val, pytest.skip.Exception):
                self.result = TestExecutionResult.SKIP
            elif isinstance(exc_val, pytest.exit.Exception):
                self.result = TestExecutionResult.ABORT
            elif isinstance(exc_val, pytest.xfail.Exception):
                self.result = TestExecutionResult.XFAIL
            else:
                self.result = TestExecutionResult.ERROR

            self.result_detail = TestExecutionResultDetail(
                type=exc_type.__name__ if exc_type else "",
                message="/n".join(traceback.format_exception_only(exc_type, exc_val)),
                trace="".join(traceback.format_tb(exc_tb)) if exc_tb else "",
            )

        if stop:
            self.stop()

    def update_result_from_pytest_report(
        self, report: TestReport, call: CallInfo[None]
    ) -> None:
        for pytest_result, target_result in zip(
            ("failed", "passed", "skipped"),
            (
                TestExecutionResult.FAIL,
                TestExecutionResult.PASS,
                TestExecutionResult.SKIP,
            ),
        ):
            if getattr(report, pytest_result):
                self.result = target_result
                break

        if call.excinfo:
            message = call.excinfo.exconly()

            if hasattr(report, "wasxfail"):
                self.result = TestExecutionResult.XFAIL
                self.reason = getattr(report, "wasxfail")
                message = (
                    ("XFAIL {}".format(self.reason) if self.reason else "XFAIL")
                    + "\n\n"
                    + message
                )

            self.result_detail = TestExecutionResultDetail(
                message=message, trace=report.longreprtext, type=call.excinfo.typename
            )

            if self.result != TestExecutionResult.SKIP and not isinstance(
                call.excinfo.value, (AssertionError, pytest.fail.Exception)
            ):
                self.result = TestExecutionResult.ERROR

        if self.result == TestExecutionResult.PASS and hasattr(report, "wasxfail"):
            self.reason = getattr(report, "wasxfail")
            self.result = TestExecutionResult.XPASS
            self.result_detail = TestExecutionResultDetail(
                message="XPASS {}".format(self.reason) if self.reason else "XPASS"
            )

    @property
    def passed(self) -> bool:
        return self.result == TestExecutionResult.PASS

    @property
    def failed(self) -> bool:
        return self.result == TestExecutionResult.FAIL

    @property
    def aborted(self) -> bool:
        return self.result == TestExecutionResult.ABORT

    @property
    def xfailed(self) -> bool:
        return self.result == TestExecutionResult.XFAIL

    @property
    def xpassed(self) -> bool:
        return self.result == TestExecutionResult.XPASS

    @property
    def error(self) -> bool:
        return self.result == TestExecutionResult.ERROR

    @property
    def skipped(self) -> bool:
        return self.result == TestExecutionResult.SKIP

    def __repr__(self) -> str:
        if self.is_stopped:
            return "<{} title={!r}, start_time={}, end_time={}, result={}>".format(
                self.__class__.__name__,
                self.title,
                self.start_time,
                self.stop_time,
                self.result,
            )

        return "<{} title={!r}, start_time={}>".format(
            self.__class__.__name__, self.title, self.start_time
        )


class TestStep(TestExecution):
    def __init__(
        self,
        title: str,
        when: Optional[Literal["setup", "call", "teardown"]] = None,
        scope: Optional[
            Literal["session", "package", "module", "class", "function"]
        ] = None,
    ):
        assert title, "Teststep title can not be empty!"
        super().__init__(title)

        self.when = when
        self.scope = scope
        self.test_steps: List[TestStep] = []

        self._origin_test_exec: Union[TestCase, TestStep] = None

    def __enter__(self) -> TestStep:
        self._origin_test_exec = TestSession().current_test_exec
        self._origin_test_exec.test_steps.append(self)

        TestSession().current_test_exec = self

        if self._origin_test_exec.when:
            self.when = self._origin_test_exec.when

        self.start()

        TestSession().pytest_config.hook.pytest_lamber_log_test_step_start(
            test_step=self, parent=self._origin_test_exec
        )

        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.update_result_from_exception(exc_type, exc_val, exc_tb, stop=True)

        TestSession().pytest_config.hook.pytest_lamber_log_test_step_stop(
            test_step=self, result=self.result, result_detail=self.result_detail
        )

        TestSession().current_test_exec = self._origin_test_exec

    def dump(self, prefix: str = " " * 2) -> str:
        output = []
        output.append(
            prefix
            + "[{}] <title={!r}, result={}, duration={}{}>".format(
                self.when,
                self.title,
                self.result,
                self.duration_str,
                " scope={!r}".format(self.scope) if self.scope else "",
            )
        )

        for step in self.test_steps:
            output.append(step.dump(prefix + " " * 2))

        return "\n".join(output)


def step(
    title: str,
    *,
    scope: Optional[
        Literal["session", "package", "module", "class", "function"]
    ] = None,
    when: Optional[Literal["setup", "call", "teardown"]] = None,
):
    def _decorator(func: Callable[..., Any]):
        if is_generator(func):

            @wraps(func)
            def _wrap_step(*args, **kwargs):
                _func = cast(Callable[..., Generator[Any, None, None]], func)
                generator = _func(*args, **kwargs)

                with TestStep(title, when=when, scope=scope):
                    result = next(generator)

                yield result

                with TestStep(title, when=when, scope=scope):
                    try:
                        next(generator)
                    except StopIteration:
                        pass
        else:

            @wraps(func)
            def _wrap_step(*args, **kwargs):
                _func = cast(Callable[..., Any], func)

                with TestStep(title, when=when, scope=scope):
                    return _func(*args, **kwargs)

        return _wrap_step

    return _decorator


class AttachmentType(Enum):
    TEXT = ("text/plain", "txt")
    HTML = ("text/html", "html")
    PNG = ("image/png", "png")
    JPEG = ("image/jpeg", "jpeg")
    URI = ("text/uri-list", "uri")
    CSV = ("text/csv", "csv")
    XML = ("text/xml", "xml")

    def __init__(self, mime_type: str, extension: str) -> None:
        self.mime_type = mime_type
        self.extension = extension


class Attachment:
    def __init__(self, name: str, type: AttachmentType, value: any):
        self.id = uuid4()
        self.name = name
        self.content_type = type
        self.content_value = value
        self.create_time = datetime.now()


class TestCase(TestStep):
    def __init__(self, item: Item):
        super().__init__(item.name)

        self.nodeid = item.nodeid
        self.sourcecodes: Set[str] = set()
        self.marker = self._compute_marker(item)
        self.caplog: Optional[str] = None
        self.capstderr: Optional[str] = None
        self.capstdout: Optional[str] = None
        self.attachments: Dict[str, Attachment] = {}

    def _compute_marker(self, item: Item) -> List[dict]:
        return [
            asdict(
                marker,
                dict_factory=lambda data: {
                    key: val for key, val in data if not key.startswith("_")
                },
            )
            for marker in item.iter_markers()
        ]

    def _compute_result(self) -> Optional[TestExecutionResult]:
        if not self.is_stopped:
            return None

        for test_step in reversed(self.test_steps):
            if not test_step.passed:
                return test_step.result

        return TestExecutionResult.PASS

    def update_result(self):
        result: Optional[TestExecutionResult] = self._compute_result()
        if result:
            self.result = result

    def stop(self, update_result: bool = True):
        super().stop()

        if update_result:
            self.update_result()

    def dump(self, prefix: str = " " * 2) -> str:
        output = [self.nodeid]

        for test_step in self.test_steps:
            output.append(test_step.dump(prefix))

        return "\n".join(output)

    @property
    def sourcecode(self) -> str:
        return "\n\n".join(self.sourcecodes)

    def attach(self, name: str, value: any, type: AttachmentType = AttachmentType.TEXT):
        self.attachments[name] = Attachment(name, type, value)


class SingletonMetaClass(type):
    _lock = Lock()
    _instances = {}

    def __call__(mcls, *args, **kwds):  # noqa: D102
        with mcls._lock:
            if mcls not in mcls._instances:
                mcls._instances[mcls] = super().__call__(*args, **kwds)
        return mcls._instances[mcls]


class TestSession(TestExecution, metaclass=SingletonMetaClass):
    def __init__(self, config: Config):
        self.project = config.getoption("lamber_project")
        if not self.project:
            self.project = "Lamber"

        self.project_id = int(
            hashlib.sha1(self.project.encode("utf-8")).hexdigest(), 16
        ) % (10**8)

        self.pytest_config = config

        self.test_cases: Dict[str, TestCase] = {}
        self.environment: Dict[str, str] = {}

        self.current_test_case: Optional[TestCase] = None
        self.current_test_exec: Optional[Union[TestCase, TestStep]] = None

        super().__init__(self.project)

    def _compute_result(self) -> Optional[TestExecutionResult]:
        for test_case in reversed(self.test_cases.values()):
            if not test_case.is_stopped:
                return

            if not test_case.passed:
                return test_case.result

        return TestExecutionResult.PASS

    def update_result(self):
        result: Optional[TestExecutionResult] = self._compute_result()
        if result:
            self.result = result

    def stop(self, update_result: bool = True):
        super().stop()

        if update_result:
            self.update_result()
