from . import datasets

def load(name):
    """Load a dataset by name."""
    if hasattr(datasets, name):
        return getattr(datasets, name).load()
    else:
        raise ValueError(f"Dataset '{name}' not found in my_datasets_lib.datasets")
    
    
def describe(name):
    """Get the description for a dataset by name."""
    if hasattr(datasets, name):
        return getattr(datasets, name).describe()
    else:
        raise ValueError(f"Dataset '{name}' not found in my_datasets_lib.datasets")
    
def list_datasets():
    """Return a list of available dataset names."""
    return [name for name in dir(datasets) if not name.startswith("_")]

