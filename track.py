class Track:
    def __init__(self, track_id, title, artist, genre, duration, rating, filepath=None):
        self.id = track_id
        self.title = title
        self.artist = artist
        self.genre = genre
        self.duration = duration
        self.rating = rating
        self.filepath = filepath

    def __repr__(self):
        return (
            f"[{self.id}] "
            f"{self.artist} - {self.title} | "
            f"{self.genre} | "
            f"{self.duration}s | "
            f"rating={self.rating}"
        )