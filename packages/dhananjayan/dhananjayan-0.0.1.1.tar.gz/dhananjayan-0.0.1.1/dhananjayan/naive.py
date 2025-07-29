import time
def dot_product(list1: list, list2: list) -> tuple:
    start = time.time()
    if len(list1) != len(list2):
        raise ValueError("Both lists must have the same length.")
    return sum(x * y for x, y in zip(list1, list2)), time.time() - start