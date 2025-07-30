"""Test OracleDB driver implementation - Synchronous Tests."""

from __future__ import annotations

from typing import Any, Literal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from pytest_databases.docker.oracle import OracleService

from sqlspec.adapters.oracledb import OracleSyncConfig
from sqlspec.statement.result import SQLResult

ParamStyle = Literal["positional_binds", "dict_binds"]

# --- Sync Fixtures ---


@pytest.fixture
def oracle_sync_session(oracle_23ai_service: OracleService) -> OracleSyncConfig:
    """Create an Oracle synchronous session."""
    return OracleSyncConfig(
        host=oracle_23ai_service.host,
        port=oracle_23ai_service.port,
        service_name=oracle_23ai_service.service_name,
        user=oracle_23ai_service.user,
        password=oracle_23ai_service.password,
    )


# --- Sync Tests ---


@pytest.mark.parametrize(
    ("params", "style"),
    [
        pytest.param(("test_name",), "positional_binds", id="positional_binds"),
        pytest.param({"name": "test_name"}, "dict_binds", id="dict_binds"),
    ],
)
@pytest.mark.skip(
    reason="Oracle RETURNING INTO clause requires PL/SQL blocks with output bind variables, "
    "which is incompatible with the standard driver interface that expects result sets. "
    "Oracle does not support the standard RETURNING syntax used by PostgreSQL/SQLite."
)
@pytest.mark.xdist_group("oracle")
def test_sync_insert_returning(oracle_sync_session: OracleSyncConfig, params: Any, style: ParamStyle) -> None:
    """Test synchronous insert returning functionality with Oracle parameter styles.

    Note: This test is skipped because Oracle's RETURNING INTO clause works differently
    than other databases. It requires:
    1. PL/SQL block execution
    2. Output bind variables to capture returned values
    3. Cannot return result sets directly like PostgreSQL/SQLite

    Example of Oracle's syntax (requires PL/SQL):
    DECLARE
        v_id NUMBER;
        v_name VARCHAR2(50);
    BEGIN
        INSERT INTO test_table (id, name) VALUES (1, 'test')
        RETURNING id, name INTO v_id, v_name;
    END;
    """
    with oracle_sync_session.provide_session() as driver:
        sql = """
        CREATE TABLE test_table (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(50)
        )
        """
        driver.execute_script(sql)

        if style == "positional_binds":
            # This syntax is not valid in Oracle without PL/SQL block
            sql = "INSERT INTO test_table (id, name) VALUES (1, :1) RETURNING id, name"
            exec_params = params
        else:  # dict_binds
            # Workaround: Use positional binds due to DPY-4009
            sql = "INSERT INTO test_table (id, name) VALUES (1, :1) RETURNING id, name"
            exec_params = params["name"]

        # This would fail with Oracle error because RETURNING requires INTO clause
        result = driver.execute(sql, exec_params)
        assert isinstance(result, SQLResult)
        assert result.data is not None
        assert len(result.data) == 1
        # Oracle often returns column names in uppercase
        assert result.data[0]["NAME"] == "test_name"
        assert result.data[0]["ID"] is not None
        assert isinstance(result.data[0]["ID"], int)
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )


@pytest.mark.parametrize(
    ("params", "style"),
    [
        pytest.param(("test_name",), "positional_binds", id="positional_binds"),
        pytest.param({"name": "test_name"}, "dict_binds", id="dict_binds"),
    ],
)
@pytest.mark.xdist_group("oracle")
def test_sync_select(oracle_sync_session: OracleSyncConfig, params: Any, style: ParamStyle) -> None:
    """Test synchronous select functionality with Oracle parameter styles."""
    with oracle_sync_session.provide_session() as driver:
        # Manual cleanup at start of test
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )
        sql = """
        CREATE TABLE test_table (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(50)
        )
        """
        driver.execute_script(sql)

        if style == "positional_binds":
            insert_sql = "INSERT INTO test_table (id, name) VALUES (:id, :name)"
            select_sql = "SELECT name FROM test_table WHERE name = :name"
            insert_params = {"id": 1, "name": params[0]}
            select_params = {"name": params[0]}
        else:  # dict_binds
            insert_sql = "INSERT INTO test_table (id, name) VALUES (:id, :name)"
            select_sql = "SELECT name FROM test_table WHERE name = :name"
            insert_params = {"id": 1, **params}
            select_params = params

        insert_result = driver.execute(insert_sql, insert_params)
        assert isinstance(insert_result, SQLResult)
        assert insert_result.rows_affected == 1

        select_result = driver.execute(select_sql, select_params)
        assert isinstance(select_result, SQLResult)
        assert select_result.data is not None
        assert len(select_result.data) == 1
        assert select_result.data[0]["NAME"] == "test_name"
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )


@pytest.mark.parametrize(
    ("params", "style"),  # Keep parametrization for structure, even if params unused for select_value
    [
        pytest.param(("test_name",), "positional_binds", id="positional_binds"),
        pytest.param({"name": "test_name"}, "dict_binds", id="dict_binds"),
    ],
)
@pytest.mark.xdist_group("oracle")
def test_sync_select_value(oracle_sync_session: OracleSyncConfig, params: Any, style: ParamStyle) -> None:
    """Test synchronous select_value functionality with Oracle parameter styles."""
    with oracle_sync_session.provide_session() as driver:
        # Manual cleanup at start of test
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )
        sql = """
        CREATE TABLE test_table (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(50)
        )
        """
        driver.execute_script(sql)

        # Workaround: Use positional binds for setup insert due to DPY-4009 error with dict_binds
        if style == "positional_binds":
            setup_value = params[0]
        else:  # dict_binds
            setup_value = params["name"]
        insert_sql_setup = "INSERT INTO test_table (id, name) VALUES (:id, :name)"
        insert_result = driver.execute(insert_sql_setup, {"id": 1, "name": setup_value})
        assert isinstance(insert_result, SQLResult)
        assert insert_result.rows_affected == 1

        # Select a literal value using Oracle's DUAL table
        select_sql = "SELECT 'test_value' FROM dual"
        value_result = driver.execute(select_sql)
        assert isinstance(value_result, SQLResult)
        assert value_result.data is not None
        assert len(value_result.data) == 1
        assert value_result.column_names is not None
        value = value_result.data[0][value_result.column_names[0]]
        assert value == "test_value"
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )


@pytest.mark.xdist_group("oracle")
def test_sync_select_arrow(oracle_sync_session: OracleSyncConfig) -> None:
    """Test synchronous select_arrow functionality."""
    with oracle_sync_session.provide_session() as driver:
        # Manual cleanup at start of test
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )
        sql = """
        CREATE TABLE test_table (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(50)
        )
        """
        driver.execute_script(sql)

        # Insert test record using positional binds
        insert_sql = "INSERT INTO test_table (id, name) VALUES (1, :1)"
        insert_result = driver.execute(insert_sql, ("arrow_name"))
        assert isinstance(insert_result, SQLResult)
        assert insert_result.rows_affected == 1

        # Select and verify with Arrow support if available
        select_sql = "SELECT name, id FROM test_table WHERE name = :name"
        if hasattr(driver, "fetch_arrow_table"):
            arrow_result = driver.fetch_arrow_table(select_sql, {"name": "arrow_name"})
            assert hasattr(arrow_result, "data")
            arrow_table = arrow_result.data
            assert isinstance(arrow_table, pa.Table)
            assert arrow_table.num_rows == 1
            assert arrow_table.num_columns == 2
            # Oracle returns uppercase column names by default
            assert arrow_table.column_names == ["NAME", "ID"]
            assert arrow_table.column("NAME").to_pylist() == ["arrow_name"]
            # Check ID exists and is a number (exact value depends on IDENTITY)
            assert arrow_table.column("ID").to_pylist()[0] is not None
            assert isinstance(
                arrow_table.column("ID").to_pylist()[0], (int, float)
            )  # Oracle NUMBER maps to float/Decimal
        else:
            pytest.skip("Oracle driver does not support Arrow operations")
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )


@pytest.mark.xdist_group("oracle")
def test_sync_to_parquet(oracle_sync_session: OracleSyncConfig) -> None:
    """Integration test: to_parquet writes correct data to a Parquet file."""
    with oracle_sync_session.provide_session() as driver:
        # Manual cleanup at start of test
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )
        sql = """
        CREATE TABLE test_table (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(50)
        )
        """
        driver.execute_script(sql)
        # Insert test records
        driver.execute("INSERT INTO test_table (id, name) VALUES (:id, :name)", {"id": 1, "name": "pq1"})
        driver.execute("INSERT INTO test_table (id, name) VALUES (:id, :name)", {"id": 2, "name": "pq2"})
        statement = "SELECT name, id FROM test_table ORDER BY name"
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
            driver.export_to_storage(statement, destination_uri=tmp.name)  # type: ignore[attr-defined]
            table = pq.read_table(tmp.name)
            assert table.num_rows == 2
            assert set(table.column_names) == {"NAME", "ID"}
            names = table.column("NAME").to_pylist()
            assert "pq1" in names and "pq2" in names
        driver.execute_script(
            "BEGIN EXECUTE IMMEDIATE 'DROP TABLE test_table'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;"
        )


@pytest.mark.xdist_group("oracle")
def test_sync_insert_with_sequence(oracle_sync_session: OracleSyncConfig) -> None:
    """Test Oracle's alternative to RETURNING - using sequences and separate SELECT."""
    with oracle_sync_session.provide_session() as driver:
        # Create sequence and table
        driver.execute_script("""
            CREATE SEQUENCE test_seq START WITH 1 INCREMENT BY 1;
            CREATE TABLE test_table (
                id NUMBER PRIMARY KEY,
                name VARCHAR2(50)
            )
        """)

        # Insert using sequence
        driver.execute("INSERT INTO test_table (id, name) VALUES (test_seq.NEXTVAL, :1)", ("test_name"))

        # Get the last inserted ID using CURRVAL
        result = driver.execute("SELECT test_seq.CURRVAL as last_id FROM dual")
        assert isinstance(result, SQLResult)
        assert result.data is not None
        assert len(result.data) == 1
        last_id = result.data[0]["LAST_ID"]

        # Verify the inserted record
        verify_result = driver.execute("SELECT id, name FROM test_table WHERE id = :1", (last_id))
        assert isinstance(verify_result, SQLResult)
        assert verify_result.data is not None
        assert len(verify_result.data) == 1
        assert verify_result.data[0]["NAME"] == "test_name"
        assert verify_result.data[0]["ID"] == last_id

        # Cleanup
        driver.execute_script("""
            BEGIN
                EXECUTE IMMEDIATE 'DROP TABLE test_table';
                EXECUTE IMMEDIATE 'DROP SEQUENCE test_seq';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -942 THEN RAISE; END IF;
            END;
        """)


@pytest.mark.xdist_group("oracle")
def test_oracle_ddl_script_parsing(oracle_sync_session: OracleSyncConfig) -> None:
    """Test that the Oracle 23AI DDL script can be parsed and prepared for execution."""
    from pathlib import Path

    from sqlspec.statement.sql import SQL, SQLConfig

    # Load the Oracle DDL script
    fixture_path = Path(__file__).parent.parent.parent.parent / "fixtures" / "oracle.ddl.sql"
    assert fixture_path.exists(), f"Fixture file not found at {fixture_path}"

    with Path(fixture_path).open() as f:
        oracle_ddl = f.read()

    # Configure for Oracle dialect with parsing enabled
    config = SQLConfig(
        enable_parsing=True,
        enable_validation=False,  # Disable validation to focus on script handling
    )

    with oracle_sync_session.provide_session():
        # Test that the script can be processed as a SQL object
        stmt = SQL(oracle_ddl, config=config, dialect="oracle").as_script()

        # Verify it's recognized as a script
        assert stmt.is_script is True

        # Verify the SQL output contains key Oracle features
        sql_output = stmt.to_sql()
        assert "ALTER SESSION SET CONTAINER" in sql_output
        assert "CREATE TABLE" in sql_output
        assert "VECTOR(768, FLOAT32)" in sql_output
        assert "JSON" in sql_output
        assert "INMEMORY PRIORITY HIGH" in sql_output

        # Note: We don't actually execute the full DDL script in tests
        # as it requires specific Oracle setup and permissions.
        # The test verifies that the script can be parsed and prepared.
