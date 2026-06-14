from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical
from textual.containers import Horizontal
from main import MusicSystem
from track import Track
import os
TEST_TRACKS = """
1|Numb|Linkin Park|Nu Metal|185|5
2|In The End|Linkin Park|Nu Metal|216|5
3|Breaking The Habit|Linkin Park|Alternative Rock|197|5
4|Sonne|Rammstein|Industrial Metal|270|5
5|Du Hast|Rammstein|Industrial Metal|249|5
6|Ich Will|Rammstein|Industrial Metal|217|4
7|Smells Like Teen Spirit|Nirvana|Grunge|301|5
8|Come As You Are|Nirvana|Grunge|219|5
9|Lithium|Nirvana|Grunge|257|4
10|Creep|Radiohead|Alternative Rock|238|5
11|Karma Police|Radiohead|Alternative Rock|261|5
12|No Surprises|Radiohead|Alternative Rock|229|5
13|Gruppa Krovi|Kino|Rock|287|5
14|Pachka Sigaret|Kino|Rock|267|5
15|Zvezda Po Imeni Solntse|Kino|Rock|245|5
16|Bohemian Rhapsody|Queen|Rock|354|5
17|Don't Stop Me Now|Queen|Rock|210|5
18|Another One Bites The Dust|Queen|Rock|215|4
19|Master Of Puppets|Metallica|Thrash Metal|515|5
20|Nothing Else Matters|Metallica|Heavy Metal|388|5
"""
TEST_RELATIONS = """
1|2|0.95
1|5|0.82
1|8|0.70
1|9|0.65
1|10|0.60
1|3|0.30
1|4|0.25

2|5|0.88
2|8|0.75
2|9|0.70
2|10|0.68
2|3|0.28
2|4|0.22

5|8|0.93
5|9|0.90
5|10|0.88
5|1|0.80
5|2|0.78
5|11|0.40

8|9|0.94
8|10|0.92
8|5|0.85
8|2|0.70
8|12|0.55
8|13|0.50

9|10|0.96
9|8|0.93
9|5|0.82
9|2|0.68
9|14|0.45

10|9|0.97
10|8|0.91
10|5|0.84
10|2|0.72
10|15|0.42

3|4|0.90
3|6|0.88
3|7|0.85
3|11|0.60
3|12|0.55
3|1|0.30

4|6|0.92
4|7|0.90
4|3|0.88
4|13|0.58
4|14|0.50
4|2|0.25

6|7|0.95
6|3|0.87
6|4|0.93
6|15|0.60
6|16|0.55
6|11|0.40

7|6|0.94
7|4|0.89
7|3|0.83
7|17|0.58
7|18|0.52
7|12|0.38

11|12|0.92
11|13|0.88
11|14|0.85
11|15|0.80
11|3|0.60
11|5|0.35

12|13|0.93
12|14|0.90
12|15|0.87
12|16|0.83
12|8|0.50
12|6|0.45

13|14|0.94
13|15|0.91
13|16|0.88
13|17|0.84
13|4|0.55
13|7|0.50

14|15|0.95
14|16|0.92
14|17|0.89
14|18|0.86
14|9|0.48
14|10|0.40

15|16|0.96
15|17|0.93
15|18|0.90
15|19|0.87
15|10|0.42
15|5|0.38

16|17|0.97
16|18|0.94
16|19|0.91
16|20|0.88
16|6|0.50
16|12|0.45

17|18|0.98
17|19|0.95
17|20|0.92
17|7|0.48
17|13|0.44
17|15|0.60

18|19|0.96
18|20|0.93
18|17|0.90
18|14|0.55
18|16|0.52
18|8|0.40

19|20|0.97
19|18|0.94
19|17|0.91
19|15|0.88
19|16|0.85
19|9|0.45

20|19|0.98
20|18|0.95
20|17|0.92
20|16|0.89
20|14|0.60
20|10|0.50
"""
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
class LoadDirectoryScreen(ModalScreen):
    def compose(self):
        yield Vertical(
            Label("Введите абсолютный путь к папке с музыкой"),
            Input(
                placeholder="/home/user/Music или C:\\Music",
                id="path"
            ),
            Button("Загрузить", id="submit"),
            Button("Отмена", id="cancel"),
        )

    def on_button_pressed(self, event):
        if event.button.id == "cancel":
            self.dismiss(None)
            return

        path = self.query_one("#path").value.strip()

        if not path:
            self.notify("Введите путь")
            return

        self.dismiss(path)
class ReadMeScreen(ModalScreen):
    def compose(self):
        yield Vertical(
            Label(
                """Это программа для анализа музыки.

Чтобы протестировать базовые функции,
нажмите t и l, а затем попробуйте вывести
рекомендации для одного из первых 20 треков.

Так же вы можете подгрузить музыку из своей папки,
для этого нажмите "load ~/Music".

Чтобы добавить связь между музыкой,
нажмите "connect_tracks".
"""
            ),
            Button("Закрыть", id="close")
        )

    def on_button_pressed(self, event):
        self.dismiss()
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
        ("o", "load_from_directory", "Load ~/Music1"),
        ("q", "quit", "Quit"),
        ("k", "clear", "Clear everything"),
        ("y", "show_readme", "Read me"),
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
        result = self.system.load_from_string(TEST_TRACKS)
        self.load_tracks()
        self.notify(f"Загружено треков: {result}")
    def action_clear(self):
        self.system.clear()
        self.load_tracks()
        self.recommendations.clear()
        self.notify("Всё очищено")

    def action_load_test_relations(self):
        result = self.system.load_relations_from_string(TEST_RELATIONS)
        self.notify(f"Загружено треков: {result}")

    def action_load_from_directory(self):
        self.push_screen(
            LoadDirectoryScreen(),
            self.directory_selected
        )

    def action_show_readme(self):
        self.push_screen(ReadMeScreen())
    def relation_added(self, data):
        if data is None:
            return
        self.system.add_relation(
            data["id1"],
            data["id2"],
            data["weight"]
        )
        self.notify("Связь добавлена")

    def directory_selected(self, path):
        if path is None:
            return

        path = os.path.abspath(path)

        if not os.path.isdir(path):
            self.notify("Папка не существует")
            return

        loaded = self.system.load_from_directory(path)

        self.notify(str(loaded))
        self.load_tracks()
if __name__ == "__main__":
    app = MusicApp()
    app.run()
