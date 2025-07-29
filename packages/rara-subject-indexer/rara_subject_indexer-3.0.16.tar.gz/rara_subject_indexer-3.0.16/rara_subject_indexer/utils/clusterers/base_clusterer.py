import abc
from collections import defaultdict
from itertools import combinations, islice
from typing import Dict, List, NoReturn


class BaseClusterer(metaclass=abc.ABCMeta):
    def __init__(
        self, 
        similarity_threshold: float = 0.85
    ) -> NoReturn:
        """ Initializes BaseClusterer instance. 
        
        Parameters
        -----------
        similarity_threshold: float
            Minimum Jaro-Winkler similarity between 
            cluster (sub)elements.
        """
        self.similarity_threshold = similarity_threshold

    def window(self, seq: list, window_size: int = 2):
        """ Returns a sliding window (of width n) over data
        from the iterable: s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
       
        Parameters
        -----------
        seq: list
            TODO
        window_size: int
            TODO
            
        """
        _it = iter(seq)
        result = tuple(islice(_it, window_size))
        if len(result) == n:
            yield result
        for elem in _it:
            result = result[1:] + (elem,)
            yield result

    def get_cluster_head(self, cluster_elements: List[str]) -> str:
        """ Gets the base element of the cluster 
        following these restrictions:
            1. Should contain as many words as possible &
            2. Should be the shortest of such candidates.
        
        Parameters
        -----------
        cluster_elements: List[str]
            List of cluster elements
        
        Returns
        -----------
        cluster_head: str
            Most likely base form out of all cluster elements.
            E.g. cluster_elements=["Tamm", "Uku Tamm", "Uku Tammele"]
            should return "Uku Tamm.
        """
        word_counts = defaultdict(list)
        for elem in cluster_elements:
            word_counts[len(elem.split())].append(elem)
        word_counts_list = sorted(
            list(word_counts.items()), key=lambda x: x[0], reverse=True
        )
        candidates = word_counts_list[0][1]
        cluster_head = min(candidates, key=len)
        return cluster_head

    def get_init_clusters(self, words: List[str]) -> Dict[str, List[str]]:
        """ Generates inital clusters based on
        (sub)word prefixes.
        
        Parameters
        -----------
        words: List[str]
            List of words to cluster.
            
        Returns
        -----------
        init_clusters: Dict[str, List[str]]
            Initial simple clusters.
        """
        init_clusters = defaultdict(list)
        for word in words:
            # Construct cluster key of subword prefixes
            cluster_key = self.generate_cluster_key(word)
            init_clusters[cluster_key].append(word)
        return dict(init_clusters)

    def update_cluster_heads(
        self, 
        clusters: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """ Updates the key elements of the clusters.
        
        Parameters
        -----------
        clusters: Dict[str, List[str]]
            Clusters to update
            
        updated_clusters: Dict[str, List[str]]
            Clusters with updated heads/keys.
        """
        updated_clusters = {}
        for key, cluster in list(clusters.items()):
            new_cluster_head = self.get_cluster_head(cluster)
            updated_clusters[new_cluster_head] = cluster
        return updated_clusters

    def merge_clusters(
        self, 
        init_clusters: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Merges clusters containing elements with smaller number of words
        with the clusters containing elements with bigger number of words, e.g:
        Cluster ("Smith": ["Smith"]) with cluster ("John Smith": ["John Smith"])-
        """
        # Step 1:
        # Assign the element with biggest word count as cluster key:
        new_clusters = {}
        for c in init_clusters:
            values = init_clusters[c]
            splitted_values = [v.split() for v in values]
            max_element = ' '.join(max(splitted_values, key=len))
            new_clusters[max_element] = values
        # print("Output of STEP 1: ", new_clusters)
        # Step 2: Cluster clusters by length
        # Output: {
        #   2: [("John Smith", ["John", "John Smith"]), ...],
        #   1: [("Lisa", ["Lisa", "Lisanne"]), ...],
        #   ...}
        clusters_by_length = defaultdict(list)
        for key in new_clusters:
            key_tokens = key.split()
            key_len = len(key_tokens)
            # if key_len > 1 and re.match(self.init_pattern, key_tokens[0]):
            #    key_len-=1
            clusters_by_length[key_len].append((key, new_clusters[key]))
        # print("Output of STEP 2: ", clusters_by_length)

        # Step 3: Sort constructed clusters by length:
        # Output: [
        #   [1, [("Lisa", ["Lisa", "Lisanne"]), ...]],
        #   [2, [("John Smith", ["John", "John Smith"]), ...]],
        #   ...]
        sorted_clusters = sorted(list(clusters_by_length.items()), key=lambda x: x[0])
        for sc in sorted_clusters:
            # Sort inner clusters by length, so that subwords
            # get appended to the bigger clusters (as it is more probable that
            # single last names, for example, are belonging to the name mentioned more
            # often if there are multiple candidates, e.g:
            # c1 = ["Gagarin"],
            # c2 = ["Juri Gagarin", "Juri Gagarin", "Juri Gagarin"],
            # c3 = ["Jelena Gagarin"]
            # We assume that c1 should be merged with c2.

            sc[1].sort(key=lambda x: len(x[1]), reverse=True)
        # print("Output of STEP 3: ", sorted_clusters)

        # Step 4: Find final cluster by merging the clusters with smaller number of words
        # with the cluster of bigger number of words, if possible:
        extended_clusters = defaultdict(list)
        for i, (word_count, clusters) in enumerate(sorted_clusters):
            for cluster_key, values in clusters:
                added = False
                try:
                    j = i + 1
                    while not added:
                        next_level_clusters = sorted_clusters[j][1]
                        cluster_key_normalized = ' '.join([c.strip() for c in cluster_key.split()])
                        for next_cluster_key, next_values in next_level_clusters:
                            next_cluster_tokens = [c.strip() for c in next_cluster_key.split()]
                            # Create a list of word paris with the same
                            # word count as in the current word, e.g:
                            # Current word = "John Smith",
                            # Next level cluster word = "John Elias Smith" ->
                            # ["John Elias", "Elias Smith", "John Smith"]
                            # iter_window = window(next_cluster_tokens, word_count)
                            iter_window = combinations(next_cluster_tokens, word_count)
                            for token_slice in iter_window:
                                token_slice = (' '.join(token_slice)).lower()
                                cluster_key_normalized = cluster_key_normalized.lower()
                                # If the slice with the same number of words is similar
                                # enough to the current word, merge the corresponding
                                # clusters.
                                if self.are_equivalent(cluster_key_normalized, token_slice):
                                    next_values.extend(values)
                                    added = True
                                    break
                            if added:
                                break
                        j += 1
                except Exception as e:
                    pass
                if not added:
                    extended_clusters[cluster_key] = values

        return extended_clusters

    @abc.abstractmethod
    def are_equivalent(self, key_1: str, key_2: str) -> bool:
        pass

    @abc.abstractmethod
    def generate_cluster_key(self, word: str) -> str:
        pass

    @abc.abstractmethod
    def cluster(self, words: List[str]) -> Dict[str, List[str]]:
        pass
