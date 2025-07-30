"""
Supabase integration helpers for the Bisslog framework.

This module provides core building blocks to support interaction with Supabase services
(auth, database, storage, etc.) through a clean architecture approach. The helper and
exception handler allow decoupling domain logic from infrastructure concerns.

Exports:
    - BasicSupabaseHelper: Helper class to perform basic Supabase operations (insert, find, count).
    - bisslog_exc_mapper_supabase: Decorator to map Supabase/HTTPX exceptions into Bisslog exceptions.
"""
from .basic_helper import BasicSupabaseHelper
from .exception_handler import bisslog_exc_mapper_supabase

__all__ = ["BasicSupabaseHelper", "bisslog_exc_mapper_supabase"]
