import pytest

import haitch as H


def test_element():
    got = str(H.div(style="color:red;")("Hello, world!"))
    want = '<div style="color:red;">Hello, world!</div>'
    assert got == want


def test_made_up_tag():
    got = str(H.foo())
    want = "<foo></foo>"
    assert got == want


def test_no_attrs():
    got = str(H.div("Hello, world!"))
    want = "<div>Hello, world!</div>"
    assert got == want


def test_strip_reserved_word_attr():
    got = str(H.button(class_="btn")("Click me!"))
    want = '<button class="btn">Click me!</button>'
    assert got == want


def test_boolean_attr():
    got = str(H.div(autofocus=True)("Hello, world!"))
    want = "<div autofocus>Hello, world!</div>"
    assert got == want


def test_false_attr_value_is_filtered_out():
    got = str(H.div(autofocus=False)("Hello, world!"))
    want = "<div>Hello, world!</div>"
    assert got == want


def test_html_tag_prepends_doctype():
    got = str(H.html())
    want = "<!doctype html><html></html>"
    assert got == want


def test_escape_attr():
    got = str(H.div(class_="<br/>"))
    want = '<div class="&lt;br/&gt;"></div>'
    assert got == want


def test_escape_child():
    got = str(H.div("<br>"))
    want = "<div>&lt;br&gt;</div>"
    assert got == want


@pytest.mark.parametrize("value", [1.0, ["1"], ("1",)])
def test_bad_attr_value(value):
    exc = f"Attribute value must be `str`, `int`, or `bool`, not {type(value)}"
    with pytest.raises(ValueError, match=exc):
        str(H.div(id_=value))


@pytest.mark.parametrize("child", [1, 1.0, True])
def test_bad_child_value(child):
    exc = f"Invalid child type: {type(child)}"
    with pytest.raises(ValueError, match=exc):
        str(H.div(child))


def test_nested_elements():
    dom = H.p(autofocus=True)(
        H.label(for_="num")("#"),
        H.input(name="num", type_="text", id_="my-num"),
    )

    got = str(dom)
    want = '<p autofocus><label for="num">#</label><input name="num" type="text" id="my-num"/></p>'

    assert got == want


def test_handle_nested_iterable():
    dom = H.ul()(
        [H.li(str(n)) for n in range(3)],
    )

    got = str(dom)
    want = "<ul><li>0</li><li>1</li><li>2</li></ul>"

    assert got == want


def test_include_child_when_condition_met():
    is_greeting = True
    dom = H.div(is_greeting and H.h1("Welcome!"))

    got = str(dom)
    want = "<div><h1>Welcome!</h1></div>"

    assert got == want


@pytest.mark.parametrize("items", [[], tuple(), set(), False, None])
def test_false_or_none_excludes_child(items):
    dom = H.div(items and H.h1("Found items!"))

    got = str(dom)
    want = "<div></div>"

    assert got == want


def test_void_element_with_extra_attrs():
    el = H.img(
        src="photo.png",
        alt="My image",
        extra_attrs={"foo": "bar"},
    )

    got = str(el)
    want = '<img src="photo.png" alt="My image" foo="bar"/>'

    assert got == want
