from subprocess import Popen, DEVNULL
import aiohttp
import asyncio
from typing import TypedDict, Optional, Any
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Input, Static
from textual import events
from selectolax.parser import HTMLParser
from pathlib import Path


class TorrentItem(TypedDict):
    title: str
    size: str
    date: str
    magnet: str


class FileAttributes(TypedDict):
    symlink: bool
    hidden: bool
    padding: bool
    executable: bool


class TorrentFile(TypedDict):
    name: str
    components: list[str]
    length: int
    included: bool
    attributes: FileAttributes


class TorrentDetails(TypedDict):
    id: int
    info_hash: str
    name: str
    output_folder: str
    files: list[TorrentFile]


class TorrentResponse(TypedDict):
    id: int
    details: TorrentDetails
    output_folder: str
    seen_peers: Optional[Any]


class WatchButton(Button):
    def __init__(self, magnet: str):
        super().__init__("PLAY", classes="watch-btn")
        self.magnet = magnet
        self.compact = False


class SearchBox(Horizontal):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.current_search_task: Optional[asyncio.Task[None]] = None

    def compose(self) -> ComposeResult:
        yield Input(classes="input")
        yield Static("[bold]ANITRACK[/bold]", classes="logo")

    async def on_input_submitted(self):
        input = self.query_one(Input)

        # Cancel any existing search
        if self.current_search_task and not self.current_search_task.done():
            self.current_search_task.cancel()

        # Start new search in background
        self.current_search_task = asyncio.create_task(
            self.scrape_nyaa_subsplease(input.value)
        )

    async def scrape_nyaa_subsplease(self, query: str):
        url = f"https://nyaa.si/user/subsplease?f=0&c=0_0&q={query}+1080p"
        timeout = aiohttp.ClientTimeout(total=2)
        results_table = self.screen.query_one("#results", Results)

        # Clear previous results and show loading
        results_table.remove_children()
        loading_msg = Static("Searching...", classes="loading-msg")
        results_table.mount(loading_msg)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    # Remove loading message
                    results_table.remove_children()

                    html = await response.text()
                    tree = HTMLParser(html)
                    results: list[TorrentItem] = []
                    for node in tree.css("tr.success"):
                        title_node = node.css_first("td:nth-child(2) a:not(.comments)")
                        magnet_node = node.css_first('a[href^="magnet"]')
                        size_node = node.css_first("td:nth-child(4)")
                        date_node = node.css_first("td[data-timestamp]")

                        if title_node and magnet_node and size_node and date_node:
                            title = title_node.text() or ""
                            magnet = magnet_node.attributes.get("href") or ""
                            size = size_node.text() or ""
                            date = date_node.text() or ""
                            results.append(
                                TorrentItem(
                                    title=title, size=size, date=date, magnet=magnet
                                )
                            )

                            watch_btn = WatchButton(magnet)
                            results_table.add_result(watch_btn, title, size, date)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            results_table.remove_children()
            error_msg = Static(
                "Connection failed. Check VPN connection.", classes="error-msg"
            )
            results_table.mount(error_msg)
        except asyncio.CancelledError:
            # Search was cancelled by new search, do nothing
            pass


class Results(VerticalScroll, can_focus=True):
    def add_result(
        self, watch_btn: WatchButton, title: str, size: str, date: str
    ) -> None:
        title_widget = Static(f"[bold]{title}[/bold]", classes="result-item title-col")
        size_widget = Static(size, classes="result-item size-col")
        date_widget = Static(date, classes="result-item date-col")

        row = Horizontal(
            watch_btn, title_widget, size_widget, date_widget, classes="result-row"
        )
        self.mount(row)

    async def on_button_pressed(self, event: WatchButton.Pressed) -> None:
        if not isinstance(event.button, WatchButton):
            return

        # Start streaming in background task
        asyncio.create_task(self._start_stream(event.button.magnet))

    async def _start_stream(self, magnet: str):
        url = "https://api.anitrack.frixaco.com/torrents"
        timeout = aiohttp.ClientTimeout(total=2)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, data=magnet) as response:
                    torrent_info: TorrentResponse = await response.json()
                    stream_url = f"https://api.anitrack.frixaco.com/torrents/{torrent_info['details']['info_hash']}/stream/{len(torrent_info['details']['files']) - 1}"

                    _ = Popen(["mpv", stream_url], stdout=DEVNULL, stderr=DEVNULL)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            error_msg = Static(
                "Streaming failed. Check VPN connection.", classes="error-msg"
            )
            self.mount(error_msg)


class AnitrackApp(App[str]):
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    CSS_PATH = str(Path(__file__).parent / "styles.tcss")

    def compose(self) -> ComposeResult:
        yield SearchBox(id="searchBox")
        yield Results(id="results")

    def on_mount(self) -> None:
        pass

    async def action_quit(self) -> None:
        self.exit("Anitrack quit.")

    def on_key(self, event: events.Key) -> None:
        pass


def main() -> None:
    app = AnitrackApp()
    exit_msg = app.run()
    print(exit_msg)
