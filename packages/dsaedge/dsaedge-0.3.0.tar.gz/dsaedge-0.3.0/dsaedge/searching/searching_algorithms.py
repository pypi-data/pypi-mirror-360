def linear_search(arr, target):
    """
    Performs a linear search to find the index of a target in an array.
    Works on both sorted and unsorted lists.
    Returns the index of the target if found, otherwise -1.
    """
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def binary_search(arr, target):
    """
    Performs an iterative binary search to find the index of a target.
    Requires the array to be sorted.
    Returns the index of the target if found, otherwise -1.
    """
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        # Check if target is present at mid
        if arr[mid] == target:
            return mid
        # If target is greater, ignore left half
        elif arr[mid] < target:
            low = mid + 1
        # If target is smaller, ignore right half
        else:
            high = mid - 1
            
    # If we reach here, then the element was not present
    return -1

def binary_search_recursive(arr, low, high, target):
    """
    Performs a recursive binary search.
    Helper function to demonstrate the recursive approach.
    """
    if high >= low:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] > target:
            return binary_search_recursive(arr, low, mid - 1, target)
        else:
            return binary_search_recursive(arr, mid + 1, high, target)
    else:
        # Element is not present in the array
        return -1

