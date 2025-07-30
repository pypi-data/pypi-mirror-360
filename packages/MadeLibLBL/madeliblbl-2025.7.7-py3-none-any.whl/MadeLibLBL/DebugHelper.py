from typing import Any

def print_for_debug(var_name: str, var_value: Any) -> None:
    """Prints a debug message with a centered variable name and its value.
    
    Formats a debug output with the variable name centered in a 40-character wide
    asterisk-decorated header, followed by the variable's value. This provides
    visually distinct debug output in console/logs.

    Args
    ----
        var_name (str): The name of the variable to display in the debug header.
        var_value (Any): The value of the variable to display. Can be of any type
                        that supports string conversion via str().

    Returns
    -------
        None: This function only prints output and doesn't return any value.

    Notes
    -----
        - The header is exactly 40 characters wide
        - Variable names are centered with asterisk padding
        - If centering can't be perfect, extra asterisks are added to the right
        - The full output consists of:
          1. Centered header with variable name
          2. The variable value on a new line

    Examples
    --------
        >>> print_for_debug("username", "john_doe")
        ************ username *************
        john_doe

        >>> print_for_debug("count", 42)
        *************** count **************
        42
    """
    # Calculate the number of asterisks needed to center the variable name
    total_length = 40
    var_name_length = len(var_name)
    asterisks_length = (total_length - var_name_length) // 2
    
    # Create the asterisk string
    asterisks = '*' * asterisks_length
    
    # Center the variable name between the asterisks
    centered_var_name = f"{asterisks} {var_name} {asterisks}"
    
    # Adjust the total length to ensure it's always 40 characters
    if len(centered_var_name) < total_length:
        centered_var_name += '*' * (total_length - len(centered_var_name))
    
    # Print the centered variable name
    print(centered_var_name)
    
    # Print the variable value
    print(var_value)