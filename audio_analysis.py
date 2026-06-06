import numpy as np

from essentia.standard import MusicExtractor

from sklearn.metrics.pairwise import cosine_similarity


def extract_features(filepath):
    try:

        extractor = MusicExtractor(
            lowlevelStats=["mean"],
            rhythmStats=["mean"],
            tonalStats=["mean"]
        )

        features, features_frames = extractor(
            filepath
        )

        vector = []

        # ---------- RHYTHM ----------
        vector.append(
            features["rhythm.bpm"]
        )

        # ---------- LOUDNESS ----------
        vector.append(
            features[
                "lowlevel.average_loudness"
            ]
        )

        # ---------- SPECTRAL ----------
        vector.append(
            features[
                "lowlevel.spectral_centroid.mean"
            ]
        )

        vector.append(
            features[
                "lowlevel.spectral_rolloff.mean"
            ]
        )

        vector.append(
            features[
                "lowlevel.zero_crossing_rate.mean"
            ]
        )
        # ---------- MFCC ----------
        mfcc = features[
            "lowlevel.mfcc.mean"
        ]
        vector.extend(mfcc)
        return np.array(
            vector,
            dtype=np.float32
        )

    except Exception as e:
        print(
            f"Ошибка анализа "
            f"{filepath}: {e}"
        )
        return None


def build_similarity_graph(
    system,
    threshold=0.85
):
    tracks = system.table.values()
    vectors = {}
    print(
        "\nИзвлечение аудио-признаков..."
    )
    # ---------- FEATURES ----------
    for track in tracks:

        if not track.filepath:
            continue
        print(
            f"Анализ: "
            f"{track.title}"
        )
        vec = extract_features(
            track.filepath
        )
        if vec is not None:
            vectors[track.id] = vec
    print(
        f"\nУспешно обработано: "
        f"{len(vectors)}"
    )
    # ---------- SIMILARITY ----------
    track_ids = list(
        vectors.keys()
    )
    created = 0
    for i in range(len(track_ids)):
        for j in range(i + 1, len(track_ids)):
            id1 = track_ids[i]
            id2 = track_ids[j]
            vec1 = vectors[id1]
            vec2 = vectors[id2]
            similarity = cosine_similarity(
                [vec1],
                [vec2]
            )[0][0]
            if similarity >= threshold:
                system.connect_tracks(
                    id1,
                    id2,
                    float(similarity)
                )
                created += 1
                print(
                    f"Связь: "
                    f"{id1} <-> {id2} "
                    f"({similarity:.3f})"
                )
    print(
        f"\nСоздано связей: "
        f"{created}"
    )