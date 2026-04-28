from src.utils.keyword_extractor import extract_keywords
from src.utils.scene_mapper import map_scene


class MediaAgent:

    def __init__(self, providers):
        self.providers = providers
        self.used_paths = set()

    def select_media(self, query, index):

        print(f"[MEDIA] Scene #{index} searching for: {query}")

        # Get scene based search queries
        scene_queries = map_scene(query)

        # Also extract keywords
        keywords = extract_keywords(query)

        search_queries = scene_queries + keywords

        search_queries = list(dict.fromkeys(search_queries))

        print(f"[INFO] Scene #{index} search queries:", search_queries)

        duplicate_paths = []

        for search_query in search_queries:

            for provider in self.providers:

                try:

                    print(
                        f"[SEARCH] Searching '{search_query}' using {provider.__class__.__name__}"
                    )

                    path = provider.get_video(search_query, index)

                    if path and path not in self.used_paths:
                        self.used_paths.add(path)

                        print(
                            f"[OK] Video found using {provider.__class__.__name__}: {path}"
                        )

                        return path
                    elif path:
                        print(f"[WARN] Duplicate media skipped: {path}")
                        duplicate_paths.append(path)

                except Exception as e:

                    print(
                        f"[WARN] Provider error from {provider.__class__.__name__}:",
                        e
                    )

        if duplicate_paths:
            reused_path = duplicate_paths[0]
            print(f"[WARN] Reusing duplicate media for scene #{index}: {reused_path}")
            return reused_path

        print("[ERROR] No video found for:", query)

        return None