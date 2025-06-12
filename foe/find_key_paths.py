def find_key_paths(data, target_key=None, target_value=None):
    """
    Finds and returns the paths to all occurrences of a target key, value, or key-value pair.
    
    Args:
        data (dict or list): The nested data structure to search.
        target_key (str, optional): The key to search for.
        target_value (any, optional): The value to search for.
    
    Returns:
        list: A list of paths where the search condition is met.
    """
    paths = []      # To store paths to the target key-value pairs
    
    def recurse(current, path, parent_path=None):
        if isinstance(current, dict):
            for key, value in current.items():
                current_path = path + [key]
                
                # Determine whether the current key-value pair matches the search criteria
                if target_key is not None and target_value is not None:
                    if key == target_key and value == target_value:
                        paths.append(current_path)
                elif target_key is not None:
                    if key == target_key:
                        paths.append(current_path)
                elif target_value is not None:
                    if value == target_value:
                        paths.append(current_path)

                # Recurse into the value
                recurse(value, current_path, parent_path=current_path if isinstance(value, dict) else parent_path)
        
        elif isinstance(current, list):
            for index, item in enumerate(current):
                current_path = path + [index]
                recurse(item, current_path, parent_path=parent_path)

    recurse(data, [])
    return paths