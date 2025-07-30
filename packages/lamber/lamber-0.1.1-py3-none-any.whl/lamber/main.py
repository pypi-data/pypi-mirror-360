from __future__ import annotations

import sys
from inspect import getsource
from pathlib import Path
from platform import platform, python_version
from typing import TYPE_CHECKING, final

from _pytest._version import version as pytest_version
from pytest import hookimpl

from lamber import __version__ as lamber_version
from lamber.models import TestCase, TestSession, step
from lamber.utils import get_local_host

if TYPE_CHECKING:
    from typing import Any, Generator, List, Optional, Tuple, Union

    from _pytest import nodes
    from _pytest.config.argparsing import OptionGroup, Parser
    from _pytest.fixtures import FixtureDef, SubRequest
    from _pytest.python import Function
    from _pytest.reports import TestReport
    from _pytest.runner import CallInfo
    from pytest import Config, ExitCode, PytestPluginManager


def pytest_addoption(parser: Parser) -> None:
    """Register argparse-style options, called once at the beginning of a testrun.

    Args:
        parser (Parser): Parser for command line arguments.
    """
    group: OptionGroup = parser.getgroup("lamber")

    group.addoption(
        "--lamber-project",
        action="store",
        default="Lamber",
        type=str,
        dest="lamber_project",
        help="Project name.",
    )

    group.addoption(
        "--lamber-config-file",
        action="store",
        default=None,
        type=Path,
        dest="lamber_config_file",
        help="Lamber config file in TOML format.",
    )

    group.addoption(
        "--lamber-sqlite-dir",
        action="store",
        default=None,
        type=Path,
        dest="lamber_sqlite_dir",
        help="Lamber sqlite db path.",
    )
    group.addoption(
        "--lamber-ignore-fixture-step",
        action="store_true",
        dest="lamber_ignore_fixture_step",
        help="Doesn't wrap fixture to step.",
    )


def pytest_addhooks(pluginmanager: PytestPluginManager):
    from lamber import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_configure(config: Config) -> None:
    config.pluginmanager.register(Lamber(config))


@final
class Lamber:
    def __init__(self, config: Config):
        self.config = config

        self.test_session = TestSession(config)

        if config.getoption("lamber_sqlite_dir"):
            from lamber.sqlite import SqlitePlugin

            config.pluginmanager.register(SqlitePlugin(config), "lamber-sqlite")

    def pytest_sessionstart(self) -> None:
        for _env in self.config.hook.pytest_lamber_report_environment(
            config=self.config
        ):
            if isinstance(_env, dict):
                self.test_session.environment.update(_env)

        self.test_session.start()

        self.config.hook.pytest_lamber_sessionstart(
            session=self.test_session, environment=self.test_session.environment
        )

    @hookimpl(tryfirst=True)
    def pytest_lamber_report_environment(self, config: Config) -> dict:
        environment = {
            "_platform": platform(),
            "_python_version": python_version(),
            "_python_executable": sys.executable,
            "_pytest_version": pytest_version,
            "_pytest_rootdir": str(config.rootpath),
            "_lamber_version": lamber_version,
        }

        host = get_local_host()
        if isinstance(host, dict):
            environment.update(host)

        plugininfo = config.pluginmanager.list_plugin_distinfo()
        if plugininfo:
            plugins = {
                f"{dist.project_name}-{dist._dist.version}"
                for _, dist in plugininfo
                if dist.project_name != "lamber"
            }
            if plugins:
                environment.update({"_plugins": ", ".join(plugins)})

        return environment

    def pytest_sessionfinish(self, exitstatus: Union[int, ExitCode]) -> None:
        self.test_session.stop()

        self.config.hook.pytest_lamber_sessionstop(
            session=self.test_session, exitstatus=exitstatus
        )

    @hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, items: List[nodes.Node]):
        self.test_session.test_cases = {item.nodeid: TestCase(item) for item in items}

        self.config.hook.pytest_lamber_log_test_cases(
            session=self.test_session,
            test_cases=[
                test_case for test_case in self.test_session.test_cases.values()
            ],
        )

    def pytest_runtest_logstart(
        self, nodeid: str, location: Tuple[str, Optional[int], str]
    ):
        self.test_session.current_test_case = self.test_session.test_cases[nodeid]
        self.test_session.current_test_case.title = location[2]

        self.test_session.current_test_exec = self.test_session.current_test_case
        self.test_session.current_test_exec.start()

        self.config.hook.pytest_lamber_log_test_case_start(
            test_case=self.test_session.current_test_exec
        )

    def pytest_runtest_logfinish(self):
        self.test_session.current_test_exec = self.test_session.current_test_case
        self.test_session.current_test_exec.stop()

        self.config.hook.pytest_lamber_log_test_case_stop(
            test_case=self.test_session.current_test_exec,
            result=self.test_session.current_test_exec.result,
            result_detail=self.test_session.current_test_exec.result_detail,
        )

    @hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self) -> Generator[None, None, None]:
        self.test_session.current_test_exec = self.test_session.current_test_case
        self.test_session.current_test_exec.when = "setup"

        try:
            yield
        finally:
            self.test_session.current_test_exec = self.test_session.current_test_case

    @hookimpl(tryfirst=True)
    def pytest_fixture_setup(
        self, fixturedef: FixtureDef[Any], request: SubRequest
    ) -> None:
        if hasattr(request, "param"):
            return

        if not (
            self.config.getoption("lamber_ignore_fixture_step")
            or hasattr(fixturedef, "_lamber_wrapped")
        ):
            self.test_session.current_test_case.sourcecodes.add(
                getsource(fixturedef.func)
            )
            fixturedef.func = step(fixturedef.argname, scope=fixturedef.scope)(
                fixturedef.func
            )

            setattr(fixturedef, "_lamber_wrapped", True)

        setattr(request.node, "_lamber_test_case", self.test_session.current_test_case)

    @hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self) -> Generator[None, None, None]:
        self.test_session.current_test_exec = self.test_session.current_test_case
        self.test_session.current_test_exec.when = "teardown"

        try:
            yield
        finally:
            self.test_session.current_test_exec = self.test_session.current_test_case

    @hookimpl(wrapper=True)
    def pytest_runtest_call(self) -> Generator[None, None, None]:
        self.test_session.current_test_exec = self.test_session.current_test_case
        self.test_session.current_test_exec.when = "call"

        try:
            yield
        finally:
            self.test_session.current_test_exec = self.test_session.current_test_case

    @hookimpl(wrapper=True)
    def pytest_pyfunc_call(self, pyfuncitem: Function) -> Generator[None, None, None]:
        self.test_session.current_test_exec = self.test_session.current_test_case
        self.test_session.current_test_case.sourcecodes.add(getsource(pyfuncitem.obj))

        self.config.hook.pytest_lamber_log_test_case_sourcecode(
            test_case=self.test_session.current_test_case,
            sourcecode=self.test_session.current_test_case.sourcecode,
        )

        pyfuncitem.obj = step("call", when="call")(pyfuncitem.obj)

        yield

    @hookimpl(wrapper=True)
    def pytest_runtest_makereport(
        self, call: CallInfo[None]
    ) -> Generator[None, TestReport, TestReport]:
        report: TestReport = yield

        self.test_session.current_test_exec.update_result_from_pytest_report(
            report, call
        )

        return report

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        if report.when == "teardown":
            self.test_session.current_test_exec.caplog = report.caplog
            self.test_session.current_test_exec.capstderr = report.capstderr
            self.test_session.current_test_exec.capstdout = report.capstdout

            self.config.hook.pytest_lamber_log_test_case_logs(
                test_case=self.test_session.current_test_case,
                caplog=self.test_session.current_test_case.caplog,
                capstderr=self.test_session.current_test_case.capstderr,
                capstdout=self.test_session.current_test_case.capstdout,
            )

            self.config.hook.pytest_lamber_log_test_case_result(
                test_case=self.test_session.current_test_case,
                result=self.test_session.current_test_case.result,
                result_detail=self.test_session.current_test_case.result_detail,
            )
