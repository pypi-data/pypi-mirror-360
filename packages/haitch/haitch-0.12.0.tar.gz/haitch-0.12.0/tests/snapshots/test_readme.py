from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_readme(snapshot: Snapshot) -> None:
    # Fetch emails from data store.
    emails = ["jane@aol.com", "bob@example.com", "mark@mail.org"]

    # Build an ordered list with org domain emails.
    dom = H.ol(class_="email-list")(
        H.li(H.a(href=f"mailto:{email}")(email))
        for email in sorted(emails)
        if email.endswith(".com")
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
