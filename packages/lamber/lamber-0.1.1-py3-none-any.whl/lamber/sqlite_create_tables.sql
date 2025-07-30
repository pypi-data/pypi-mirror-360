BEGIN;

CREATE TABLE
    IF NOT EXISTS lamber_host (
        ip INTEGER PRIMARY KEY,
        hostname VARCHAR(128),
        create_time REAL DEFAULT (unixepoch ('subsec')),
        last_run_time REAL
    );

CREATE TABLE
    IF NOT EXISTS lamber_project (
        id INTEGER PRIMARY KEY,
        project_name VARCHAR(128) NOT NULL,
        create_time REAL DEFAULT (unixepoch ('subsec')),
        last_run_time REAL
    );

CREATE TABLE
    IF NOT EXISTS lamber_session (
        uuid VARCHAR(32) PRIMARY KEY,
        start_time REAL,
        stop_time REAL,
        host_ip INTEGER,
        project_id INTEGER,
        environment BLOB,
        duration REAL GENERATED ALWAYS AS (stop_time - start_time) VIRTUAL,
        FOREIGN KEY (host_ip) REFERENCES lamber_host (ip) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY (project_id) REFERENCES lamber_project (id) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS lamber_testcase (
        uuid VARCHAR(32) PRIMARY KEY,
        start_time REAL,
        stop_time REAL,
        nodeid VARCHAR(1024),
        marker BLOB,
        sourcecode TEXT,
        result VARCHAR(10),
        result_detail BLOB,
        pytest_caplog TEXT,
        pytest_capstderr TEXT,
        pytest_capstdout TEXT,
        session_uuid VARCHAR(32),
        duration REAL GENERATED ALWAYS AS (stop_time - start_time) VIRTUAL,
        FOREIGN KEY (session_uuid) REFERENCES lamber_session (uuid) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS lamber_teststep (
        uuid VARCHAR(32) PRIMARY KEY,
        start_time REAL,
        stop_time REAL,
        title VARCHAR(1024) NOT NULL,
        when_ VARCHAR(10) CHECK (when_ IN ('setup', 'call', 'teardown')),
        scope VARCHAR(10) CHECK (
            scope IN (
                'function',
                'class',
                'module',
                'package',
                'session'
            )
        ),
        result VARCHAR(10),
        result_detail BLOB,
        testcase_uuid VARCHAR(32),
        parent_uuid VARCHAR(32),
        duration REAL GENERATED ALWAYS AS (stop_time - start_time) VIRTUAL,
        FOREIGN KEY (testcase_uuid) REFERENCES lamber_testcase (uuid) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (parent_uuid) REFERENCES lamber_teststep (uuid) ON DELETE CASCADE ON UPDATE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS lamber_attachment (
        uuid VARCHAR(32) PRIMARY KEY,
        name VARCHAR(128),
        content_type VARCHAR(32),
        content_value,
        create_time REAL DEFAULT (unixepoch ('subsec')),
        testcase_uuid VARCHAR(32),
        FOREIGN KEY (testcase_uuid) REFERENCES lamber_testcase (uuid) ON DELETE CASCADE ON UPDATE CASCADE
    );

COMMIT;
