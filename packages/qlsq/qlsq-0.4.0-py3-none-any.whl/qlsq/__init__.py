from typing import Self
from dataclasses import dataclass
from abc import ABC
import datetime as dt
import uuid

class QueryError(Exception): ...


class UnknownArgError(QueryError): ...


class UnknownFieldError(QueryError): ...


class QueryTypeError(QueryError): ...


class ContextNotSpecifiedError(QueryError): ...


class ContextNotFoundError(QueryError): ...


class ContextError(Exception): ...


class ArgParserConflictError(ContextError): ...


class ContextFieldConflictError(ContextError): ...


class ContextTableConflictError(ContextError): ...


class ContextRootTableError(ContextError): ...


class ContextTableResolutionError(ContextError): ...


class MissingClaimsError(Exception): ...


class QueryType:
    numeric = "numeric"
    boolean = "boolean"
    text = "text"
    date = "date"
    uuid = "uuid"
    null = "null"
    condition = "condition"
    select = "select"
    update = "update"
    set = "set"
    insert = "insert"
    delete = "delete"
    where = "where"
    orderby = "orderby"
    direction = "direction"
    limit = "limit"
    offset = "offset"
    using = "using"

    value_types = {
        "numeric",
        "boolean",
        "text",
        "date",
        "uuid",
        "null",
    }


@dataclass
class ContextField:
    alias: str
    source: str
    query_type: str
    table_alias: str
    read_claim: str
    edit_claim: str
    filter_claim: str


@dataclass
class ContextTable:
    alias: str
    source: str
    join_condition: str
    depends_on: list[str]


class Context:
    def __init__(self, tables: list[ContextTable], fields: list[ContextField]):

        self.tables = dict()
        for t in tables:
            self._add_table(t)

        self.tables_order = []
        self._set_tables_order()

        self.fields = dict()
        for f in fields:
            self._add_field(f)

        # FIXME insert, delete, date_delta
        self.arg_parsers = {
            "str": QueryStr,
            "date": QueryDate,
            "uuid": QueryUuid,
            "concat": QueryConcat,
            "lower": QueryLower,
            "upper": QueryUpper,
            "add": QueryAdd,
            "sub": QuerySub,
            "mul": QueryMul,
            "div": QueryDiv,
            "coalesce": QueryCoalesce,
            "select": QuerySelect,
            "where": QueryWhere,
            "and": QueryAnd,
            "or": QueryOr,
            "like": QueryLike,
            "eq": QueryEq,
            "neq": QueryNeq,
            "lt": QueryLt,
            "gt": QueryGt,
            "lte": QueryLte,
            "gte": QueryGte,
            "not": QueryNot,
            "is_null": QueryIsNull,
            "is_not_null": QueryIsNotNull,
            "in": QueryIn,
            "orderby": QueryOrderby,
            "asc": QueryAsc,
            "desc": QueryDesc,
            "limit": QueryLimit,
            "offset": QueryOffset,
            "update": QueryUpdate,
            "set": QuerySet,
            "using": QueryUsing,
        }

    def _add_field(self, field: ContextField):
        if field.alias in self.fields:
            raise ContextFieldConflictError(
                f"field.alias in self.fields {field.alias=}"
            )
        self.fields[field.alias] = field

    def _add_table(self, table: ContextTable):
        if table.alias in self.tables:
            raise ContextTableConflictError(
                f"table.alias in self.tables {table.alias=}"
            )

        self.tables[table.alias] = table

    def _set_tables_order(self):
        tables_order = []

        root_tables = {k for k, v in self.tables.items() if not v.depends_on}
        if len(root_tables) != 1:
            raise ContextRootTableError(f"len(root_tables) != 1 {root_tables=}")

        tables_order.append(list(root_tables)[0])
        remaining_tables = set(self.tables) - root_tables
        resolved_tables = set(root_tables)

        while len(remaining_tables) > 0:
            continue_resolve = False
            for table_alias in sorted(remaining_tables):
                table = self.tables[table_alias]
                depends_on = set(table.depends_on)
                if depends_on.issubset(resolved_tables):
                    tables_order.append(table_alias)
                    resolved_tables.add(table_alias)
                    remaining_tables.discard(table_alias)
                    continue_resolve = True
            if not continue_resolve:
                raise ContextTableResolutionError(
                    f"_set_tables_order {remaining_tables=} {resolved_tables=}"
                )

        self.tables_order = tables_order

    def add_arg_parser(
        self,
        query_id,
        query_cls,
    ):
        if query_id in self.arg_parsers:
            raise ArgParserConflictError(f"query_id in self.arg_parsers {query_id}")

        self.arg_parsers[query_id] = query_cls


class ContextRegistry(dict):

    def parse_query(self, lq):
        q = Query(self, lq)
        return q

    def to_sql(self, lq, claims=None):
        q = Query(self, lq)
        q.assert_claims(claims)
        return q.to_sql()


def find_single_context(lq):
    if not isinstance(lq, list):
        raise ContextNotSpecifiedError(f"{lq=}")

    lq = [q for q in lq if len(q) > 0 and q[0] == "using"]
    if len(lq) != 1:
        raise ContextNotSpecifiedError(f"{lq=}")

    lq = lq[0]
    if len(lq) != 2:
        raise ContextNotSpecifiedError(f"{lq=}")

    context_alias = lq[1]
    if not isinstance(context_alias, str):
        raise ContextNotSpecifiedError(
            f"not isinstance(context_alias, str), {context_alias=}"
        )

    return context_alias


def parse_arg(context, lq_arg):
    if lq_arg is None:
        return QueryNull()
    elif isinstance(lq_arg, float):
        return QueryFloat(lq_arg)
    elif isinstance(lq_arg, int):
        return QueryInt(lq_arg)
    elif isinstance(lq_arg, bool):
        return QueryBool(lq_arg)
    elif isinstance(lq_arg, str):
        return QueryField(context, lq_arg)
    elif isinstance(lq_arg, list):
        assert len(lq_arg) > 0
        q_id = lq_arg[0]
        arg = context.arg_parsers[q_id](context, lq_arg)
        return arg
    else:
        raise UnknownArgError(f"parse_arg error {lq_arg}")


def parse_args(context, lq_args):
    result = [parse_arg(context, a) for a in lq_args]
    return result


def assert_args_types(args, allowed_types: set):
    for arg in args:
        arg_query_type = arg.query_type()
        if arg_query_type not in allowed_types:
            raise QueryTypeError(
                f"assert_args_types {arg=} {arg_query_type=} {allowed_types=}"
            )


def assert_args_types_equal(args):
    if len(args) < 2:
        return

    query_types = {a.query_type() for a in args}
    if len(query_types) > 1:
        raise QueryTypeError(f"assert_args_types_equal {query_types=}")


def assert_args_contains_exactly_1(args, target_types):
    found_types = [a.query_type() for a in args if a.query_type() in target_types]
    if len(found_types) != 1:
        raise QueryTypeError(f"assert_args_contains_exactly_1 {found_types=}")

    return list(found_types)[0]


def assert_args_contains_at_most_1(args, target_types):
    found_types = [a.query_type() for a in args if a.query_type() in target_types]
    if len(found_types) > 1:
        raise QueryTypeError(f"assert_args_contains_at_most_1 {found_types=}")


def find_arg_by_type(args, target_type):
    for arg in args:
        if arg.query_type() == target_type:
            return arg

    return None


class QueryBase(ABC):
    args: list[Self] = []

    def to_sql(self):
        raise NotImplementedError("to_sql")

    def query_type(self):
        raise NotImplementedError("query_type")

    def collect_fields(self):
        result = set()
        for arg in self.args:
            result |= arg.collect_fields()
        return result

    def collect_read_claims(self, context):
        result = set()
        for arg in self.args:
            result |= arg.collect_read_claims(context)
        return result

    def collect_filter_claims(self, context):
        result = set()
        for arg in self.args:
            result |= arg.collect_filter_claims(context)
        return result

    def collect_edit_claims(self, context):
        result = set()
        for arg in self.args:
            result |= arg.collect_edit_claims(context)
        return result


class QueryFloat(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, float)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.numeric


class QueryInt(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, int)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.numeric


class QueryBool(QueryBase):
    def __init__(self, lq_arg):
        assert isinstance(lq_arg, bool)
        self.value = lq_arg

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if self.value:
            return "TRUE", params
        else:
            return "FALSE", params

    def query_type(self):
        return QueryType.boolean


class QueryNull(QueryBase):
    def __init__(self):
        pass

    def to_sql(self, params=None):
        if params is None:
            params = dict()
        return "NULL", params

    def query_type(self):
        return QueryType.null


class QueryStr(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "str"
        if isinstance(lq[1], str):
            self.value = lq[1]
        elif lq[1] is None:
            self.value = None
        else:
            # FIXME maybe ValueTypeError?
            raise QueryTypeError(f"expected type of str or None {lq=}")

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.text


class QueryDate(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "date"
        if lq[1] is None:
            self.value = None
        elif isinstance(lq[1], str):
            self.value = dt.datetime.fromisoformat(lq[1])
        elif isinstance(lq[1], (int, float)):
            self.value = dt.datetime.fromtimestamp(lq[1], dt.timezone.utc)
        else:
            raise QueryTypeError(f"expected type of int, str or None {lq=}")

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.date

class QueryUuid(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "uuid"
        if lq[1] is None:
            self.value = None
        elif isinstance(lq[1], str):
            self.value = uuid.UUID(lq[1])
        else:
            raise QueryTypeError(f"expected type of str or None {lq=}")

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        param_name = f"param_{len(params)}"
        params[param_name] = self.value
        return f"%({param_name})s", params

    def query_type(self):
        return QueryType.uuid

class QuerySelect(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "select"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            QueryType.value_types,
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"SELECT {', '.join(args_sql)}", params

    def query_type(self):
        return QueryType.select

    def collect_edit_claims(self, context):
        return set()

    def collect_filter_claims(self, context):
        return set()


class QueryConcat(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "concat"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.text,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' || '.join(args_sql)})", params

    def query_type(self):
        return QueryType.text


class QueryLower(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "lower"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.text,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"LOWER({sql_0})", params

    def query_type(self):
        return QueryType.text


class QueryUpper(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "upper"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.text,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"UPPER({sql_0})", params

    def query_type(self):
        return QueryType.text


class QueryAdd(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "add"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' + '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QuerySub(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "sub"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' - '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryMul(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "mul"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' * '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryDiv(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "div"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {
                QueryType.numeric,
                QueryType.null,
            },
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' / '.join(args_sql)})", params

    def query_type(self):
        return QueryType.numeric


class QueryField(QueryBase):
    def __init__(self, context, lq_arg):
        if lq_arg not in context.fields:
            raise UnknownFieldError(f"lq_arg not in context.fields {lq_arg=}")

        context_field = context.fields[lq_arg]
        self.table_alias = context_field.table_alias
        self.source = context_field.source
        self.alias = lq_arg
        self.field_query_type = context.fields[lq_arg].query_type

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        return f"{self.table_alias}.{self.source}", params

    def query_type(self):
        return self.field_query_type

    def collect_fields(self):
        return set([self.alias])

    def collect_read_claims(self, context):
        field = context.fields[self.alias]
        if field.read_claim:
            return set([field.read_claim])
        return set()

    def collect_filter_claims(self, context):
        field = context.fields[self.alias]
        if field.filter_claim:
            return set([field.filter_claim])
        return set()

    def collect_edit_claims(self, context):
        field = context.fields[self.alias]
        if field.edit_claim:
            return set([field.edit_claim])
        return set()


class QueryCoalesce(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) >= 2
        assert lq[0] == "coalesce"
        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"COALESCE({", ".join(args_sql)})", params

    def query_type(self):
        return self.args[0].query_type()


class QueryWhere(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) >= 1
        assert lq[0] == "where"

        if len(lq) == 1:
            self.args = []
            return

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        # Act as AND operator to make easy to add query constraints on backend
        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"WHERE ({' AND '.join(args_sql)})", params

    def query_type(self):
        return QueryType.where

    def collect_edit_claims(self, context):
        return set()

    def add_condition(self, context, lq):
        lq_args = [lq]
        args = parse_args(context, lq_args)
        assert_args_types(
            args,
            {QueryType.condition},
        )
        self.args.extend(args)


class QueryAnd(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "and"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.condition})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' AND '.join(args_sql)})", params

    def query_type(self):
        return QueryType.condition


class QueryOr(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) > 1
        assert lq[0] == "or"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.condition})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"({' OR '.join(args_sql)})", params

    def query_type(self):
        return QueryType.condition


class QueryEq(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "eq"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        assert_args_types_equal(args)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} = {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryNeq(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "neq"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        assert_args_types_equal(args)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} != {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryLt(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "lt"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} < {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryLte(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "lte"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} <= {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryGt(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "gt"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} > {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryGte(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "gte"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.numeric, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} >= {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryNot(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "not"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.condition})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"(NOT {sql_0})", params

    def query_type(self):
        return QueryType.condition


class QueryIsNull(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "is_null"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"({sql_0} IS NULL)", params

    def query_type(self):
        return QueryType.condition


class QueryIsNotNull(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "is_not_null"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"({sql_0} IS NOT NULL)", params

    def query_type(self):
        return QueryType.condition


class QueryIn(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) >= 3
        assert lq[0] == "in"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_rest = [arg.to_sql(params)[0] for arg in self.args[1:]]
        return f"({sql_0} IN ({', '.join(sql_rest)}))", params

    def query_type(self):
        return QueryType.condition


class QueryLike(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "like"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.text, QueryType.null})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        sql_1, _ = self.args[1].to_sql(params)
        return f"({sql_0} LIKE {sql_1})", params

    def query_type(self):
        return QueryType.condition


class QueryOrderby(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) >= 1
        assert lq[0] == "orderby"

        if len(lq) == 1:
            self.args = []
            return

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types | {QueryType.direction})
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"ORDER BY {', '.join(args_sql)}", params

    def query_type(self):
        return QueryType.orderby

    def collect_edit_claims(self, context):
        return set()


class QueryAsc(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "asc"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"{sql_0} ASC", params

    def query_type(self):
        return QueryType.direction


class QueryDesc(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "desc"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, QueryType.value_types)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0, _ = self.args[0].to_sql(params)
        return f"{sql_0} DESC", params

    def query_type(self):
        return QueryType.direction


class QueryLimit(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "limit"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert isinstance(args[0], QueryInt)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        sql_0, _ = self.args[0].to_sql(params)
        return f"LIMIT {sql_0}", params

    def query_type(self):
        return QueryType.limit

    def collect_edit_claims(self, context):
        return set()


class QueryOffset(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "offset"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert isinstance(args[0], QueryInt)
        self.args = args

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if len(self.args) == 0:
            return ""

        sql_0, _ = self.args[0].to_sql(params)
        return f"OFFSET {sql_0}", params

    def query_type(self):
        return QueryType.offset

    def collect_edit_claims(self, context):
        return set()


class QueryUpdate(QueryBase):
    def __init__(self, context: Context, lq):
        assert lq is not None
        assert len(lq) >= 2
        assert lq[0] == "update"

        lq_args = lq[1:]
        args = parse_args(context, lq_args)
        assert_args_types(args, {QueryType.set})
        self.args = args
        self.context = context

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        root_table_alias = self.context.tables_order[0]
        root_table = self.context.tables[root_table_alias]
        args_sql = [arg.to_sql(params)[0] for arg in self.args]
        return f"UPDATE {root_table.source} SET {", ".join(args_sql)} ", params

    def query_type(self):
        return QueryType.update


class QuerySet(QueryBase):
    def __init__(self, context: Context, lq):
        assert lq is not None
        assert len(lq) == 3
        assert lq[0] == "set"

        lq_arg_0 = lq[1]
        arg_0 = parse_arg(context, lq_arg_0)
        if not isinstance(arg_0, QueryField):
            raise QueryTypeError(f"not isinstance(arg_0, QueryField) {lq=}")

        table_alias = arg_0.table_alias
        root_table_alias = context.tables_order[0]
        if table_alias != root_table_alias:
            raise QueryError(f"updating non root table {lq=}, {root_table_alias=}")

        lq_arg_1 = lq[2]
        arg_1 = parse_arg(context, lq_arg_1)
        assert_args_types([arg_1], QueryType.value_types)
        assert_args_types_equal([arg_0, arg_1])

        self.arg_0: QueryField = arg_0
        self.arg_1: QueryBase = arg_1
        self.args = [arg_0, arg_1]

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        sql_0 = self.arg_0.source
        sql_1, _ = self.arg_1.to_sql(params)

        return f"{sql_0} = {sql_1}", params

    def query_type(self):
        return QueryType.set

    def collect_read_claims(self, context):
        return self.arg_1.collect_read_claims(context)

    def collect_filter_claims(self, context):
        return set()

    def collect_edit_claims(self, context):
        return self.arg_0.collect_edit_claims(context)

class QueryUsing(QueryBase):
    def __init__(self, context, lq):
        assert lq is not None
        assert len(lq) == 2
        assert lq[0] == "using"
        assert isinstance(lq[1], str)
        self.context_alias = lq[1]

    def query_type(self):
        return QueryType.using
        
class Query(QueryBase):
    def __init__(self, context_registry, lq):
        assert lq is not None
        context_alias = find_single_context(lq)
        context = context_registry.get(context_alias)
        if context is None:
            raise ContextNotFoundError(f"{context_alias=}")
        self.context = context

        args = parse_args(context, lq)
        self.query_type = assert_args_contains_exactly_1(
            args,
            {
                QueryType.select,
                QueryType.update,
                QueryType.insert,
                QueryType.delete,
            },
        )
        self.select = None
        self.update = None
        self.insert = None
        self.delete = None
        self.where = None
        self.orderby = None
        self.limit = None
        self.offset = None

        if self.query_type == QueryType.select:
            assert_args_contains_at_most_1(
                args,
                {QueryType.where},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.orderby},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.limit},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.offset},
            )
            self.select = find_arg_by_type(args, QueryType.select)
            self.where = find_arg_by_type(args, QueryType.where)
            self.orderby = find_arg_by_type(args, QueryType.orderby)
            self.limit = find_arg_by_type(args, QueryType.limit)
            self.offset = find_arg_by_type(args, QueryType.offset)
            self.args = args
            return
        elif self.query_type == QueryType.update:
            assert_args_contains_at_most_1(
                args,
                {QueryType.where},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.orderby},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.limit},
            )
            assert_args_contains_at_most_1(
                args,
                {QueryType.offset},
            )
            self.update = find_arg_by_type(args, QueryType.update)
            self.where = find_arg_by_type(args, QueryType.where)
            self.orderby = find_arg_by_type(args, QueryType.orderby)
            self.limit = find_arg_by_type(args, QueryType.limit)
            self.offset = find_arg_by_type(args, QueryType.offset)
            self.args = args
        else:
            raise NotImplementedError(f"not implemented {self.query_type=}")

    def collect_read_fields(self):
        result = set()
        if self.select is not None:
            result |= self.select.collect_fields()

        if self.where is not None:
            result |= self.where.collect_fields()

        if self.orderby is not None:
            result |= self.orderby.collect_fields()

        if self.limit is not None:
            result |= self.limit.collect_fields()

        if self.offset is not None:
            result |= self.offset.collect_fields()

        return result

    def collect_edit_fields(self):
        result = set()
        if self.update is not None:
            result |= self.update.collect_fields()

        return result

    def collect_filter_fields(self):
        result = set()

        if self.where is not None:
            result |= self.where.collect_fields()

        if self.orderby is not None:
            result |= self.orderby.collect_fields()

        if self.limit is not None:
            result |= self.limit.collect_fields()

        if self.offset is not None:
            result |= self.offset.collect_fields()

        return result

    def to_sql(self, params=None):
        if params is None:
            params = dict()

        if self.query_type == QueryType.select:
            select_part, _ = self.select.to_sql(params)
            where_part = ""
            if self.where is not None:
                where_part, _ = self.where.to_sql(params)
            orderby_part = ""
            if self.orderby is not None:
                orderby_part, _ = self.orderby.to_sql(params)
            limit_part = ""
            if self.limit is not None:
                limit_part, _ = self.limit.to_sql(params)
            offset_part = ""
            if self.offset is not None:
                offset_part, _ = self.offset.to_sql(params)
            from_part = self.build_from_clause()
            parts = [
                select_part,
                from_part,
                where_part,
                orderby_part,
                limit_part,
                offset_part,
            ]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params
        elif self.query_type == QueryType.update:
            update_part, _ = self.update.to_sql(params)
            where_part = ""
            if self.where is not None:
                where_part, _ = self.where.to_sql(params)
            orderby_part = ""
            if self.orderby is not None:
                orderby_part, _ = self.orderby.to_sql(params)
            limit_part = ""
            if self.limit is not None:
                limit_part, _ = self.limit.to_sql(params)
            offset_part = ""
            if self.offset is not None:
                offset_part, _ = self.offset.to_sql(params)
            from_part = self.build_from_clause()
            parts = [
                update_part,
                from_part,
                where_part,
                orderby_part,
                limit_part,
                offset_part,
            ]
            parts = [p for p in parts if p]
            return "\n".join(parts) + ";", params
        else:
            raise NotImplementedError(f"not implemented {self.query_type=}")

    def get_required_tables(self):
        fields = self.collect_fields()
        fields = [self.context.fields[f] for f in fields]
        tables = set()
        for field in fields:
            tables.add(field.table_alias)

        tables = [self.context.tables[t] for t in tables]
        required_tables = set()
        for table in tables:
            required_tables.add(table.alias)
            for table_alias in table.depends_on:
                required_tables.add(table_alias)

        return required_tables

    def build_from_clause(self):
        required_tables = self.get_required_tables()
        root_table = self.context.tables_order[0]
        root_table = self.context.tables[root_table]
        if len(required_tables) == 0:
            return f"FROM {root_table.source} {root_table.alias}"

        from_clause = f"FROM {root_table.source} {root_table.alias}"
        required_tables -= {root_table.alias}
        for table_alias in self.context.tables_order:
            if table_alias not in required_tables:
                continue

            table = self.context.tables[table_alias]
            from_clause += (
                f"\nLEFT JOIN {table.source} {table.alias} ON {table.join_condition}"
            )

        return from_clause

    def get_required_claims(self):
        result = set()
        result |= self.collect_read_claims(self.context)
        result |= self.collect_filter_claims(self.context)
        result |= self.collect_edit_claims(self.context)
        return result

    def assert_claims(self, claims=None):
        if claims is None:
            claims = set()

        claims = set(claims)
        required_claims = self.get_required_claims()
        missing_claims = required_claims - claims
        if len(missing_claims) == 0:
            return

        raise MissingClaimsError(f"assert_claims {missing_claims=}")

    def add_where_condition(self, lq):
        if self.where is None:
            arg = QueryWhere(self.context, ["where"])
            self.where = arg
            self.args.append(arg)

        self.where.add_condition(self.context, lq)

    def set_limit(self, limit):
        self.args = [a for a in self.args if a.query_type() != QueryType.limit]
        arg = QueryLimit(self.context, ["limit", limit])
        self.limit = arg
        self.args.append(arg)

    def set_offset(self, offset):
        self.args = [a for a in self.args if a.query_type() != QueryType.offset]
        arg = QueryOffset(self.context, ["offset", offset])
        self.offset = arg
        self.args.append(arg)
