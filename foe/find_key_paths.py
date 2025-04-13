def find_key_paths(data, target_key, target_value):
    # Finds and prints the paths to all occurrences of a target key-value pair.
    # 
    # Args:
    #     data (dict or list): The nested data structure to search.
    #     target_key (str): The key to search for.
    #     target_value (any): The value that the target key should have.
    # 
    # Returns:
    #     key paths
    paths = []      # To store paths to the target key-value pairs
    
    def recurse(current, path, parent_path=None):
        # Recursively traverses the data structure to find target key-value pairs.
        # 
        # Args:
        #     current (any): The current element in the data structure.
        #     path (list): The path taken to reach the current element.
        #     parent_path (list): The path to the parent of the current element.
        # 
        # Returns:
        #     None
        if isinstance(current, dict):
            for key, value in current.items():
                current_path = path + [key]
                # Check if the current key-value pair matches the target
                if key == target_key and value == target_value:
                    paths.append(current_path)
                # Recurse into the value
                recurse(value, current_path, parent_path=current_path if isinstance(value, dict) else parent_path)
        elif isinstance(current, list):
            for index, item in enumerate(current):
                # Represent list indices as [index]
                current_path = path + [index]
                recurse(item, current_path, parent_path=parent_path)
        # For other data types, do nothing

    # Start the recursion with the initial data and an empty path
    recurse(data, [])
    
    # Print the results for target key-value pairs    
    # if not paths:
    #     print(f"No occurrences of '{target_key}': '{target_value}' found.")
    # else:
    #     print(f"Found {len(paths)} occurrence(s) of '{target_key}': '{target_value}'.")
        
    return(paths)