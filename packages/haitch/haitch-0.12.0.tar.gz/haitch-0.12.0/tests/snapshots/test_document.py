from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_document(snapshot: Snapshot) -> None:
    styles = """
    .inline {
        color: grey;
    }
    """
    dom = H.html(lang="en")(
        H.head(
            H.meta(charset="utf-8"),
            H.meta(name="viewport", content="width=device-width, initial-scale=1"),
            H.meta(http_equiv="x-ua-compatible", content="ie=edge"),
            H.title("Basic page"),
            H.link(href="main.css", rel="stylesheet"),
            H.link(href="custom.css", rel="stylesheet"),
            H.script(src="main.js", defer=True),
            H.style(styles),
        ),
        H.body(class_="container")(
            H.dialog(open=True)("Hi there!"),
            H.noscript("JavaScript is not enabled. Good job."),
            H.div(
                H.a(href="#")("Hyperlink"),
                H.hr(),
                H.br(),
                H.ol(
                    H.li(H.data(value="1")("First point")),
                    H.li(H.data(value="2")("Second point")),
                ),
            ),
            H.h3("Code"),
            H.div(
                H.code("print('code block')"),
                H.del_(
                    H.p("print('hello, world.')"),
                ),
                H.ins(
                    H.p("print('code block')"),
                ),
                H.samp("code block"),
                H.p(
                    H.var("print"),
                    " is a builtin function in Python.",
                ),
            ),
            H.h3("Template and slot"),
            H.template(
                H.slot(name="attributes")(H.p("None")),
            ),
            H.h3("Inline formatting"),
            H.p(
                "This document has ",
                H.abbr("CSS"),
                "(Cascading Style Sheets) in the head element.",
            ),
            H.div(class_="inline")(
                H.p("This is a ", H.mark("mark"), "."),
                H.p("This is with ", H.em("emphasis"), "."),
                H.p("This is with ", H.s("strikethrough"), "."),
                H.p("This is with ", H.b("attention"), "."),
                H.p("This is ", H.strong("strong"), "."),
                H.p("This is ", H.i("idiomatic"), "."),
                H.p("This is ", H.u("unarticulated"), "."),
                H.p("This is a", H.q("quote"), "."),
                H.p("This is a", H.sub("subscript"), "."),
                H.p("This is a", H.sup("superscript"), "."),
                H.p("Type ", H.kbd("Ctrl-C"), "to copy."),
                H.p("The date is ", H.time(datetime="2018-07-07")("July 7th")),
                H.address(
                    H.a(href="tel:+141555-0132")("+1 (415) 555-0132"),
                ),
            ),
            H.h3("Description list"),
            H.dl(
                H.dt("Beast of Bodmin"),
                H.dd("A large feline inhabiting Bodmin Moor."),
                H.dt("Morgawr"),
                H.dd("A sea serpent."),
            ),
            H.pre("print('hello, world')"),
            H.unsafe("You can pass <i>raw</i> HTML with unsafe tag."),
            H.h3("Language specific"),
            H.ruby(
                " 明日 ",
                H.rp("("),
                H.rt("Ashita"),
                H.rp(")"),
            ),
            H.bdo(dir="ltr")("אה, אני אוהב להיות ליד חוף הים"),
            H.bdi("الرجل القوي إيان"),
        ),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
