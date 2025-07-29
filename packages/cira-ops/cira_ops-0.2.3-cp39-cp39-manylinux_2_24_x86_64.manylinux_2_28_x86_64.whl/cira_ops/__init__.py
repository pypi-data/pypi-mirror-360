from ._core import _process_array
from ._core import _process_array_s

def process_array(input_array):
    """
    Wrapper function for process_array with some additional checks.
    
    Args:
        input_array (numpy.ndarray): Input 2D NumPy array
    
    Returns:
        numpy.ndarray: Processed array
    """
    return _process_array(input_array)
    
def process_array_s(clss, input_array):
    return _process_array_s(clss, input_array)

__all__ = ['process_array', 'process_array_s']
