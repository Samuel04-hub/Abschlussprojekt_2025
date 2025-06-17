def insertion_sort(array): 
    """ Function to peform insertion sort on a list"""
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        while j >= 0 and key < array[j]:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key
    return array




def bubble_sort(array):
    """ Function to peform bubble sort on a list"""
    n = len(array)
    for i in range(n):
        for j in range(0, n-i-1):
            if array[j] > array[j+1]:
                array[j], array[j+1] = array[j+1], array[j]
    return array

if __name__ == "__main__":
    # Example usage
    data = [64, 34, 25, 12, 22, 11, 90]
    print("Unsorted array:", data)
    sorted_data = bubble_sort(data)
    print("Sorted array:", sorted_data)
