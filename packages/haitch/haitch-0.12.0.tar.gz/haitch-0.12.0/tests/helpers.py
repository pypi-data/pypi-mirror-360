import inspect
from typing import Union

from bs4 import BeautifulSoup as bs
from bs4.formatter import HTMLFormatter

from haitch import SupportsHtml


def prettify(dom: SupportsHtml) -> Union[str, bytes]:
    """Pretty format rendered HTML to make it easier to spot diffs."""
    formatter = HTMLFormatter(indent=2, empty_attributes_are_booleans=True)
    soup = bs(str(dom), features="html.parser")
    return soup.prettify(formatter=formatter)


def get_snapshot_name() -> str:
    """Derive the snapshot name based on test function name."""
    function_name = inspect.currentframe().f_back.f_code.co_name  # type: ignore
    return f"{function_name}.html"
