"""
Core functionality for AlphaStation package.
"""


class AlphaStation:
    """AlphaStation main class."""
    
    def __init__(self, name="AlphaStation"):
        """Initialize AlphaStation with a name."""
        self.name = name
        self.status = "inactive"
    
    def activate(self):
        """Activate AlphaStation."""
        self.status = "active"
        return f"AlphaStation '{self.name}' is now active"
    
    def get_info(self):
        """Get AlphaStation information."""
        return {
            "name": self.name,
            "status": self.status
        }


def alpha_function(x, y=1):
    """
    Alpha function for AlphaStation.
    
    Args:
        x (float): Input value
        y (float): Multiplier (default: 1)
    
    Returns:
        float: Result of x * y + 42
    """
    return x * y + 42 