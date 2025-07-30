import requests
import secrets
import json
from vecx.exceptions import raise_exception
from vecx.index import Index
from vecx.hybrid_index import HybridIndex
from vecx.user import User
from vecx.crypto import get_checksum
from vecx.utils import is_valid_index_name
from functools import lru_cache

SUPPORTED_REGIONS = ["us-west", "india-west", "local"]
class VectorX:
    def __init__(self, token:str|None=None):
        self.token = token
        self.region = "local"
        self.base_url = "http://127.0.0.1:8080/api/v1"
        # Token will be of the format user:token:region
        if token:
            token_parts = self.token.split(":")
            if len(token_parts) > 2:
                self.base_url = f"https://{token_parts[2]}.vectorxdb.ai/api/v1"
                self.token = f"{token_parts[0]}:{token_parts[1]}"
        self.version = 1

    def __str__(self):
        return self.token

    def set_token(self, token:str):
        self.token = token
        self.region = self.token.split (":")[1]
    
    def set_base_url(self, base_url:str):
        self.base_url = base_url
    
    def generate_key(self)->str:
        # Generate a random hex key of length 32
        key = secrets.token_hex(16)  # 16 bytes * 2 hex chars/byte = 32 chars
        print("Store this encryption key in a secure location. Loss of the key will result in the irreversible loss of associated vector data.\nKey: ",key)
        return key

    def create_index(self, name:str, dimension:int, space_type:str, M:int=16, key:str|None=None, ef_con:int=128, use_fp16:bool=True, version:int=None):
        if is_valid_index_name(name) == False:
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        if dimension > 10000:
            raise ValueError("Dimension cannot be greater than 10000")
        space_type = space_type.lower()
        if space_type not in ["cosine", "l2", "ip"]:
            raise ValueError(f"Invalid space type: {space_type}")
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'index_name': name,
            'dim': dimension,
            'space_type': space_type,
            'M':M,
            'ef_con': ef_con,
            'checksum': get_checksum(key),
            'use_fp16': use_fp16,
            'version': version
        }
        response = requests.post(f'{self.base_url}/index/create', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return "Index created successfully"

    def create_hybrid_index(self, name: str, dimension: int, space_type: str = "l2", 
                          vocab_size: int = 30522, M: int = 16, key: str | None = None, 
                          ef_con: int = 200, use_fp16: bool = False, version: int = None):
        """
        Create a hybrid index that supports both dense and sparse vectors.
        
        Args:
            name: Index name
            dimension: Dimension of dense vectors
            space_type: Distance metric ("l2", "cosine", "ip")
            vocab_size: Vocabulary size for sparse vectors (default: 30522 for BERT)
            M: HNSW M parameter
            key: Encryption key (optional)
            ef_con: HNSW ef_construction parameter
            use_fp16: Use FP16 for dense vectors
            version: Version number
        
        Returns:
            Success message
        """
        if not is_valid_index_name(name):
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        if dimension > 10000:
            raise ValueError("Dimension cannot be greater than 10000")
        
        space_type = space_type.lower()
        if space_type not in ["cosine", "l2", "ip"]:
            raise ValueError(f"Invalid space type: {space_type}")
        
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'index_name': name,
            'dim': dimension,
            'vocab_size': vocab_size,
            'space_type': space_type,
            'M': M,
            'ef_con': ef_con,
            'use_fp16': use_fp16,
            'checksum': get_checksum(key)
        }
        
        if version is not None:
            data['version'] = version
        
        response = requests.post(f'{self.base_url}/hybrid/create', headers=headers, json=data)
        if response.status_code not in [200, 201]:
            print(response.text)
            raise_exception(response.status_code, response.text)
        
        return "Hybrid index created successfully"

    def list_indexes(self):
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.get(f'{self.base_url}/index/list', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        indexes = response.json()
        return indexes
    
    # TODO - Delete the index cache if the index is deleted
    def delete_index(self, name:str):
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.delete(f'{self.base_url}/index/{name}/delete', headers=headers)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return f'Index {name} deleted successfully'

    def delete_hybrid_index(self, name: str):
        """
        Delete a hybrid index.
        
        Args:
            name: Index name
        
        Returns:
            Success message
        """
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.delete(f'{self.base_url}/hybrid/{name}/delete', headers=headers)
        if response.status_code not in [200, 201]:
            print(response.text)
            raise_exception(response.status_code, response.text)
        return f'Hybrid index {name} deleted successfully'


    # Keep in lru cache for sometime
    @lru_cache(maxsize=20)  # Increased cache size to accommodate both types
    def get_index(self, name: str, key: str | None = None, hybrid: bool = False):
        """
        Get an index instance (regular or hybrid).
        
        Args:
            name: Index name
            key: Encryption key (optional)
            hybrid: If True, returns HybridIndex instance; if False, returns Index instance
        
        Returns:
            Index or HybridIndex instance based on the hybrid parameter
        """
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        
        # Get index details from the server
        response = requests.get(f'{self.base_url}/index/{name}/info', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        
        data = response.json()
        
        # Raise error if checksum does not match
        checksum = get_checksum(key)
        if checksum != data['checksum']:
            raise_exception(403, "Checksum does not match. Please check the key.")
        
        # Create appropriate index instance based on type
        if hybrid:
            idx = HybridIndex(
                name=name, 
                key=key, 
                token=self.token, 
                url=self.base_url, 
                version=self.version, 
                params=data
            )
        else:
            idx = Index(
                name=name, 
                key=key, 
                token=self.token, 
                url=self.base_url, 
                version=self.version, 
                params=data
            )
        
        return idx

    def get_hybrid_index(self, name: str, key: str | None = None):
        """
        Get a hybrid index instance.
        
        Args:
            name: Index name
            key: Encryption key (optional)
        
        Returns:
            HybridIndex instance
            
        Note:
            This is a convenience method that calls get_index(name, key, hybrid=True)
        """
        return self.get_index(name, key, hybrid=True)
    
    def get_user(self):
        return User(self.base_url, self.token)

