import regex as re
from typing import Dict, List, NoReturn, Tuple
from jellyfish import jaro_winkler_similarity as jw
from rara_subject_indexer.utils.clusterers.base_clusterer import BaseClusterer
from rara_subject_indexer.config import DEFAULT_TITLE_SIMILARITY_THRESHOLD, LOGGER


class TitleClusterer(BaseClusterer):
    def __init__(
        self, 
        similarity_threshold: float = DEFAULT_TITLE_SIMILARITY_THRESHOLD
    ) -> NoReturn:
        BaseClusterer.__init__(self, similarity_threshold)

    def generate_cluster_key(self, word: str) -> str:
        return word

    def are_equivalent(self, key_1: str, key_2: str) -> bool:
        if jw(key_1, key_2) > self.similarity_threshold:
            return True
        return False
    
    def final_merge(self, clusters: dict) -> dict:
        """ Custom (additional) merger function.
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
        """Finds clusters of similar strings.
        """
        LOGGER.debug(f"Clustering titles.")
        init_clusters = self.get_init_clusters(words)
        clusters = self.merge_clusters(init_clusters)
        extended_clusters = self.update_cluster_heads(clusters)
        final_clusters = self.final_merge(extended_clusters)
        return dict(final_clusters)
