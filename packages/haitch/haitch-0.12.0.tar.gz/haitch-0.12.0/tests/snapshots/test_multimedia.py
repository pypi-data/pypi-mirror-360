from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_multimedia(snapshot: Snapshot) -> None:
    dom = H.fragment(
        H.video(
            H.source(src="friday.webm", type_="video/webm"),
            H.track(default=True, src="friday.vtt"),
        ),
        H.figure(
            H.img(src="elephant.jpg", alt="Elephant at sunset"),
            H.figcaption("An elephant at sunset"),
        ),
        H.picture(
            H.source(srcset="surfer.jpg"),
            H.img(src="wave.jpg", alt="Tidal wave"),
        ),
        H.audio(controls=True, src="roar.mp3"),
        H.object(type="video/mp4", data="flower.mp4"),
        H.canvas(width=120, height=120)("Alternative text describing canvas."),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
