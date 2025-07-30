"""Stream type classes for tap-readme."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th

from tap_readme.client import ReadMeStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class Categories(ReadMeStream):
    """Categories stream."""

    name = "categories"
    path = "/v1/categories"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("title", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("order", th.IntegerType),
        th.Property("reference", th.BooleanType),
        th.Property("version", th.StringType),
        th.Property("project", th.StringType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("type", th.StringType),
        th.Property("id", th.StringType),
        th.Property("_id", th.StringType),
    ).to_dict()

    def get_child_context(
        self,
        record: dict[str, t.Any],
        context: Context | None,  # noqa: ARG002
    ) -> dict[str, t.Any] | None:
        """Return a dictionary of child context data."""
        return {
            "category_slug": record["slug"],
        }


class CategoryDocs(ReadMeStream):
    """Category docs stream."""

    parent_stream_type = Categories

    name = "category_docs"
    path = "/v1/categories/{category_slug}/docs"
    primary_keys = ("_id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("_id", th.StringType),
        th.Property("title", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("order", th.IntegerType),
        th.Property("hidden", th.BooleanType),
        th.Property("children", th.ArrayType(th.ObjectType())),
    ).to_dict()


class Metadata(ReadMeStream):
    """API specification metadata stream."""

    name = "metadata"
    path = "/v1/api-specification"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property("title", th.StringType),
        th.Property("source", th.StringType),
        th.Property("_id", th.StringType),
        th.Property("lastSynced", th.DateTimeType),
        th.Property("version", th.StringType),
        th.Property(
            "category",
            th.ObjectType(
                th.Property("title", th.StringType),
                th.Property("slug", th.StringType),
                th.Property("order", th.IntegerType),
                th.Property("_id", th.StringType),
                th.Property("type", th.StringType),
                th.Property("id", th.StringType),
            ),
        ),
        th.Property("type", th.StringType),
        th.Property("id", th.StringType),
    ).to_dict()


class Changelogs(ReadMeStream):
    """Changelogs stream."""

    name = "changelogs"
    path = "/v1/changelogs"
    primary_keys = ("_id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "metadata",
            th.ObjectType(
                th.Property("image", th.ArrayType(th.StringType)),
                th.Property("title", th.StringType),
                th.Property("description", th.StringType),
                th.Property("keywords", th.StringType),
            ),
        ),
        th.Property(
            "algolia",
            th.ObjectType(
                th.Property("recordCount", th.IntegerType),
                th.Property("publishPending", th.BooleanType),
            ),
        ),
        th.Property("title", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("body", th.StringType),
        th.Property("type", th.StringType),
        th.Property("hidden", th.BooleanType),
        th.Property("revision", th.IntegerType),
        th.Property("_id", th.StringType),
        th.Property("pendingAlgoliaPublish", th.BooleanType),
        th.Property("createdAt", th.DateTimeType),
        th.Property("updatedAt", th.DateTimeType),
        th.Property("__v", th.IntegerType),
        th.Property("html", th.StringType),
    ).to_dict()
