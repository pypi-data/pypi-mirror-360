import numpy as np

def compute_normalized_inner_product(v1, v2):
    """
    Calculate the dot product of two normalized vectors (cosine similarity)
    
    Args:
        v1 (array-like): First vector
        v2 (array-like): Second vector
        
    Returns:
        float: Normalized dot product (cosine similarity) between 0 and 1
    """
    # Convert to numpy arrays
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    # Calculate norms
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    # Check for zero vectors
    if norm_v1 == 0 or norm_v2 == 0:
        return 0
    
    # Normalize vectors
    v1_normalized = v1 / norm_v1
    v2_normalized = v2 / norm_v2
    
    # Calculate dot product of normalized vectors
    return np.dot(v1_normalized, v2_normalized)


def get_lexicographical_orderd_df(df, ascending=False):
    return df.sort_values(by=df.columns.tolist(), ascending=ascending)

        