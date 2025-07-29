"""
File utility functions for handling file operations in MCard.
"""
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypeVar, TYPE_CHECKING

from mcard.model.interpreter import ContentTypeInterpreter
from mcard.model.card_collection import CardCollection

# Import MCard type for type hints
if TYPE_CHECKING:
    from mcard.model.mcard import MCard
else:
    MCard = TypeVar('MCard')  # For runtime type checking

# Set up logger
logger = logging.getLogger(__name__)

class FileUtility:
    """
    Internal utility class for file operations in MCard.
    This class is not meant to be used directly. Use the standalone functions instead.
    """
    
    def __init__(self, collection: CardCollection):
        """Initialize with a CardCollection for storing MCards."""
        self.collection = collection
    
    @staticmethod
    def process_mcard(mcard: MCard) -> Optional[Dict[str, Any]]:
        """Process a single MCard into a displayable format.
        
        This function takes an MCard object and converts it into a dictionary with
        display-friendly fields including a content preview and formatted timestamps.
        
        Args:
            mcard: An instance of MCard or MCardFromData.
            
        Returns:
            dict: A dictionary with processed card data for display, or None if mcard is None.
            The dictionary contains the following keys:
                - hash: The card's unique hash
                - content_type: The type of content in the card
                - created_at: Formatted creation timestamp
                - content_preview: A preview of the card's content (first 50 chars)
                - card_class: The class name of the card (for debugging)
        """
        if mcard is None:
            return None
        
        try:
            # Safely get attributes with defaults using appropriate getter methods
            card_hash = getattr(mcard, 'hash', 'N/A')
            content = getattr(mcard, 'content', None)
            # Use getter methods instead of direct attribute access
            content_type = mcard.get_content_type() if hasattr(mcard, 'get_content_type') else 'unknown'
            created_at = mcard.get_g_time() if hasattr(mcard, 'get_g_time') else None
            
            # Create a preview of the content
            content_str = str(content) if content is not None else ''
            content_preview = content_str[:50] + ('...' if len(content_str) > 50 else '')
            
            # Format the creation time
            created_at_str = str(created_at)[:19] if created_at is not None else 'N/A'
            
            # Get the class name for debugging
            card_class = mcard.__class__.__name__
            
            return {
                'hash': card_hash,
                'content_type': content_type,
                'created_at': created_at_str,
                'content_preview': content_preview,
                'card_class': card_class  # For debugging
            }
        except Exception as e:
            logger.error("Error processing card: %s", str(e))
            return None
    
    @staticmethod
    def _load_files(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
        """
        Load all files from the specified directory.
        
        Args:
            directory: The directory to load files from (can be str or Path)
            recursive: If True, recursively load files from subdirectories
            
        Returns:
            A list of Path objects for all files in the directory
        """
        dir_path = Path(directory) if isinstance(directory, str) else directory
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory '{dir_path}' does not exist.")
            
        if recursive:
            return [f for f in dir_path.rglob("*") if f.is_file()]
        return [f for f in dir_path.glob("*") if f.is_file()]
    
    @staticmethod
    def _analyze_content(content: bytes) -> Dict[str, Any]:
        """Analyze content using ContentTypeInterpreter and return metadata."""
        mime_type, extension = ContentTypeInterpreter.detect_content_type(content)
        is_binary = ContentTypeInterpreter.is_binary_content(content)
        
        return {
            "mime_type": mime_type,
            "extension": extension,
            "is_binary": is_binary,
            "size": len(content)
        }
    
    @staticmethod
    def _read_file(file_path: Union[str, Path]) -> bytes:
        """Read the contents of a file and return as bytes."""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        if not path.exists():
            raise FileNotFoundError(f"File '{path}' does not exist.")
            
        with open(path, 'rb') as f:
            return f.read()
    
    @classmethod
    def _process_file(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Process a single file and return its metadata.
        
        For text files, ensures the content is properly decoded to UTF-8 when possible.
        """
        # Read file content as bytes
        content = cls._read_file(file_path)
        
        # Analyze the content to get MIME type and other metadata
        analysis = cls._analyze_content(content)
        mime_type = analysis["mime_type"]
        is_binary = analysis["is_binary"]
        
        # For text files, try to decode the content
        if not is_binary and mime_type.startswith('text/'):
            try:
                # Decode the content as UTF-8 for text files
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, try with error replacement
                try:
                    content = content.decode('utf-8', errors='replace')
                except Exception as e:
                    logger.warning(f"Failed to decode content for {file_path} as UTF-8: {e}")
        
        return {
            "content": content,
            "filename": Path(file_path).name,
            "mime_type": mime_type,
            "extension": analysis["extension"],
            "is_binary": is_binary,
            "size": analysis["size"]
        }
        
    def _process_and_store_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Process a file, create an MCard, and store it in the collection."""
        from mcard import MCard
            
        try:
            logger.debug(f"Starting to process file: {file_path}")
            
            # Process the file
            file_info = self._process_file(file_path)
            if not file_info:
                logger.warning(f"No file info returned for: {file_path}")
                return None
                
            logger.debug(f"Processing file info - Type: {type(file_info)}, Keys: {list(file_info.keys())}")
            logger.debug(f"Content type: {file_info.get('mime_type')}, Size: {file_info.get('size')} bytes")
            
            # Create MCard with just the content bytes
            try:
                mcard = MCard(content=file_info["content"])
                logger.debug(f"Created MCard with hash: {mcard.get_hash()}")
            except Exception as _e:
                logger.error(f"Failed to create MCard for {file_path}", exc_info=True)
                return None
            
            # Add to collection
            try:
                self.collection.add(mcard)
                logger.debug("Successfully added MCard to collection")
            except Exception as _e:
                logger.error(f"Failed to add MCard to collection for {file_path}", exc_info=True)
                return None
            
            # Prepare and return processing info
            result = {
                "hash": mcard.get_hash(),
                "content_type": file_info.get("mime_type"),
                "is_binary": file_info.get("is_binary"),
                "filename": file_info.get("filename"),
                "size": file_info.get("size")
            }
            
            logger.info(f"Successfully processed file: {file_path}")
            return result
            
        except Exception as _e:
            logger.error(f"Error processing {file_path}", exc_info=True)
            return None

def load_file_to_collection(path: Union[str, Path], 
                         collection: CardCollection, 
                         recursive: bool = False) -> List[Dict[str, Any]]:
    """
    Load a file or directory of files into the specified collection.
    
    This function handles the entire process of:
    1. If path is a file: Process that single file
    2. If path is a directory: Process all files in the directory (optionally recursively)
    3. Store the processed files in the collection
    4. Return processing information
    
    Args:
        path: Path to a file or directory to process
        collection: CardCollection to store the MCards in
        recursive: If True and path is a directory, recursively process files in subdirectories (default: False)
        
    Returns:
        List of dictionaries with processing information for each processed file
        
    Example:
        ```python
        from mcard import CardCollection
        from mcard.file_utility import load_file_to_collection
        
        # Create or load a collection
        collection = CardCollection()
        
        # Load a single file
        results = load_file_to_collection('/path/to/file.txt', collection)
        
        # Load files from a directory (non-recursive)
        results = load_file_to_collection('/path/to/files', collection)
        
        # Load files recursively from a directory
        results = load_file_to_collection('/path/to/files', collection, recursive=True)
        ```
    """
    path = Path(path) if isinstance(path, str) else path
    utility = FileUtility(collection)
    results = []
    
    if path.is_file():
        # Process a single file
        result = utility._process_and_store_file(path)
        if result:
            results.append(result)
    elif path.is_dir():
        # Process all files in the directory
        file_paths = utility._load_files(path, recursive=recursive)
        for file_path in file_paths:
            result = utility._process_and_store_file(file_path)
            if result:
                results.append(result)
    else:
        raise FileNotFoundError(f"Path '{path}' does not exist or is not accessible")
            
    return results
