from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical
from textual.containers import Horizontal
from main import MusicSystem, Track
class AddRelationScreen(ModalScreen):
    def compose(self):
        yield Vertical(
            Label("Добавление связи"),
            Input(
                placeholder="ID первого трека",
                id="track1"
            ),
            Input(
                placeholder="ID второго трека",
                id="track2"
            ),
            Input(
                placeholder="Вес связи",
                id="weight",
                value="1"
            ),
            Button("Добавить", id="submit"),
            Button("Отмена", id="cancel"),
        )
    def on_button_pressed(self, event):
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        try:
            data = {
                "id1": self.query_one("#track1").value,
                "id2": self.query_one("#track2").value,
                "weight": float(
                    self.query_one("#weight").value
                )
            }
            self.dismiss(data)
        except ValueError:
            self.notify("Вес должен быть числом")
class AddTrackScreen(ModalScreen):
    def compose(self):
        yield Vertical(
            Label("Добавление трека"),
            Input(placeholder="ID", id="track_id"),
            Input(placeholder="Название", id="title"),
            Input(placeholder="Исполнитель", id="artist"),
            Input(placeholder="Жанр", id="genre"),
            Input(placeholder="Длительность", id="duration"),
            Input(placeholder="Рейтинг", id="rating"),
            Button("Добавить", id="submit"),
            Button("Отмена", id="cancel"),
        )
    def on_button_pressed(self, event):
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        try:
            track = Track(
                self.query_one("#track_id").value,
                self.query_one("#title").value,
                self.query_one("#artist").value,
                self.query_one("#genre").value,
                int(self.query_one("#duration").value),
                int(self.query_one("#rating").value),
            )
            self.dismiss(track)
        except ValueError:
            self.notify("Duration и Rating должны быть числами")
class MusicApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    DataTable {
        height: 1fr;
    }
    """
    BINDINGS = [
        ("a", "add_track", "Add"),
        ("d", "delete_track", "Delete"),
        ("c", "connect_tracks", "Connect"),
        ("r", "show_recommendations", "Recommend"),
        ("t", "load_test_tracks", "Load Tracks"),
        ("l", "load_test_relations", "Load Relations"),
        ("q", "quit", "Quit"),
        ("С", "clear", "Clear everything"),
    ]
    def __init__(self):
        super().__init__()
        self.system = MusicSystem()
        # тестовые данные
        self.system.add_track(
            Track("1", "Numb", "Linkin Park", "Rock", 185, 9)
        )
        self.system.add_track(
            Track("2", "In The End", "Linkin Park", "Rock", 210, 10)
        )
        self.system.add_track(
            Track("3", "After Dark", "Mr.Kitty", "Synthwave", 250, 8)
        )
    def compose(self) -> ComposeResult:
        yield Header()
        self.table = DataTable()
        self.recommendations = DataTable()
        yield Horizontal(
            self.table,
            self.recommendations
        )
        yield Footer()
    def on_mount(self):
        self.table.add_columns(
            "ID",
            "Artist",
            "Title",
            "Genre",
            "Duration",
            "Rating"
        )
        self.recommendations.add_columns(
            "ID",
            "Artist",
            "Title",
            "Rating"
        )
        self.table.cursor_type = "row"
        self.load_tracks()
    def load_tracks(self):
        self.table.clear()

        tracks = sorted(
            self.system.table.values(),
            key=lambda t: int(t.id)
        )
        for track in tracks:
            self.table.add_row(
                track.id,
                track.artist,
                track.title,
                track.genre,
                str(track.duration),
                str(track.rating)
            )
    def track_added(self, track):

        if track is None:
            return
        self.system.add_track(track)
        self.load_tracks()
        self.notify("Трек добавлен")
    def action_add_track(self):
        self.push_screen(
            AddTrackScreen(),
            self.track_added
        )
    def action_delete_track(self):
        row_index = self.table.cursor_row
        if row_index is None:
            self.notify("Трек не выбран")
            return
        row = self.table.get_row_at(row_index)
        track_id = row[0]
        self.system.delete_track(track_id)
        self.load_tracks()
        self.notify(f"Удалён трек {track_id}")
    def action_show_recommendations(self):
        row_index = self.table.cursor_row
        if row_index is None:
            self.notify("Трек не выбран")
            return
        track_id = self.table.get_row_at(row_index)[0]
        recs = self.system.recommend(track_id)
        self.recommendations.clear()
        if not recs:
            self.notify("Нет рекомендаций")
            return
        for t in recs:
            self.recommendations.add_row(
                t.id, t.artist, t.title, str(t.rating)
            )
        self.notify(f"Рекомендаций: {len(recs)}")
        self.notify("Рекомендации обновлены")
    def action_connect_tracks(self):
        self.push_screen(
            AddRelationScreen(),
            self.relation_added
        )
    def action_load_test_tracks(self):
        self.system.load_from_file("testtracks.txt")
        self.load_tracks()
        self.notify("Треки загружены из testtracks.txt")
    def action_clear(self):
        self.system.clear()
        self.load_tracks()
        self.recommendations.clear()
        self.notify("Всё очищено")
    def action_load_test_relations(self):
        self.system.load_relations("testrelationts.txt")
        self.notify("Связи загружены из testrelations.txt")
    def relation_added(self, data):
        if data is None:
            return
        self.system.add_relation(
            data["id1"],
            data["id2"],
            data["weight"]
        )
        self.notify("Связь добавлена")
if __name__ == "__main__":
    app = MusicApp()
    app.run()
