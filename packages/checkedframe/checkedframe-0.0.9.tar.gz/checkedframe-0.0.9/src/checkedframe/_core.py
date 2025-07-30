from __future__ import annotations

import copy
import dataclasses
import string
from typing import Any, Optional

import narwhals.stable.v1 as nw
import narwhals.stable.v1.typing as nwt

from ._checks import Check, CheckInputType
from ._dtypes import CastError, _Column, _nw_type_to_cf_type, _TypedColumn
from ._utils import get_class_members
from .exceptions import SchemaError
from .selectors import Selector


@dataclasses.dataclass
class _ResultWrapper:
    res: Any
    msg: str
    identifier: str
    column: str
    operation: str
    native: bool = False
    is_expr: bool = False


def _run_check(
    check: Check,
    check_name: str,
    nw_df: nw.DataFrame,
    series_name: Optional[str] = None,
):
    """_summary_

    Parameters
    ----------
    check : Check
        _description_
    nw_df : nw.DataFrame
        _description_
    check_name : str
        _description_
    check_input_type : CheckInputType
        _description_
    series_name : Optional[str], optional
        , by default None

    Returns
    -------
    bool | int
        Returns either a boolean that is True when the check passes or an integer
        representing the number of rows that fail the check.

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    """
    assert check.func is not None

    new_check_name = (
        f"__checkedframe_{'' if series_name is None else series_name}_{check_name}__"
    )
    column_name = "__dataframe__" if series_name is None else series_name

    err_msg = string.Template(
        "${check_name} failed for {summary} rows: ${check_description}"
    ).safe_substitute(
        {"check_name": check_name, "check_description": check.description}
    )

    if check.return_type == "Expr":
        if check.input_type == "str":
            expr = check.func(series_name).alias(new_check_name)
        else:
            expr = check.func().alias(new_check_name)

        assert isinstance(check.native, bool)

        return _ResultWrapper(
            expr,
            msg=err_msg,
            identifier=new_check_name,
            column=column_name,
            operation=check_name,
            native=check.native,
            is_expr=True,
        )
    else:
        if check.input_type == "Series":
            if series_name is None:
                raise ValueError(
                    "Series cannot be automatically determined in this context"
                )

            input_ = nw_df[series_name]
        elif check.input_type == "Frame":
            # mypy complains here that the input type is Series, not DataFrame, but it
            # is only a Series if the above branch is hit, which means this branch is
            # not

            input_ = nw_df  # type: ignore[assignment]
        else:
            raise ValueError("Invalid input type")

        if check.native:
            input_ = input_.to_native()

        res = check.func(input_)

        if check.return_type == "Series":
            res = nw.from_native(res, series_only=True).alias(new_check_name)
            return _ResultWrapper(
                res,
                msg=err_msg,
                identifier=new_check_name,
                column=column_name,
                operation=check_name,
                native=False,
                is_expr=False,
            )
        elif check.return_type == "bool":
            res = nw.lit(res).alias(new_check_name)
            return _ResultWrapper(
                res,
                msg=err_msg,
                identifier=new_check_name,
                column=column_name,
                operation=check_name,
                native=False,
                is_expr=True,
            )


@dataclasses.dataclass
class _PrivateInterrogationResult:
    df: nw.DataFrame
    mask: nw.DataFrame
    is_good: nw.Series
    summary: nw.DataFrame


@dataclasses.dataclass
class InterrogationResult:
    df: nwt.IntoDataFrame
    mask: nwt.IntoDataFrame
    is_good: nwt.IntoSeries
    summary: nwt.IntoDataFrame


def _private_interrogate(
    schema: Schema, df: nwt.IntoDataFrameT, cast: bool
) -> _PrivateInterrogationResult:
    nw_df = nw.from_native(df, eager_only=True)
    df_schema = nw_df.collect_schema()  # type: ignore[attribute]

    results: list[_ResultWrapper] = []
    for expected_name, expected_col in schema.expected_schema.items():
        # Check existence. There are three possible states:
        # 1. The column exists
        # 2. The column exists but is not required
        # 3. The column exists but is required
        #
        # If the column exists but is not required, the check shouldn't error, but we
        # can't perform any of the next steps like casting or checks, so we have to skip
        # them.
        check_name = f"__checkedframe_{expected_name}_existence__"
        existence_message = ""
        if expected_name in df_schema:
            actually_exists = True
            existence_check = nw.lit(True)
        else:
            actually_exists = False
            if expected_col.required:
                existence_check = nw.lit(False)
                existence_message = "Column marked as required but not found"
            else:
                existence_check = nw.lit(True)

        results.append(
            _ResultWrapper(
                existence_check.alias(check_name),
                msg=existence_message,
                identifier=check_name,
                column=expected_name,
                operation="existence",
                native=False,
                is_expr=True,
            )
        )

        if not actually_exists:
            continue

        # check data types
        actual_dtype = df_schema[expected_name]
        if actual_dtype == expected_col.to_narwhals():
            pass
        else:
            if expected_col.cast or cast:
                try:
                    nw_df = nw_df.with_columns(
                        _nw_type_to_cf_type(actual_dtype)._safe_cast(
                            nw_df[expected_name], expected_col
                        )
                    )
                except CastError as e:
                    identifier = f"__checkedframe_{expected_name}_cast__"

                    results.append(
                        _ResultWrapper(
                            e.element_passes.alias(identifier),
                            msg=e.msg,
                            identifier=identifier,
                            column=expected_name,
                            operation="cast",
                            native=False,
                            is_expr=isinstance(e.element_passes, nw.Expr),
                        )
                    )
                    continue
            else:
                identifier = f"__checkedframe_{expected_name}_dtype__"
                results.append(
                    _ResultWrapper(
                        nw.lit(False).alias(identifier),
                        msg=f"Expected {expected_col}, got {actual_dtype}",
                        identifier=identifier,
                        column=expected_name,
                        operation="dtype",
                        native=False,
                        is_expr=False,
                    )
                )
                continue

        # nullable / nanable checks
        builtin_checks = []

        if not expected_col.nullable:
            builtin_checks.append(Check.is_not_null())

        if hasattr(expected_col, "allow_nan") and not expected_col.allow_nan:
            builtin_checks.append(Check.is_not_nan())

        if hasattr(expected_col, "allow_inf") and not expected_col.allow_inf:
            builtin_checks.append(Check.is_not_inf())

        for check in builtin_checks:
            assert check.name is not None

            results.append(
                _run_check(
                    check=check,
                    check_name=check.name,
                    nw_df=nw_df,
                    series_name=expected_name,
                )
            )

        # user checks
        for i, check in enumerate(expected_col.checks):
            check_name = f"check_{i}" if check.name is None else check.name

            result = _run_check(
                check,
                check_name,
                nw_df,
                series_name=expected_name,
            )

            results.append(result)

    for i, check in enumerate(schema.checks):
        check_name = f"frame_check_{i}" if check.name is None else check.name

        result = _run_check(check, check_name, nw_df)
        results.append(result)

    native_exprs = []
    exprs = []
    series_store = []
    id_col_mapper = {}
    id_op_mapper = {}
    id_msg_mapper = {}
    for result in results:
        id_op_mapper[result.identifier] = result.operation
        id_col_mapper[result.identifier] = result.column
        id_msg_mapper[result.identifier] = result.msg

        res = result.res
        if result.is_expr:
            if result.native:
                native_exprs.append(res)
            else:
                exprs.append(res)
        else:
            series_store.append(res)

    temp_index_col = "__checkedframe_temporary_index_s;dlfjks;dflkj__"
    check_df = (
        nw_df.lazy()
        .with_row_index(temp_index_col)
        .select(temp_index_col, *exprs)
        .drop(temp_index_col)
        .collect()
    )
    check_df_native = nw.from_native(nw_df.to_native().lazy().select(*native_exprs).collect())  # type: ignore

    check_df_all = nw.concat(
        [check_df, check_df_native], how="horizontal"
    ).with_columns(*series_store)

    n_rows = nw_df.shape[0]

    is_good = check_df_all.select(nw.all_horizontal(nw.all()).alias("is_good"))[
        "is_good"
    ]

    summary_df = (
        check_df_all.lazy()
        .select(nw.all().__invert__().sum())
        .unpivot(variable_name="id", value_name="n_failed")
        .with_columns(
            nw.col("n_failed").__truediv__(n_rows).alias("pct_failed"),
            nw.col("id").replace_strict(id_col_mapper).alias("column"),
            nw.col("id").replace_strict(id_op_mapper).alias("operation"),
            nw.col("id").replace_strict(id_msg_mapper).alias("message"),
        )
        .drop("id")
        .collect()
    )

    return _PrivateInterrogationResult(
        df=nw_df,
        mask=check_df_all,  # type: ignore
        is_good=is_good,  # type: ignore
        summary=summary_df,  # type: ignore
    )


def _interrogate(
    schema: Schema, df: nwt.IntoDataFrameT, cast: bool
) -> InterrogationResult:
    res = _private_interrogate(schema=schema, df=df, cast=cast)

    return InterrogationResult(
        df=res.df.to_native(),
        mask=res.mask.to_native(),
        is_good=res.is_good.to_native(),
        summary=res.summary.select(
            "column", "operation", "n_failed", "pct_failed"
        ).to_native(),
    )


def _filter(schema: Schema, df: nwt.IntoDataFrameT, cast: bool) -> nwt.IntoDataFrameT:
    res = _private_interrogate(schema=schema, df=df, cast=cast)

    return res.df.filter(res.is_good).to_native()


def _generate_error_message(
    summary_df: nwt.IntoDataFrame, columns: list[str], n_rows: int
) -> str:
    failures = (
        nw.from_native(summary_df, eager_only=True)
        .filter(nw.col("n_failed").__gt__(0))
        .with_columns(
            nw.len().over("column").alias("error_count"),
            nw.col("column").__ne__("__dataframe__").alias("is_column_check"),
        )
    )

    column_failures = failures.filter(nw.col("is_column_check"))
    frame_failures = failures.filter(nw.col("is_column_check").__invert__())
    total_error_count = failures.shape[0]

    n_rows_str = f"{n_rows:,}"

    def _wrap_err(e: str) -> str:
        return f"    - {e}"

    relevant_info = ["message", "n_failed", "pct_failed", "error_count"]
    output = []
    for column in columns:
        bullets: list[str] = []

        tmp = column_failures.filter(nw.col("column") == column)

        if tmp.is_empty():
            continue

        for (
            message,
            n_failed,
            pct_failed,
            error_count,
        ) in tmp.select(
            relevant_info
        ).iter_rows(named=False):

            summary = f"{n_failed:,} / {n_rows_str} ({pct_failed:.2%})"
            message = message.format(summary=summary)
            bullets.append(_wrap_err(message))

        output.append(f"  {column}: {error_count} error(s)")
        output.extend(bullets)

    for message, n_failed, pct_failed, error_count in frame_failures.select(
        relevant_info
    ).iter_rows(named=False):
        summary = f"{n_failed:,} / {n_rows_str} ({pct_failed:.2%})"
        message = message.format(summary=summary)
        output.append(f"  * {message}")

    error_summary = [f"Found {total_error_count} error(s)"]

    return "\n".join(error_summary + output)


def _validate(schema: Schema, df: nwt.IntoDataFrameT, cast: bool) -> nwt.IntoDataFrameT:
    res = _private_interrogate(schema, df, cast)

    if not res.is_good.all():
        raise SchemaError(
            _generate_error_message(
                summary_df=res.summary, columns=schema.columns(), n_rows=res.df.shape[0]
            )
        )

    return res.df.to_native()


class _SchemaCacheMeta(type):
    def __new__(cls, name, bases, namespace):
        new_class = super().__new__(cls, name, bases, namespace)
        new_class._schema = None

        return new_class


class Schema(metaclass=_SchemaCacheMeta):
    """A lightweight schema representing a DataFrame. Briefly, a schema consists of
    columns and their associated data types. In addition, the schema stores checks that
    can be run either on a specific column or the entire DataFrame. Since `checkedframe`
    leverages `narwhals`, any Narwhals-compatible DataFrame (Pandas, Polars, Modin,
    PyArrow, cuDF) is valid.

    A Schema can be used in two ways. It can either be initialized directly from a
    dictionary or inherited from in a class.

    Parameters
    ----------
    expected_schema : dict[str, Column]
        A dictionary of column names and data types
    checks : Optional[Sequence[Check]], optional
        A list of checks to run, by default None

    Examples
    --------
    Let's say we have a Polars DataFrame we want to validate. We have one column, a
    string, that should be 3 characters.

    .. code-block:: python

        import polars as pl

        df = pl.DataFrame({"col1": ["abc", "ef"]})

    Via inheritance:

    .. code-block:: python

        import checkedframe as cf

        class MySchema(cf.Schema):
            col1 = cf.String()

            @cf.Check(columns="col1")
            def check_length(s: pl.Series) -> pl.Series:
                return s.str.len_bytes() == 3

        MySchema.validate(df)

    Via explicit construction:

    .. code-block:: python

        import checkedframe as cf

        MySchema = cf.Schema({
            "col1": cf.String(
                checks=[cf.Check(lambda s: s.str.len_bytes() == 3)]
            )
        })

        MySchema.validate(df)
    """

    _schema: Optional[Schema]

    def __init__(
        self,
        expected_schema: dict[str, _TypedColumn],
        checks: Optional[list[Check]] = None,
    ):
        self.expected_schema = expected_schema
        self.checks = [] if checks is None else checks
        self.interrogate = self.__interrogate  # type: ignore
        self.validate = self.__validate  # type: ignore
        self.filter = self.__filter  # type: ignore
        self.columns = self.__columns  # type: ignore

    @classmethod
    def columns(cls) -> list[str]:
        if cls._schema is None:
            cls._schema = cls._parse_into_schema()

        return list(cls._schema.expected_schema.keys())

    def __columns(self) -> list[str]:
        return list(self.expected_schema.keys())

    @classmethod
    def _parse_into_schema(cls) -> Schema:
        if cls._schema is not None:
            return cls._schema

        schema_dict: dict[str, _TypedColumn] = {}
        checks = []

        attr_list = get_class_members(cls)

        for attr, val in attr_list:
            if isinstance(val, _Column):
                new_val = copy.copy(val)
                # We may modify checks, which is a list, so we need to copy it
                new_val.checks = list(val.checks)

                col_name = attr if new_val.name is None else new_val.name

                # TODO: A TypedColumn is a Column and a DType, but the isinstance check
                # above does not work on TypedColumn, only Column.
                schema_dict[col_name] = new_val  # type: ignore[assignment]

        for attr, val in attr_list:
            if isinstance(val, Check):
                if (cols_or_selector := val.columns) is not None:
                    if isinstance(cols_or_selector, Selector):
                        cols = cols_or_selector(schema_dict)  # type: ignore
                    else:
                        cols = cols_or_selector

                    for c in cols:
                        if c in schema_dict:
                            schema_dict[c].checks.append(val)
                else:
                    checks.append(val)

        res = Schema(expected_schema=schema_dict, checks=checks)
        cls._schema = res

        return res

    @classmethod
    def interrogate(
        cls, df: nwt.IntoDataFrameT, cast: bool = False
    ) -> InterrogationResult:
        return _interrogate(cls._parse_into_schema(), df, cast)

    def __interrogate(
        self, df: nwt.IntoDataFrameT, cast: bool = False
    ) -> InterrogationResult:
        return _interrogate(self, df, cast)

    @classmethod
    def validate(cls, df: nwt.IntoDataFrameT, cast: bool = False) -> nwt.IntoDataFrameT:
        """Validate the given DataFrame

        Parameters
        ----------
        df : nwt.IntoDataFrameT
            Any Narwhals-compatible DataFrame, see https://narwhals-dev.github.io/narwhals/
            for more information
        cast : bool, optional
            Whether to cast columns, by default False

        Returns
        -------
        nwt.IntoDataFrameT
            Your original DataFrame

        Raises
        ------
        SchemaError
            If validation fails
        """
        return _validate(cls._parse_into_schema(), df, cast)

    def __validate(
        self, df: nwt.IntoDataFrameT, cast: bool = False
    ) -> nwt.IntoDataFrameT:
        return _validate(self, df, cast)

    @classmethod
    def filter(cls, df: nwt.IntoDataFrameT, cast: bool = False) -> nwt.IntoDataFrameT:
        return _filter(cls._parse_into_schema(), df, cast)

    def __filter(
        self, df: nwt.IntoDataFrameT, cast: bool = False
    ) -> nwt.IntoDataFrameT:
        return _filter(self, df, cast)
