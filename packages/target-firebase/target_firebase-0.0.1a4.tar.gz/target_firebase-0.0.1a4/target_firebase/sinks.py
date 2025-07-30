"""Firebase target sink class, which handles writing streams."""

from __future__ import annotations

import typing as t

from singer_sdk.sinks import RecordSink

if t.TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client


class FirebaseSink(RecordSink):
    """Firebase target sink class."""

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize the sink."""
        super().__init__(*args, **kwargs)
        if len(self.key_properties) > 1:
            msg = "Composite keys are not supported"
            raise NotImplementedError(msg)

        self._db: Client | None = None

    @property
    def db(self) -> Client:
        """Return the Firestore client."""
        if self._db is None:
            msg = "Firestore client not initialized"
            raise ValueError(msg)
        return self._db

    @db.setter
    def db(self, db: Client) -> None:
        """Set the Firestore client."""
        self._db = db

    def process_record(self, record: dict, context: dict) -> None:  # noqa: ARG002
        """Process the record.

        Args:
            record: Individual record in the stream.
            context: Stream partition or context dictionary.
        """
        if len(self.key_properties) == 1:
            self.db.collection("cities").document(self.key_properties[0]).set(record)
            return

        self.db.collection("cities").add(record)
