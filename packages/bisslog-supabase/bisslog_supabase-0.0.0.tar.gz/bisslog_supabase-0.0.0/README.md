# Business logic - Supabase (bisslog-supabase-py)

[![PyPI](https://img.shields.io/pypi/v/bisslog-supabase-py)](https://pypi.org/project/bisslog-supabase-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

It is an extension of the bisslog library to support processes with the Supabase service using the official Python SDK.

If you want to know more about what bisslog is, you can enter [here](https://github.com/darwinhc/bisslog-docs) or in their [library](https://github.com/darwinhc/bisslog-core-py)

---

## 🚀 Installation
You can install `bisslog-supabase-py` using **pip**:

```bash
pip install bisslog-supabase-py
```

## Usage example

~~~python
import os
from supabase import create_client
from abc import ABC, abstractmethod
from bisslog import Division, bisslog_db
from bisslog_supabase import BasicSupabaseHelper, bisslog_exc_mapper_supabase


class MarketingDivision(Division, ABC):

    @abstractmethod
    def find_sales_per_client(self, email: str):
        raise NotImplementedError("find_sales_per_client must be implemented")


class MarketingSupabaseDivision(MarketingDivision, BasicSupabaseHelper):

    @bisslog_exc_mapper_supabase
    def find_sales_per_client(self, email: str):
        return self.find_one("sales", {"email": email})


supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_SERVICE_ROLE"]
client = create_client(supabase_url, supabase_key)

marketing_div = MarketingSupabaseDivision(client)
bisslog_db.register_adapters(marketing=marketing_div)
~~~

## Components

### BasicSupabaseHelper

`BasicSupabaseHelper` is a helper class for interacting with Supabase tables via the official SDK.  
It provides convenient methods for performing insert, query, and count operations while maintaining traceability through `TransactionTraceable`.

#### **Initialization**
~~~python
BasicSupabaseHelper(client: SupabaseClient)
~~~

Initializes the helper with a `SupabaseClient` instance.

#### **Methods**

- `insert_one`
~~~python
insert_one(table: str, data: dict) -> Optional[dict]
~~~
Inserts a record into the specified table and returns the inserted data or None.

- `find_one`
~~~python
find_one(table: str, filters: dict) -> Optional[dict]
~~~
Fetches a single row matching the filters or returns None.

- `get_length`
~~~python
get_length(table: str, filters: Optional[dict] = None) -> int
~~~
Returns the number of matching rows in the given table.

### bisslog_exc_mapper_supabase

Decorator to map Supabase or HTTPX exceptions to their corresponding Bisslog exceptions.

| **Exception (httpx/Supabase)** | **Mapped Bisslog Exception**        |
|-------------------------------|-------------------------------------|
| `HTTPStatusError 400`         | `InvalidDataExtException`          |
| `HTTPStatusError 401`         | `ConfigurationExtException`        |
| `HTTPStatusError 403/404`     | `ProgrammingErrorExtException`     |
| `HTTPStatusError 409`         | `IntegrityErrorExtException`       |
| `HTTPStatusError 5xx`         | `OperationalErrorExtException`     |
| `TimeoutException`            | `TimeoutExtException`              |
| `RequestError`                | `ConnectionExtException`           |
| `Exception` (fallback)        | `ExternalInteractionError`         |

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.