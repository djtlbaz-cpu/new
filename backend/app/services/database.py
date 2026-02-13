from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from supabase import Client, create_client

from ..config import settings


@dataclass
class DatabaseGateway:
    client: Optional[Client] = None
    enabled: bool = False

    def __post_init__(self) -> None:
        if self.client is None and settings.supabase_url and settings.supabase_service_key:
            try:
                self.client = create_client(settings.supabase_url, settings.supabase_service_key)
            except (RuntimeError, ValueError, Exception) as exc:
                print(f"[Supabase] Failed to initialize client: {exc}")
                self.client = None
        self.enabled = self.client is not None

    def is_enabled(self) -> bool:
        return self.enabled and self.client is not None

    def _safe_insert(self, table: str, payload: Dict[str, Any]) -> bool:
        if not self.is_enabled():
            return False
        try:
            self.client.table(table).insert(payload).execute()
            return True
        except (ConnectionError, TimeoutError, RuntimeError, ValueError) as exc:
            print(f"[Supabase] Failed to insert into {table}: {exc}")
            return False

    def log_generation(self, payload: Dict[str, Any]) -> bool:
        return self._safe_insert("generation_events", payload)

    def store_pattern_feedback(self, payload: Dict[str, Any]) -> bool:
        return self._safe_insert("pattern_feedback", payload)

    def store_preference_profile(self, payload: Dict[str, Any]) -> bool:
        return self._safe_insert("preference_profiles", payload)

    def store_midi_asset(self, payload: Dict[str, Any]) -> bool:
        return self._safe_insert("midi_assets", payload)

    def store_training_batch(self, payload: Dict[str, Any]) -> bool:
        return self._safe_insert("training_batches", payload)


class _GatewayHolder:
    instance: DatabaseGateway | None = None


def get_database_gateway() -> DatabaseGateway:
    if _GatewayHolder.instance is None:
        _GatewayHolder.instance = DatabaseGateway()
    return _GatewayHolder.instance
