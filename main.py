from grafLib import Graph
from hash_table import HashTable
from sorting import quicksort
from avl_tree import AVLTree
from collections import deque
from audio_loader import scan_music_directory
from track import Track
from audio_analysis import build_similarity_graph

def bfs_recommendations(graph, start, max_depth=2):
    visited = set()
    queue = deque([(start, 0, 1.0)])  # (node, depth, score)
    visited.add(start)
    scores = {}  # node -> accumulated weight score
    while queue:
        node, depth, score = queue.popleft()
        if 0 < depth <= max_depth:
            if node not in scores:
                scores[node] = 0
            scores[node] += score
        if depth >= max_depth:
            continue
        for neighbor in graph.nodes.get(node, []):
            if neighbor in visited:
                continue
            # найти вес ребра
            weight = 1.0
            for e in graph.edges:
                if (e["from"] == node and e["to"] == neighbor) or \
                   (not graph.directed and e["from"] == neighbor and e["to"] == node):
                    weight = e["weight"]
                    break
            visited.add(neighbor)
            new_score = score * weight * 0.6
            queue.append((neighbor, depth + 1, new_score))
    # сортируем по “важности рекомендации”
    sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [node for node, _ in sorted_nodes]

class MusicSystem:
    def __init__(self):
        self.table = HashTable(100)
        self.tree = AVLTree()
        self.graph = Graph(directed=False)
    def add_track(self, track):
        if self.table.find(track.id):
            return False
        self.table.insert(track.id, track)
        self.tree.insert((track.rating, track.id))
        self.graph.add_node(track.id)
        return True
    def find_track(self, track_id):
        return self.table.find(track_id)
    def delete_track(self, track_id):
        track = self.table.find(track_id)
        if not track:
            return False
        self.table.delete(track_id)
        self.tree.delete((track.rating, track.id))
        self.graph.remove_node(track_id)
        return True
    def load_from_directory(self, directory: str):
        loaded = scan_music_directory(directory,self)
        #build_similarity_graph(self)
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"Edges: {len(self.graph.edges)}\nNodes: {len(self.graph.nodes)}\n")
        return (f"Загружено треков: {loaded}")
    def load_from_file(self, filename):
        try:
            loaded = 0
            with open(filename, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    if len(parts) != 6:
                        return f"Ошибка в строке {line_number}: неверный формат."
                        continue
                    try:
                        track_id = parts[0]
                        title = parts[1]
                        artist = parts[2]
                        genre = parts[3]
                        duration = int(parts[4])
                        rating = int(parts[5])
                        track = Track(
                            track_id,
                            title,
                            artist,
                            genre,
                            duration,
                            rating
                        )
                        self.add_track(track)
                        loaded += 1
                    except ValueError:
                        print(
                            f"Ошибка в строке {line_number}: "
                            f"duration/rating должны быть числами."
                        )
            print(f"\nЗагружено треков: {loaded}")
        except FileNotFoundError:
            return "Файл не найден"

    def load_from_string(self, text):
        loaded = 0

        for line_number, line in enumerate(
                text.splitlines(),
                start=1
        ):
            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            if len(parts) != 6:
                continue

            try:
                track = Track(
                    parts[0],
                    parts[1],
                    parts[2],
                    parts[3],
                    int(parts[4]),
                    int(parts[5])
                )

                self.add_track(track)
                loaded += 1

            except ValueError:
                continue

        return loaded

    def load_relations_from_string(self, text):
        loaded = 0

        for line_number, line in enumerate(
                text.splitlines(),
                start=1
        ):
            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            if len(parts) < 2:
                print(
                    f"Ошибка в строке {line_number}: "
                    f"неверный формат."
                )
                continue

            a = parts[0]
            b = parts[1]

            weight = 1.0

            if len(parts) >= 3 and parts[2]:
                try:
                    weight = float(parts[2])
                except ValueError:
                    print(
                        f"Ошибка в строке {line_number}: "
                        f"вес должен быть числом."
                    )
                    continue

            if self.table.find(a) is None:
                print(f"Трек {a} не найден.")
                continue

            if self.table.find(b) is None:
                print(f"Трек {b} не найден.")
                continue

            self.add_relation(a, b, weight)
            loaded += 1

        return f"Загружено связей: {loaded}"
    def load_relations(self, filename):
        try:
            loaded = 0
            with open(filename, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    # минимум 2 поля: id1, id2
                    if len(parts) < 2:
                        print(f"Ошибка в строке {line_number}: неверный формат")
                        continue
                    a = parts[0]
                    b = parts[1]
                    weight = 1.0
                    if len(parts) >= 3 and parts[2] != "":
                        try:
                            weight = float(parts[2])
                        except ValueError:
                            print(f"Ошибка в строке {line_number}: вес должен быть числом")
                            continue
                    # проверка существования треков
                    if self.table.find(a) is None or self.table.find(b) is None:
                        print(f"Связь {a}-{b} пропущена: трек не найден.")
                        continue
                    self.connect_tracks(a, b, weight)
                    loaded += 1
            return f"\nЗагружено связей: {loaded}"
        except FileNotFoundError:
            return "Файл не найден."
    def add_relation(self, id1, id2, weight=1):
        if not self.table.find(id1):
            return "Первый трек не найден."
        if not self.table.find(id2):
            return "Второй трек не найден."
        self.graph.add_edge(id1, id2, weight)
        return "Связь добавлена."
    def show_sorted(self):
        pairs = self.tree.inorder()
        print("\n=== Треки по рейтингу ===")
        for rating, track_id in reversed(pairs):
            track = self.table.find(track_id)
            print(track)

    def recommend(self, track_id):
        ids = bfs_recommendations(self.graph, track_id)
        tracks = []
        for tid in ids:
            track = self.table.find(tid)
            if track:
                tracks.append(track)
        return tracks
    def generate_report(self):
        tracks = self.table.values()
        sorted_tracks = quicksort(
            tracks,
            key=lambda t: t.rating
        )
        print("\n=== Отчёт ===")
        for track in reversed(sorted_tracks):
            print(track)
    def connect_tracks(self, a, b, weight=1):
        if a not in self.graph.nodes:
            self.graph.add_node(a)
        if b not in self.graph.nodes:
            self.graph.add_node(b)
        self.graph.add_edge(a, b, weight)
    def print_tracks(self, tracks):
        if not tracks:
            print("Список пуст.")
            return
        print("\n" + "=" * 90)
        print(
            f"{'ID':<6}"
            f"{'Исполнитель':<20}"
            f"{'Название':<25}"
            f"{'Жанр':<15}"
            f"{'Длит.':<10}"
            f"{'Рейт.':<8}"
        )
        print("=" * 90)
        for track in tracks:
            print(
                f"{track.id:<6}"
                f"{track.artist[:18]:<20}"
                f"{track.title[:23]:<25}"
                f"{track.genre[:13]:<15}"
                f"{str(track.duration) + 's':<10}"
                f"{track.rating:<8}"
            )
        print("=" * 90)
    def show_all_tracks(self):
        tracks = self.table.values()
        if not tracks:
            return "Треков нет"
        sorted_tracks = sorted(tracks, key=lambda t: int(t.id)) #Шобы хеш не портил мне порядок
        self.print_tracks(sorted_tracks)

    def search_by_title(self, query):
        result = []
        for track in self.table.values():
            if query.lower() in track.title.lower():
                result.append(track)
            self.print_tracks(result)
    def clear(self):
        self.table = HashTable(100)
        self.tree = AVLTree()
        self.graph = Graph(directed=False)
def main():
    system = MusicSystem()
    # тестовые данные
    system.add_track(Track("1", "Numb", "Linkin Park", "Rock", 185, 9))
    system.add_track(Track("2", "In The End", "Linkin Park", "Rock", 210, 10))
    system.add_track(Track("3", "After Dark", "Mr.Kitty", "Synthwave", 250, 8))
    system.add_relation("1", "2")
    system.add_relation("2", "3")
    while True:
        print("\n==============================")
        print(" Музыкальная система")
        print("==============================")
        print("1 - Добавить трек")
        print("2 - Найти трек")
        print("3 - Удалить трек")
        print("4 - Добавить связь")
        print("5 - Показать сортировку")
        print("6 - Рекомендации")
        print("7 - Отчёт")
        print("8 - Загрузить треки")
        print("9 - Загрузить связи")
        print("10 - Показать все треки")
        print("11 - Поиск по названию")
        print("0 - Выход")
        choice = input("\n> ")
        if choice == "1":
            track_id = input("ID: ")
            title = input("Название: ")
            artist = input("Исполнитель: ")
            genre = input("Жанр: ")
            try:
                duration = int(input("Длительность: "))
                rating = int(input("Рейтинг: "))
            except ValueError:
                print("Неверный ввод.")
                continue
            track = Track(
                track_id,
                title,
                artist,
                genre,
                duration,
                rating
            )
            system.add_track(track)
        elif choice == "2":
            track_id = input("ID трека: ")
            track = system.find_track(track_id)
            if track:
                print(track)
            else:
                print("Не найден.")
        elif choice == "3":
            track_id = input("ID трека: ")
            system.delete_track(track_id)
        elif choice == "4":
            id1 = input("Первый трек: ")
            id2 = input("Второй трек: ")
            system.add_relation(id1, id2)
        elif choice == "5":
            system.show_sorted()
        elif choice == "6":
            track_id = input("ID трека: ")
            system.recommend(track_id)
        elif choice == "7":
            system.generate_report()
        elif choice == "8":
            filename = input("Файл треков: ")
            system.load_from_file(filename)
        elif choice == "9":
            filename = input("Файл связей: ")
            system.load_relations(filename)
        elif choice == "10":
            system.show_all_tracks()
        elif choice == "11":
            query = input("Название: ")
            system.search_by_title(query)
        elif choice == "0":
            print("Выход...")
            break
        else:
            print("Неизвестная команда.")

if __name__ == "__main__":
    main()
