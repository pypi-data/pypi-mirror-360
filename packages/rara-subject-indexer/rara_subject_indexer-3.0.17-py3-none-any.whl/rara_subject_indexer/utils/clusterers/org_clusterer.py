import regex as re
from typing import Dict, List, NoReturn, Tuple
from jellyfish import jaro_winkler_similarity as jw
from rara_subject_indexer.utils.clusterers.base_clusterer import BaseClusterer
from rara_subject_indexer.config import DEFAULT_ORG_SIMILARITY_THRESHOLD, LOGGER


class OrganizationClusterer(BaseClusterer):
    def __init__(
            self, 
            similarity_threshold: float = DEFAULT_ORG_SIMILARITY_THRESHOLD
    ) -> NoReturn:
        BaseClusterer.__init__(self, similarity_threshold)

        self.patterns = {
            "AS": r"(?<=(^|\W))(AS\W?(i|ile|ilt|lt|le|ga|iga|st|ist)?|aktsiaselts\w{,4})(?=$|\W)",
            "OÜ": r"(?<=(^|\W))(OÜ\W?(le|lt|ga|d|st)?|osaühing\w{,4})(?=$|\W)",
            "MTÜ": r"(?<=(^|\W))(MTÜ\W?(le|lt|ga|d|st)?|mittetulundusühing\w{,4})(?=$|\W)",
            "SA": r"(?<=(^|\W))(SA\W?(le|lt|ga|d|st)?|sihtasutus\w{,4})(?=$|\W)",
            "KÜ": r"(?<=(^|\W))(KÜ\W?(le|lt|ga|d|st)?|korteriühistu\w{,4})(?=$|\W)",
            "THE": r"(?<=(^|\W))(T|the)(?=$|\W)"
        }
        self.org_indicator = "|".join(list(self.patterns.values()))

        self.equivalence_patterns = [
            r"(pank|panga\w{,2})"
        ]

    def remove_org_indicator(self, word: str) -> str:
        return re.sub(self.org_indicator, '', word, flags=re.IGNORECASE).strip()

    def generate_cluster_key(self, word: str) -> str:
        cluster_key = self.remove_org_indicator(word)
        return cluster_key

    def are_equivalent(self, key_1: str, key_2: str) -> bool:
        key_1 = self.remove_org_indicator(key_1)
        key_2 = self.remove_org_indicator(key_2)

        if jw(key_1, key_2) > self.similarity_threshold:
            return True

        for pattern in self.equivalence_patterns:
            if re.match(pattern, key_1) and re.match(pattern, key_2):
                return True

        return False

    def final_merge_org_clusters(self, clusters: dict) -> dict:
        """ Custom (additional) merger function for organizations.
        """
        keys = list(clusters.keys())
        final_clusters = {}
        for i, key in enumerate(keys):
            if i == 0:
                final_clusters[key] = clusters[key]
            else:
                added = False
                for final_key in final_clusters:
                    if self.are_equivalent(key, final_key):
                        final_clusters[final_key].extend(clusters[key])
                        added = True
                        break
                if not added:
                    final_clusters[key] = clusters[key]
        return final_clusters

    def cluster(self, words: List[str]) -> Dict[str, List[str]]:
        """Finds clusters of similar strings."""
        LOGGER.debug(f"Clustering organizations.")
        init_clusters = self.get_init_clusters(words)
        merged_clusters = self.merge_clusters(init_clusters)
        clusters = self.final_merge_org_clusters(merged_clusters)
        extended_clusters = self.update_cluster_heads(clusters)
        return extended_clusters
