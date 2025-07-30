from __future__ import annotations

import json
import signal
import sqlite3
from datetime import datetime
from ipaddress import IPv4Address
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from typing import TYPE_CHECKING

import pytest

from lamber.models import AttachmentType, TestCase, TestStep

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Union

    from _pytest.config import Config

    from lamber.models import (
        TestExecutionResult,
        TestExecutionResultDetail,
        TestSession,
    )

sqlite3.register_adapter(datetime, lambda value: value.timestamp())


class SqlitePlugin:
    def __init__(self, config: Config):
        self.path: Path = config.getoption("lamber_sqlite_dir")

        assert self.path.is_dir(), "`--lamber-sqlite-dir` isn't an directory."

        self.path = self.path / "lamber.db"

        self.queue = Queue()
        self.event = Event()

        self._thread = _Thread(self.path, self.queue, self.event)

    def pytest_lamber_report_environment(self, config: Config) -> dict:
        return {"_sqlite": str(self.path.resolve())}

    def pytest_lamber_sessionstart(
        self, session: TestSession, environment: Dict[str, str]
    ):
        def _handler(signum: int, _):
            self.queue.put(
                (
                    "execute",
                    """
                    UPDATE lamber_session
                    SET
                        stop_time = ?
                    WHERE
                        uuid = ?;
                    """,
                    (datetime.now(), session.id_hex),
                    True,
                )
            )

            raise pytest.exit(
                f"Interrupted by signal {signum}", pytest.ExitCode.INTERRUPTED
            )

        signal.signal(signal.SIGTERM, _handler)

        self._thread.start()

        self.queue.put(
            (
                "execute",
                """
                INSERT INTO
                    lamber_project (id, project_name)
                VALUES
                    (?, ?) ON CONFLICT (id) DO NOTHING;
                """,
                (session.project_id, session.project),
                False,
            )
        )

        int_ip: Optional[int] = None
        if "_ip" in environment:
            try:
                int_ip = int(IPv4Address(environment["_ip"]))
            except ValueError:
                pass
            else:
                hostname = environment.get("_hostname", None)
                self.queue.put(
                    (
                        "execute",
                        """
                        INSERT INTO
                            lamber_host (ip, hostname)
                        VALUES
                            (?, ?) ON CONFLICT (ip) DO NOTHING;
                        """,
                        (int_ip, hostname),
                        False,
                    )
                )
                self.queue.put(
                    (
                        "execute",
                        """
                        UPDATE lamber_host
                        SET
                            last_run_time = ?
                        WHERE
                            ip = ?;
                        """,
                        (session.start_time, int_ip),
                        False,
                    )
                )

        self.queue.put(
            (
                "execute",
                """
                INSERT INTO
                    lamber_session (
                        uuid,
                        start_time,
                        host_ip,
                        project_id,
                        environment
                    )
                VALUES
                    (?, ?, ?, ?, jsonb (?));
                """,
                (
                    session.id_hex,
                    session.start_time,
                    int_ip,
                    session.project_id,
                    json.dumps(
                        {
                            key: val
                            for key, val in environment.items()
                            if key not in ("_ip", "_hostname")
                        }
                    ),
                ),
                False,
            )
        )

        self.queue.put(
            (
                "execute",
                """
                UPDATE lamber_project
                SET
                    last_run_time = ?
                WHERE
                    id = ?;
                """,
                (session.start_time, session.project_id),
                True,
            )
        )

    def pytest_lamber_sessionstop(self, session: TestSession) -> None:
        self.queue.put(
            (
                "execute",
                """
                UPDATE lamber_session
                SET
                    stop_time = ?
                WHERE
                    uuid = ?;
                """,
                (session.stop_time, session.id_hex),
                True,
            )
        )

    def pytest_lamber_log_test_cases(
        self, session: TestSession, test_cases: List[TestCase]
    ) -> None:
        if test_cases:
            self.queue.put(
                (
                    "executemany",
                    """
                    INSERT INTO
                        lamber_testcase (uuid, nodeid, session_uuid, marker)
                    VALUES
                        (?, ?, ?, json (?));
                    """,
                    [
                        (
                            test_case.id_hex,
                            test_case.nodeid,
                            session.id_hex,
                            test_case.marker and json.dumps(test_case.marker) or None,
                        )
                        for test_case in test_cases
                    ],
                    True,
                )
            )

    def pytest_lamber_log_test_case_start(self, test_case: TestCase) -> None:
        self.queue.put(
            (
                "execute",
                """
                UPDATE lamber_testcase
                SET
                    start_time = ?
                WHERE
                    uuid = ?;
                """,
                (test_case.start_time, test_case.id_hex),
                True,
            )
        )

    def pytest_lamber_log_test_case_sourcecode(
        self, test_case: TestCase, sourcecode: str
    ) -> None:
        if sourcecode:
            self.queue.put(
                (
                    "execute",
                    """
                    UPDATE lamber_testcase
                    SET
                        sourcecode = ?
                    WHERE
                        uuid = ?;
                    """,
                    (test_case.sourcecode, test_case.id_hex),
                    True,
                )
            )

    @pytest.hookimpl(trylast=True)
    def pytest_lamber_log_test_case_stop(
        self,
        test_case: TestCase,
        result: TestExecutionResult,
        result_detail: Optional[TestExecutionResultDetail],
    ) -> None:
        self.queue.put(
            (
                "execute",
                """
                UPDATE lamber_testcase
                SET
                    stop_time = ?, result = ?, result_detail = jsonb(?)
                WHERE
                    uuid = ?;
                """,
                (
                    test_case.stop_time,
                    result.name,
                    result_detail and json.dumps(result_detail) or None,
                    test_case.id_hex,
                ),
                True,
            )
        )

        if test_case.attachments:
            self.queue.put(
                (
                    "executemany",
                    """
                    INSERT INTO
                        lamber_attachment (
                            uuid,
                            name,
                            content_type,
                            content_value,
                            create_time,
                            testcase_uuid
                        )
                    VALUES
                        (?, ?, json (?), ?, ?, ?);
                    """,
                    [
                        (
                            attachment.id.hex,
                            attachment.name,
                            json.dumps(
                                attachment.content_type,
                                default=lambda obj: isinstance(obj, AttachmentType)
                                and (obj.mime_type, obj.extension)
                                or obj,
                            ),
                            attachment.content_value,
                            attachment.create_time,
                            test_case.id_hex,
                        )
                        for attachment in test_case.attachments.values()
                    ],
                    True,
                )
            )

    def pytest_lamber_log_test_step_start(
        self, test_step: TestStep, parent: Union[TestCase, TestStep]
    ) -> None:
        parent_uuid: Optional[bytes] = None
        testcase_uuid: Optional[bytes] = None

        if isinstance(parent, TestCase):
            testcase_uuid = parent.id_hex
        elif isinstance(parent, TestStep):
            parent_uuid = parent.id_hex

        self.queue.put(
            (
                "execute",
                """
                INSERT INTO
                    lamber_teststep (
                        uuid,
                        start_time,
                        title,
                        scope,
                        when_,
                        testcase_uuid,
                        parent_uuid
                    )
                VALUES
                    (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    test_step.id_hex,
                    test_step.start_time,
                    test_step.title,
                    test_step.scope,
                    test_step.when,
                    testcase_uuid,
                    parent_uuid,
                ),
                True,
            )
        )

    def pytest_lamber_log_test_step_stop(
        self,
        test_step: TestStep,
        result: TestExecutionResult,
        result_detail: Optional[TestExecutionResultDetail],
    ) -> None:
        self.queue.put(
            (
                "execute",
                """
                UPDATE lamber_teststep
                SET
                    stop_time = ?, result = ?, result_detail = jsonb(?)
                WHERE
                    uuid = ?;
                """,
                (
                    test_step.stop_time,
                    result.name,
                    result_detail and json.dumps(result_detail) or None,
                    test_step.id_hex,
                ),
                True,
            )
        )

    def pytest_lamber_log_test_case_logs(
        self,
        test_case: TestCase,
        caplog: str,
        capstderr: str,
        capstdout: str,
    ) -> None:
        self.queue.put(
            (
                "execute",
                """
                UPDATE lamber_testcase
                SET
                    pytest_caplog = ?, pytest_capstderr = ?, pytest_capstdout = ?
                WHERE
                    uuid = ?;
                """,
                (
                    caplog,
                    capstderr,
                    capstdout,
                    test_case.id_hex,
                ),
                True,
            )
        )

    def pytest_unconfigure(self):
        self.event.set()
        self._thread.join()


class _Thread(Thread):
    def __init__(self, path: Path, queue: Queue, event: Event):
        super().__init__(name="Lamber-Sqlite")

        self._path = path
        self._queue = queue
        self._event = event

        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

        self._sql_scripts: Dict[Path, str] = {}

    def _create_tables(self) -> None:
        self._exec_script(Path(__file__).parent / "sqlite_create_tables.sql")

    def _read_script(self, file: Path) -> str:
        result: Optional[str] = None

        with file.open() as _file:
            result = _file.read()

        return result

    def _exec_script(self, file: Path):
        self._cursor.executescript(
            self._sql_scripts.setdefault(file, self._read_script(file))
        )

    def run(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self._path)
            self._connection.execute("PRAGMA foreign_keys = ON")

        if self._cursor is None:
            self._cursor = self._connection.cursor()

        self._create_tables()

        while not (self._event.is_set() and self._queue.empty()):
            try:
                method, sql, args, commit = self._queue.get_nowait()
            except Empty:
                pass
            except ValueError:
                pass
            else:
                getattr(self._cursor, method)(sql, args)
                if commit:
                    self._connection.commit()

        self._connection.commit()
        self._connection.close()
