class InvalidLanguageException(Exception):
    """Raised when language is not supported."""
        
class InvalidSplitMethodError(Exception):
    """Raised when TextSplitter is initiated with invalid splitting option."""
    
class InvalidMethodException(Exception):
    """Raised for invalid keyword extraction method."""

class InvalidKeywordTypeException(Exception):
    """Raised for invalid keyword types."""
    
class InvalidInputException(Exception):
    """Raised for invalid input."""
    
class StemmerLoadingException(Exception):
    """Raised when stemmer for a specific language cannot be loaded."""
    
class NotImplementedException(Exception):
    """Raised when method is not implemented."""
    
class ModelNotLoadedException(Exception):
    """Raised when model object is missing."""
    
class ModelExistsException(Exception):
    """Raised during training when an existing model is already loaded."""
    
class MissingValueException(Exception):
    """Raised when a value is missing from config / kwargs etc"""
    
class MissingFileException(Exception):
    """Raised when a necessary model/config etc file is missing."""
    
class MissingDataException(Exception):
    """Raised when relevant model data is missing."""