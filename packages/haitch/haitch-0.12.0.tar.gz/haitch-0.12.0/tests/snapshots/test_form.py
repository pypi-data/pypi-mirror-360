from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_form(snapshot: Snapshot) -> None:
    dom = H.main(
        H.search(
            H.form(action="", method="get")(
                H.fieldset(
                    H.legend("Find users"),
                    H.div(
                        H.label(for_="name")("Enter name: "),
                        H.input(type_="text", name="name", id_="name", required=True),
                        H.button("Search"),
                    ),
                    H.div(
                        H.label(for_="company-choice")("Company: "),
                        H.input(
                            list_="companies",
                            id_="company-choice",
                            name="company-choice",
                        ),
                    ),
                    H.div(
                        H.label(for_="role-select")("Role: "),
                        H.select(name="roles", id_="rolect-select")(
                            H.optgroup(label="Internal")(
                                H.option(value="admin")("Admin"),
                                H.option(value="analyst")("Analyst"),
                            )
                        ),
                    ),
                    H.div(
                        H.label(for_="search-progress")("Progress: "),
                        H.progress(id_="search-progress", max="100", value="70")("70%"),
                    ),
                    H.div(
                        H.label(for_="search-meter")("Meter: "),
                        H.meter(id_="search-meter", max="100", value="70")("70%"),
                    ),
                    H.div(
                        H.label(for_="comments")("Add some comments: "),
                        H.textarea(id_="comments", name="comments", rows=3),
                    ),
                ),
            ),
        ),
        H.datalist(id_="companies")(
            H.option(value="Alpha"),
            H.option(value="Beta"),
        ),
        H.output(name="result", for_="name")("John Doe"),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
