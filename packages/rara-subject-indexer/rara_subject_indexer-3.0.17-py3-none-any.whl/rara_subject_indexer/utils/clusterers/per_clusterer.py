import regex as re
import sys
from collections import defaultdict
from typing import Dict, List, NoReturn
from jellyfish import jaro_winkler_similarity as jw
from rara_subject_indexer.utils.clusterers.base_clusterer import BaseClusterer
from rara_subject_indexer.config import DEFAULT_PER_SIMILARITY_THRESHOLD, LOGGER

class PersonaClusterer(BaseClusterer):
    def __init__(
            self, 
            similarity_threshold: float = DEFAULT_PER_SIMILARITY_THRESHOLD
    ) -> NoReturn:
        BaseClusterer.__init__(self, similarity_threshold)
        self.first_word_key_prefix_length = 5
        self.key_prefix_length = 3
        self.init_pattern = re.compile(r"^\w\.?( ?\w\.?)?$")  # for detecting E. / J.K etc

    def has_init_match(self, word: str) -> bool:
        word_tokens = [w.strip() for w in word.split()]
        if len(word_tokens) > 1 and re.match(self.init_pattern, word_tokens[0]):
            return True
        return False

    def clean_key(self, key: str) -> str:
        key_tokens = [w.strip() for w in key.split()]
        key_inits = [w[0] for w in key_tokens[:-1]]
        key_init_str = "".join(key_inits)
        clean_key = f"{key_init_str} {key_tokens[-1]}"
        return clean_key

    def merge_init_clusters(self, extended_clusters: Dict[str, List[str]]):
        # Step 5: Merge cluster heads containing initials
        final_clusters = defaultdict(list)
        # Filter out cluster heads containing initials:
        heads_with_initials = [key for key in extended_clusters if self.has_init_match(key)]
        heads_without_initials = list(set(extended_clusters.keys()) - set(heads_with_initials))

        for init_head in heads_with_initials:
            init_match_found = False
            for head in heads_without_initials:
                # If cluster head with initials is equivalent with some other cluster head,
                # merge clusters
                if self.are_equivalent(init_head.lower(), head.lower(), init_mode=True):
                    if head not in final_clusters:
                        final_clusters[head].extend(extended_clusters[head])
                    final_clusters[head].extend(extended_clusters[init_head])
                    init_match_found = True
                    break
            if not init_match_found:
                if init_head not in final_clusters:
                    final_clusters[init_head].extend(extended_clusters[init_head])

        # Finally add all unmerged clusters to the output_
        for head in heads_without_initials:
            if head not in final_clusters:
                final_clusters[head] = extended_clusters[head]
        return final_clusters

    def generate_cluster_key(self, word: str) -> str:
        # cluster_key = word[:self.first_word_key_prefix_length]
        tokens = [t.strip() for t in word.split()]
        if len(tokens) > 1:
            cluster_key = tokens[0].strip('.')[: self.first_word_key_prefix_length]
            for t in tokens[1:]:
                cluster_key += t[: self.key_prefix_length]
        else:
            cluster_key = word[: self.first_word_key_prefix_length]
        return cluster_key.lower()

    def are_equivalent(self, key_1: str, key_2: str, 
                       init_mode: bool = False
    ) -> bool:
        if init_mode and (self.has_init_match(key_1) or self.has_init_match(key_2)):
            key_1 = self.clean_key(key_1)
            key_2 = self.clean_key(key_2)
        if jw(key_1, key_2) > self.similarity_threshold:
            return True
        return False

    def cluster(self, words: List[str]) -> Dict[str, List[str]]:
        """Finds clusters of similar strings."""
        LOGGER.debug(f"Clustering persons.")
        init_clusters = self.get_init_clusters(words)
        clusters = self.merge_clusters(init_clusters)
        extended_clusters = self.update_cluster_heads(clusters)
        final_clusters = self.merge_init_clusters(extended_clusters)
        return dict(final_clusters)
