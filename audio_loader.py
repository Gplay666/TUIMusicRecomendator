import os
import subprocess
import json

from track import Track


AUDIO_EXTENSIONS = {
    ".mp3",
    ".flac",
    ".ogg",
    ".wav",
    ".m4a"
}


def probe_file(path: str):
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        path
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    return json.loads(result.stdout)


def safe_tag(tags, key, default):
    value = tags.get(key)

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


def extract_metadata(probe_data, filename):
    if not probe_data:
        return None

    fmt = probe_data.get("format", {})
    tags = fmt.get("tags", {})

    title = safe_tag(
        tags,
        "title",
        os.path.splitext(filename)[0]
    )

    artist = safe_tag(
        tags,
        "artist",
        "Unknown"
    )

    genre = safe_tag(
        tags,
        "genre",
        "Unknown"
    )

    duration = int(
        float(fmt.get("duration", 0))
    )

    # fallback:
    # "Artist - Title.mp3"
    if artist == "Unknown":
        name = os.path.splitext(filename)[0]

        if " - " in name:
            parts = name.split(" - ", 1)

            if len(parts) == 2:
                artist = parts[0].strip()
                title = parts[1].strip()

    return (
        title,
        artist,
        genre,
        duration
    )


def scan_music_directory(directory: str, system):
    loaded = 0

    auto_id = len(
        system.table.values()
    ) + 1

    for root, _, files in os.walk(directory):

        for file in files:

            ext = os.path.splitext(file)[1].lower()

            if ext not in AUDIO_EXTENSIONS:
                continue

            path = os.path.join(root, file)

            try:
                probe = probe_file(path)

                meta = extract_metadata(
                    probe,
                    file
                )

                if not meta:
                    continue

                (
                    title,
                    artist,
                    genre,
                    duration
                ) = meta

                track = Track(
                    track_id=str(auto_id),
                    title=title,
                    artist=artist,
                    genre=genre,
                    duration=duration,
                    rating=5,
                    filepath = path
                )

                system.add_track(track)

                loaded += 1
                auto_id += 1

            except Exception as e:
                print(
                    f"Ошибка загрузки {file}: {e}"
                )

    return loaded