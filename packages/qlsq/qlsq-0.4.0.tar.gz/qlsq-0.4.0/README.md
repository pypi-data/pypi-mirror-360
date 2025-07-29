# qlsq (QL²) - Predictable SQL Query Generation

[![PyPI version](https://badge.fury.io/py/qlsq.svg)](https://pypi.org/project/qlsq/)

**qlsq** (QL-squared) is a Python library for generating predictable, secure SQL queries from Lisp-like query expressions. It helps you build complex database queries while maintaining control over performance and security.

## ✨ Key Features

- **Prevents N+1 Query Problems** - Results nesing is not allowed
- **Query Complexity Control** - Restrict filtering to indexed columns only
- **Smart Join Management** - Only performs LEFT JOINs for actually selected fields
- **Claim-Based Access Control** - Fine-grained permissions for each field (read/edit/filter)
- **Predictable Output** - Generates clean, parameterized SQL queries
- **PostgreSQL Integration** - Works seamlessly with psycopg, generating parameterized queries

## 🚀 Installation

```bash
pip install qlsq
# or
uv add qlsq
# or
poetry add qlsq
```

## 📋 Requirements

- Python 3.12+
- psycopg2 or psycopg3 (for PostgreSQL integration)

## 🎯 Use Cases

Perfect for applications that need:
- Dynamic query building from frontend filters
- Multi-tenant applications with complex permissions
- APIs that expose flexible data querying capabilities
- Applications requiring predictable query performance

## 📖 Quick Start

### 1. Define Your Context

Every query operates within a context that defines tables and fields:

```python
from qlsq import ContextTable, ContextField, Context, QueryType

# Define tables and their relationships
tables = [
    ContextTable(
        alias="ut",
        source="user_tasks", 
        join_condition=None,  # Root table
        depends_on=[]
    ),
    ContextTable(
        alias="u",
        source="users",
        join_condition="u.id = ut.user_id",
        depends_on=["ut"]  # Depends on user_tasks table
    ),
]

# Define available fields with permissions
fields = [
    ContextField(
        alias="full_name",
        source="full_name",
        query_type=QueryType.text,
        table_alias="u",
        read_claim="r_full_name",
        edit_claim="e_full_name", 
        filter_claim="f_full_name",
    ),
    ContextField(
        alias="user_id",
        source="user_id",
        query_type=QueryType.numeric,
        table_alias="ut",
        read_claim="r_user_id",
        edit_claim="e_user_id",
        filter_claim="f_user_id",
    ),
]

# Create the context
context = Context(tables, fields)

# Create the context registry
context_registry = ContextRegistry(
    {
        "user_tasks": context,
    }
)
```

### 2. Write Lisp-Like Queries

```python
# Simple query: SELECT full_name WHERE user_id = 3
query_expression = [
    ["using", "user_tasks"], # specify context
    ["select", "full_name"],
    ["where", ["eq", "user_id", 3]]
]
```

### 3. Generate SQL (Two Approaches)

**Approach A: Parse then generate**
```python
# Parse and generate SQL
query = context.parse_query(query_expression)
sql, params = query.to_sql()

print("Generated SQL:")
print(sql)
# Output: SELECT u.full_name FROM user_tasks ut LEFT JOIN users u ON u.id = ut.user_id WHERE (ut.user_id = %(param_0)s);

print("Parameters:")
print(params)
# Output: {"param_0": 3}
```

**Approach B: Direct generation with claims**
```python
# Generate SQL directly with claims validation
user_claims = ["r_full_name", "f_user_id"]  # User's permissions
sql, params = context.to_sql(query_expression, user_claims)
```

### 4. Claims-Based Security

```python
# Define user permissions
user_claims = ["r_full_name", "f_user_id"]  # Can read full_name, filter by user_id

# This will work - user has required claims
query = context.parse_query([["select", "full_name"], ["where", ["eq", "user_id", 3]]])
query.assert_claims(user_claims)  # Validates permissions

# This will fail - user lacks r_user_id claim
try:
    query = context.parse_query([["select", "user_id"]])
    query.assert_claims(user_claims)  # Raises MissingClaimsError
except MissingClaimsError as e:
    print(f"Access denied: {e}")
```

### 5. Execute with psycopg

```python
import psycopg2

# Execute the query
with psycopg2.connect(database_url) as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        results = cursor.fetchall()
```

## 🔍 Advanced Examples

### Complex Filtering

```python
# Multiple conditions with AND/OR logic
query = [
    ["using", "user_tasks"],
    ["select", "full_name", "user_id"],
    ["where", [
        "and",
        ["eq", "user_id", 3],
        ["like", "full_name", ["str", "%john%"]]
    ]]
]
```

### Mathematical Operations

```python
# Arithmetic operations
query = [
    ["select", ["add", "field1", "field2"]],  # Addition
    ["select", ["sub", "field1", "field2"]],  # Subtraction  
    ["select", ["mul", "field1", "field2"]],  # Multiplication
    ["select", ["div", "field1", "field2"]],  # Division
]
```

### String Operations

```python
# String manipulation
query = [
    ["select", ["concat", "first_name", ["str", " "], "last_name"]],  # Concatenation
    ["select", ["lower", "full_name"]],   # Lowercase
    ["select", ["upper", "full_name"]],   # Uppercase
]
```

### Date Handling

```python
# Date operations
query = [
    ["where", ["eq", "created_at", ["date", "2024-01-15T10:30:00Z"]]]
]
```

### Null Checks and Coalescing

```python
# Working with NULL values
query = [
    ["select", ["coalesce", "nickname", ["str", "-NA-"]]],
    ["where", ["is_not_null", "email"]],  # Check for non-null
]
```

### Sorting and Limiting

```python
# Add sorting and pagination
query = [
    ["using", "users"],
    ["select", "full_name", "user_id"],
    ["where", ["gt", "user_id", 0]],
    ["orderby", ["asc", "full_name"]],  # Note: asc/desc wraps the field
    ["limit", 10],
    ["offset", 20]
]
```

### IN Clause and Complex Conditions

```python
# Multiple values and complex logic
query = [
    ["using", "users"],
    ["select", "full_name"],
    ["where", [
        "or",
        ["in", "user_id", 1, 2, 3, 4],
        ["and", 
            ["gte", "age", 18],
            ["like", "email", ["str", "%@company.com"]]
        ]
    ]]
]
```

## 🛡️ Security Features

### Claim-Based Access Control

```python
# Only users with proper claims can access fields
user_claims = ["r_full_name", "f_user_id"]  # Can read full_name, filter by user_id
sql, params = context.to_sql(query_expression, user_claims) # Will raise MissingClaimsError if claims are missing
```

### Query Validation

- Prevents filtering on non-indexed columns (if configured)
- Validates field access permissions
- Ensures proper table relationships
- Protects against SQL injection through parameterization

## 🎨 Query Language Reference

### Core Operations
| Operation | Syntax | Example |
|-----------|--------|---------|
| Select | `["select", "field1", "field2"]` | `["select", "name", "email"]` |
| Where | `["where", condition]` | `["where", ["eq", "id", 1]]` |

### Comparison Operators
| Operation | Syntax | Example |
|-----------|--------|---------|
| Equals | `["eq", field, value]` | `["eq", "status", ["str", "active"]]` |
| Not Equals | `["neq", field, value]` | `["neq", "status", ["str", "deleted"]]` |
| Greater Than | `["gt", field, value]` | `["gt", "age", 18]` |
| Greater/Equal | `["gte", field, value]` | `["gte", "score", 100]` |
| Less Than | `["lt", field, value]` | `["lt", "price", 50]` |
| Less/Equal | `["lte", field, value]` | `["lte", "quantity", 10]` |
| Like Pattern | `["like", field, pattern]` | `["like", "name", ["str", "%john%"]]` |
| In List | `["in", field, val1, val2, ...]` | `["in", "id", 1, 2, 3]` |

### Logical Operators
| Operation | Syntax | Example |
|-----------|--------|---------|
| And | `["and", cond1, cond2, ...]` | `["and", ["eq", "a", 1], ["eq", "b", 2]]` |
| Or | `["or", cond1, cond2, ...]` | `["or", ["eq", "status", "active"], ["eq", "status", "pending"]]` |
| Not | `["not", condition]` | `["not", ["eq", "deleted", true]]` |

### Null Checks
| Operation | Syntax | Example |
|-----------|--------|---------|
| Is Null | `["is_null", field]` | `["is_null", "deleted_at"]` |
| Is Not Null | `["is_not_null", field]` | `["is_not_null", "email"]` |

### Mathematical Operations
| Operation | Syntax | Example |
|-----------|--------|---------|
| Addition | `["add", expr1, expr2, ...]` | `["add", "base_price", "tax"]` |
| Subtraction | `["sub", expr1, expr2, ...]` | `["sub", "total", "discount"]` |
| Multiplication | `["mul", expr1, expr2, ...]` | `["mul", "price", "quantity"]` |
| Division | `["div", expr1, expr2]` | `["div", "total", "count"]` |

### String Operations
| Operation | Syntax | Example |
|-----------|--------|---------|
| Concatenate | `["concat", str1, str2, ...]` | `["concat", "first_name", ["str", " "], "last_name"]` |
| Lowercase | `["lower", string_expr]` | `["lower", "email"]` |
| Uppercase | `["upper", string_expr]` | `["upper", "code"]` |
| Coalesce | `["coalesce", expr1, expr2, ...]` | `["coalesce", "nickname", ["str", "-NA-"]]` |

### Literal Values
| Type | Syntax | Example |
|------|--------|---------|
| String | `["str", "value"]` | `["str", "hello world"]` |
| Date | `["date", "iso_string"]` | `["date", "2024-01-15T10:30:00Z"]` |
| Integer | `42` | `["eq", "age", 25]` |
| Float | `3.14` | `["eq", "price", 19.99]` |
| Boolean | `true`/`false` | `["eq", "active", true]` |
| Null | `null` | `["eq", "deleted_at", null]` |

### Ordering and Pagination
| Operation | Syntax | Example |
|-----------|--------|---------|
| Order By | `["orderby", direction1, direction2, ...]` | `["orderby", ["asc", "name"], ["desc", "created_at"]]` |
| Ascending | `["asc", field]` | `["asc", "name"]` |
| Descending | `["desc", field]` | `["desc", "created_at"]` |
| Limit | `["limit", count]` | `["limit", 10]` |
| Offset | `["offset", count]` | `["offset", 20]` |

## ⚠️ Limitations

- **No nested queries** - Complex nesting must be implemented in SQL
- **PostgreSQL only** - Currently only supports PostgreSQL via psycopg
- **Left joins only** - Developer must ensure there are no unwanted duplicates

## 🔧 API Reference

`FIXME`: list main classes, methods, exceptions


## 🤝 Contributing

Contributions are welcome! `main` branch is for development, each release and subseaquent hotfixes land on separate branches like `v0.1.3`.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/qlsq/)
