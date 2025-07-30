from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Union

    from _pytest.config import Config, ExitCode

    from lamber.models import (
        TestCase,
        TestExecutionResult,
        TestExecutionResultDetail,
        TestSession,
        TestStep,
    )


def pytest_lamber_report_environment(config: Config) -> Optional[Dict]: ...


def pytest_lamber_sessionstart(
    session: TestSession, environment: Dict[str, str]
) -> None: ...


def pytest_lamber_sessionstop(
    session: TestSession, exitstatus: Union[int, ExitCode]
) -> None: ...


def pytest_lamber_log_test_cases(
    session: TestSession, test_cases: List[TestCase]
) -> None: ...


def pytest_lamber_log_test_case_start(test_case: TestCase) -> None: ...


def pytest_lamber_log_test_case_sourcecode(
    test_case: TestCase, sourcecode: str
) -> None: ...


def pytest_lamber_log_test_case_stop(
    test_case: TestCase,
    result: TestExecutionResult,
    result_detail: Optional[TestExecutionResultDetail],
) -> None: ...


def pytest_lamber_log_test_step_start(
    test_step: TestStep, parent: Union[TestCase, TestStep]
) -> None: ...


def pytest_lamber_log_test_step_stop(
    test_step: TestStep,
    result: TestExecutionResult,
    result_detail: Optional[TestExecutionResultDetail],
) -> None: ...


def pytest_lamber_log_test_case_logs(
    test_case: TestCase,
    caplog: str,
    capstderr: str,
    capstdout: str,
) -> None: ...


def pytest_lamber_log_test_case_result(
    test_case: TestCase,
    result: TestExecutionResult,
    result_detail: Optional[TestExecutionResultDetail],
) -> None: ...
