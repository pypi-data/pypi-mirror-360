"""Supabase database helper implementation"""
from typing import Optional, Dict, Any

from supabase import Client as SupabaseClient
from bisslog.transactional.transaction_traceable import TransactionTraceable


class BasicSupabaseHelper(TransactionTraceable):
    """Basic helper for interacting with Supabase using common operations.

    This class provides convenience methods for inserting, retrieving, and counting
    records in Supabase tables while supporting traceability and clean architecture.
    """

    def __init__(self, client: SupabaseClient) -> None:
        self.client = client

    def insert_one(self, table: str, data: dict) -> Optional[dict]:
        """
        Insert a single row into a Supabase table.

        Parameters
        ----------
        table : str
            The name of the target table.
        data : dict
            A dictionary representing the row to be inserted.

        Returns
        -------
        dict or None
            The inserted row as returned by Supabase, or None if insertion failed.
        """
        response = self.client.table(table).insert(data).execute()
        if response.data:
            return response.data[0]
        return None

    def find_one(self, table: str, filters: Dict[str, Any]) -> Optional[dict]:
        """
        Fetch a single row from a Supabase table matching the given filters.

        Parameters
        ----------
        table : str
            The name of the table to query.
        filters : dict
            A dictionary of field-value pairs to filter by (e.g., {"email": "user@example.com"}).

        Returns
        -------
        dict or None
            The first matching row, or None if no match was found.
        """
        query = self.client.table(table)
        for key, value in filters.items():
            query = query.eq(key, value)
        response = query.limit(1).execute()
        if response.data:
            return response.data[0]
        return None

    def get_length(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Get the total number of rows in a table matching the given filters.

        Parameters
        ----------
        table : str
            The name of the table to count records in.
        filters : dict, optional
            Field-value pairs to filter by. If omitted, counts all records.

        Returns
        -------
        int
            The total number of matching rows.
        """
        query = self.client.table(table).select('*', count='exact')
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.count or 0
