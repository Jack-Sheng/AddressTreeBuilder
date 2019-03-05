def binary_Searching(alist, data):
    """
    非递归解决二分查找
    :param alist:
    :return:
    """
    length = len(alist)
    first = 0
    last = length - 1
    while first <= last:
        mid = (last + first) // 2
        if alist[mid][1] > data:
            last = mid - 1
        elif alist[mid][1] < data:
            first = mid + 1
        else:
            return mid
    return mid





