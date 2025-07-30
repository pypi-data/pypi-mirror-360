import re

def is_valid_index_name(index_name):
    # Regular expression for alphanumeric characters and underscores
    pattern = re.compile(r'^[a-zA-Z0-9_]+$')
    if pattern.match(index_name) and len(index_name) <= 48:
        return True
    else:
        return False
    

def reciprocal_rank_fusion(data, k=60):
    """
    Reciprocal Rank Fusion (RRF) Algorithm for combining dense and sparse search results.
    
    Args:
        data (dict): Input data containing dense_results, sparse_results, metadata, etc.
        k (int): RRF parameter, typically 60. Lower values emphasize top-ranked results.
    
    Returns:
        list: List of dictionaries with combined RRF scores and ranking information.
    """
    
    # Extract data from input
    dense_results = data.get('dense_results', [])
    sparse_results = data.get('sparse_results', [])
    metadata = data.get('metadata', [])
    
    # Create dictionaries for quick lookup
    dense_rank_map = {doc['id']: doc['rank'] for doc in dense_results}
    sparse_rank_map = {doc['id']: doc['rank'] for doc in sparse_results}
    
    # Create lookup maps for scores and vectors
    dense_data_map = {doc['id']: doc for doc in dense_results}
    sparse_data_map = {doc['id']: doc for doc in sparse_results}
    
    # Create metadata lookup
    metadata_map = {meta['id']: meta.get('meta', '') for meta in metadata}
    
    # Get all unique document IDs
    all_doc_ids = set()
    all_doc_ids.update(dense_rank_map.keys())
    all_doc_ids.update(sparse_rank_map.keys())
    
    # Calculate RRF scores for each document
    rrf_results = []
    
    for doc_id in all_doc_ids:
        rrf_score = 0
        
        # Get ranks (None if document doesn't appear in a ranking list)
        dense_rank = dense_rank_map.get(doc_id)
        sparse_rank = sparse_rank_map.get(doc_id)
        
        # Calculate RRF contribution from dense ranking
        if dense_rank is not None:
            rrf_score += 1 / (k + dense_rank)
        
        # Calculate RRF contribution from sparse ranking  
        if sparse_rank is not None:
            rrf_score += 1 / (k + sparse_rank)
        
        # Determine which vector to use (prefer dense if both present, otherwise use available)
        vector = None
        if doc_id in dense_data_map and doc_id in sparse_data_map:
            # Both present, use dense vector
            vector = dense_data_map[doc_id].get('vector')
        elif doc_id in dense_data_map:
            # Only dense present
            vector = dense_data_map[doc_id].get('vector')
        elif doc_id in sparse_data_map:
            # Only sparse present
            vector = sparse_data_map[doc_id].get('vector')
        
        # Create result object
        result = {
            'id': doc_id,
            'rrf_score': rrf_score,
            'sparse_rank': sparse_rank if sparse_rank is not None else 0,
            'dense_rank': dense_rank if dense_rank is not None else 0,
            'meta': metadata_map.get(doc_id, ''),
            'vector': vector
        }
        
        rrf_results.append(result)
    
    # Sort by RRF score in descending order
    rrf_results.sort(key=lambda x: x['rrf_score'], reverse=True)
    
    return rrf_results


def validate_rrf_input(data):
    """
    Validate the input data structure for RRF algorithm.
    
    Args:
        data (dict): Input data to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    
    if not isinstance(data, dict):
        return False, "Input data must be a dictionary"
    
    # Check required keys
    required_keys = ['dense_results', 'sparse_results']
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"
    
    # Validate dense_results structure
    if not isinstance(data['dense_results'], list):
        return False, "dense_results must be a list"
    
    for i, doc in enumerate(data['dense_results']):
        if not isinstance(doc, dict):
            return False, f"dense_results[{i}] must be a dictionary"
        
        # Required keys - vector is optional
        required_doc_keys = ['id', 'score', 'rank']
        for key in required_doc_keys:
            if key not in doc:
                return False, f"dense_results[{i}] missing required key: {key}"
    
    # Validate sparse_results structure
    if not isinstance(data['sparse_results'], list):
        return False, "sparse_results must be a list"
    
    for i, doc in enumerate(data['sparse_results']):
        if not isinstance(doc, dict):
            return False, f"sparse_results[{i}] must be a dictionary"
        
        # Required keys - vector is optional
        required_doc_keys = ['id', 'score', 'rank']
        for key in required_doc_keys:
            if key not in doc:
                return False, f"sparse_results[{i}] missing required key: {key}"
    
    # Validate metadata if present
    if 'metadata' in data:
        if not isinstance(data['metadata'], list):
            return False, "metadata must be a list"
        
        for i, meta in enumerate(data['metadata']):
            if not isinstance(meta, dict):
                return False, f"metadata[{i}] must be a dictionary"
            
            if 'id' not in meta:
                return False, f"metadata[{i}] missing required key: id"
    
    return True, "Valid input structure"