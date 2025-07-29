from typing import List, Dict

class BaseIndexer:
    """
    The common parent for all indexers.
    """

    def __init__(self, top_k: int = 30, **config):
        """
        TODO
        """
        self.config = config
        self.top_k = top_k
       

    def find_keywords(self, text: str) -> List[Dict]:
        """
        Find or extract keywords from the input text.
        """
        raise NotImplementedError("Subclasses must implement this method.")