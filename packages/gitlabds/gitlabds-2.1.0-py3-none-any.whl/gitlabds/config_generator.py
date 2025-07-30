import yaml
from typing import Any, Dict, List


class ConfigGenerator:
    """
    A simple, flexible configuration builder for creating YAML files
    with any structure.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a configuration with optional initial values.
        
        Parameters
        ----------
        **kwargs : any
            Initial configuration values
        """
        self.data = kwargs.copy() if kwargs else {}
    
    def add(self, path: str, value: Any):
        """
        Add or update a value at the specified path.
        
        Parameters
        ----------
        path : str
            Dot-notation path (e.g., 'section.subsection.key')
        value : any
            Value to set
            
        Returns
        -------
        self : Config
            For method chaining
        """
        parts = path.split('.')
        current = self.data
        
        # Navigate through the path, creating dictionaries as needed
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the final value
        current[parts[-1]] = value
        return self
    
    def to_yaml(self, file_path: str):
        """
        Write the configuration to a YAML file.
        
        Parameters
        ----------
        file_path : str
            Path to the output file
            
        Returns
        -------
        self : Config
            For method chaining
        """
        with open(file_path, 'w') as f:
            yaml.safe_dump(self.data, f, sort_keys=False)
        return self
    
    def __str__(self):
        return yaml.safe_dump(self.data, sort_keys=False)