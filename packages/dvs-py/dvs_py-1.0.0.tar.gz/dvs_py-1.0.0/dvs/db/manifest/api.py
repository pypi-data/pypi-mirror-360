# dvs/db/manifest/api.py
import logging
import typing

import duckdb

import dvs
import dvs.utils.openapi as openapi_utils
from dvs.types.manifest import Manifest as ManifestType
from dvs.utils.display import DISPLAY_SQL_PARAMS, DISPLAY_SQL_QUERY
from dvs.utils.timer import Timer

logger = logging.getLogger(__name__)


class Manifest:
    def __init__(self, dvs: "dvs.DVS"):
        self.dvs = dvs

    def touch(self, *, verbose: bool | None = None) -> bool:
        """
        Create the manifest table if it does not exist.
        Returns True when table creation is completed successfully.
        """
        verbose = self.dvs.verbose if verbose is None else verbose

        with Timer() as timer:
            self._touch(verbose=verbose)

        if verbose:
            dur = timer.duration * 1000
            logger.debug(f"Created table: '{dvs.MANIFEST_TABLE_NAME}' in {dur:.3f} ms")

        return True

    def receive(self, *, verbose: bool | None = None) -> ManifestType | None:
        """
        Retrieve the manifest from the DuckDB database.
        Returns None if no manifest record exists.
        """
        verbose = self.dvs.verbose if verbose is None else verbose

        with Timer() as timer:
            out = self._receive(verbose=verbose)

        if verbose:
            dur = timer.duration * 1000
            logger.debug(f"Retrieved manifest in {dur:.3f} ms")

        return out

    def create(
        self, manifest: ManifestType, *, verbose: bool | None = None
    ) -> ManifestType:
        """
        Insert a new manifest record into the DuckDB database.
        Returns the created manifest instance.
        """
        verbose = self.dvs.verbose if verbose is None else verbose

        with Timer() as timer:
            out = self._create(manifest, verbose=verbose)

        if verbose:
            dur = timer.duration * 1000
            logger.debug(f"Created manifest in {dur:.3f} ms")

        return out

    def drop(self, *, verbose: bool | None = None) -> bool:
        """
        Drop the manifest table and all its data.
        This operation is irreversible.
        """
        verbose = self.dvs.verbose if verbose is None else verbose

        with Timer() as timer:
            self._drop(verbose=verbose)

        if verbose:
            dur = timer.duration * 1000
            logger.debug(f"Dropped table: '{dvs.MANIFEST_TABLE_NAME}' in {dur:.3f} ms")

        return True

    def _touch(self, *, verbose: bool | None = None) -> bool:
        """
        Internal method to create the manifest table if it does not exist.
        Handles table creation SQL generation and execution.
        """
        create_table_sql = openapi_utils.openapi_to_create_table_sql(
            ManifestType.model_json_schema(), table_name=dvs.MANIFEST_TABLE_NAME
        ).strip()

        if verbose:
            self.dvs.settings.console.print(
                f"\nCreating table: '{dvs.MANIFEST_TABLE_NAME}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=create_table_sql)}\n"
            )

        try:
            self.dvs.conn.sql(create_table_sql)
        except duckdb.CatalogException as e:
            if "already exists" in str(e).lower():
                logger.debug(f"Table '{dvs.MANIFEST_TABLE_NAME}' already exists")
            else:
                raise e

        return True

    def _receive(self, *, verbose: bool | None = None) -> ManifestType | None:
        """
        Internal method to retrieve the manifest from the DuckDB database.
        Executes SELECT query and validates the result as ManifestType.
        """
        columns = list(ManifestType.model_json_schema()["properties"].keys())
        columns_expr = ",".join(columns)

        query = f"SELECT {columns_expr} FROM {dvs.MANIFEST_TABLE_NAME}"

        if verbose:
            self.dvs.settings.console.print(
                "\nRetrieving manifest with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
            )

        result = self.dvs.conn.execute(query).fetchone()

        if result is None:
            return None

        data = dict(zip(columns, result))
        manifest = ManifestType.model_validate(data)

        return manifest

    def _create(
        self, manifest: ManifestType, *, verbose: bool | None = None
    ) -> ManifestType:
        """
        Internal method to insert a manifest record into the DuckDB database.
        Executes INSERT query with manifest data as parameters.
        """
        columns = list(manifest.model_json_schema()["properties"].keys())
        columns_expr = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        parameters: typing.List[typing.Tuple[typing.Any, ...]] = [
            tuple(getattr(manifest, c) for c in columns)
        ]

        query = (
            f"INSERT INTO {dvs.MANIFEST_TABLE_NAME} ({columns_expr}) "
            + f"VALUES ({placeholders})"
        )

        if verbose:
            self.dvs.settings.console.print(
                "\nCreating manifest with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
                + f"{DISPLAY_SQL_PARAMS.format(params=parameters)}\n"
            )

        self.dvs.conn.executemany(query, parameters)

        return manifest

    def _drop(self, *, verbose: bool | None = None) -> None:
        """
        Internal method to drop the manifest table.
        """
        query = f"DROP TABLE IF EXISTS {dvs.MANIFEST_TABLE_NAME}"

        if verbose:
            self.dvs.settings.console.print(
                f"\nDropping table: '{dvs.MANIFEST_TABLE_NAME}' with SQL:\n"
                + f"{DISPLAY_SQL_QUERY.format(sql=query)}\n"
            )

        self.dvs.conn.execute(query)
