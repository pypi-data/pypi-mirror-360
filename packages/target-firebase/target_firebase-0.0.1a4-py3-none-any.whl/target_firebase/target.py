"""Firebase target class."""

from __future__ import annotations

import typing as t

import firebase_admin
from firebase_admin import credentials, firestore
from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_firebase.sinks import FirebaseSink


class TargetFirebase(Target):
    """Sample target for Firebase."""

    name = "target-firebase"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "credential_file",
            th.StringType,
            description=(
                "The path to the Google Cloud Firestore credential file. "
                "If none is provided, Google Application Default Credentials are used."
            ),
        ),
        th.Property(
            "credential",
            th.ObjectType(
                th.Property(
                    "type",
                    th.Constant("service_account"),
                    required=True,
                    description="The type of credential.",
                    default="service_account",
                ),
                th.Property(
                    "client_email",
                    th.StringType,
                    required=True,
                    description="The service account's email.",
                ),
                th.Property(
                    "token_uri",
                    th.StringType,
                    description="The OAuth 2.0 Token URI.",
                    default="https://oauth2.googleapis.com/token",
                ),
                th.Property(
                    "project_id",
                    th.StringType,
                    required=True,
                    description="Project ID associated with the service account credential.",
                ),
                th.Property(
                    "universe_domain",
                    th.StringType,
                    description=(
                        "The universe domain. The default universe domain is "
                        "googleapis.com. For default value self signed jwt is "
                        "used for token refresh."
                    ),
                ),
                th.Property(
                    "trust_boundary",
                    th.StringType,
                    description="String representation of trust boundary meta.",
                ),
            ),
            description=(
                "The Google Cloud Firestore credential object. "
                "If none is provided, Google Application Default Credentials are used."
            ),
        ),
        th.Property(
            "firebase_app",
            th.StringType,
            description="The name of the Firebase app to use.",
            default="[DEFAULT]",
        ),
        th.Property(
            "database_id",
            th.StringType,
            description=(
                "The database ID of the Google Cloud Firestore database to be used. "
                "Defaults to the default Firestore database ID if not specified or an "
                "empty string."
            ),
        ),
    ).to_dict()

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize the target.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        if credential := self.config.get("credential"):
            cred = credentials.Certificate(credential)
        elif credential_file := self.config.get("credential_file"):
            cred = credentials.Certificate(credential_file)
        else:
            cred = credentials.ApplicationDefault()

        try:
            _app = firebase_admin.get_app(name=self.config.get("firebase_app"))
        except ValueError:
            _app = firebase_admin.initialize_app(
                credential=cred,
                name=self.config.get("firebase_app"),
            )

        self.db = firestore.client(app=_app, database_id=self.config.get("database_id"))

    def get_sink(self, *args: t.Any, **kwargs: t.Any) -> FirebaseSink:
        """Return a new instance of a Firebase sink.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            FirebaseSink: A new instance of FirebaseSink.
        """
        sink = super().get_sink(*args, **kwargs)
        sink.db = self.db
        return sink

    default_sink_class = FirebaseSink


if __name__ == "__main__":
    """Run the TargetFirebase CLI."""
    TargetFirebase.cli()
