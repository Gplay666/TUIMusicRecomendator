import random
import timeit
import matplotlib.pyplot as plt

# ---------- Алгоритмы сортировки ----------
def bubble_sort(arr):
    n = len(arr)
    arr = arr.copy()
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# def quicksort(arr):
#     if len(arr) <= 1:
#         return arr.copy()
#     pivot = arr[len(arr) // 2]
#     left = [x for x in arr if x < pivot]
#     middle = [x for x in arr if x == pivot]
#     right = [x for x in arr if x > pivot]
#     return quicksort(left) + middle + quicksort(right)
def quicksort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr.copy()
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if key(x) < key(pivot)]
    middle = [x for x in arr if key(x) == key(pivot)]
    right = [x for x in arr if key(x) > key(pivot)]
    return (
        quicksort(left, key)
        + middle
        + quicksort(right, key)
    )

def merge_sort(arr):
    if len(arr) <= 1:
        return arr.copy()
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# ---------- Генерация данных ----------
def generate_data(n, data_type):
    if data_type == 'random':
        return [random.randint(0, 10000) for _ in range(n)]
    elif data_type == 'sorted':
        return list(range(n))
    elif data_type == 'reversed':
        return list(range(n, 0, -1))
    elif data_type == 'almost_sorted':
        arr = list(range(n))
        # перемешаем 5% элементов
        for _ in range(int(n * 0.05)):
            i, j = random.sample(range(n), 2)
            arr[i], arr[j] = arr[j], arr[i]
        return arr

# ---------- Измерение времени ----------
def measure_time(sort_func, arr, repeats=5):
    arr_copy = arr.copy()
    timer = timeit.Timer(lambda: sort_func(arr_copy))
    times = timer.repeat(repeat=repeats, number=1)
    return min(times)  # берём минимальное время

# ---------- Основной эксперимент ----------
# sizes_bubble = [100, 500, 1000]
# sizes_fast = [100, 500, 1000, 5000, 10000, 20000]
# data_types = ['random', 'sorted', 'reversed', 'almost_sorted']
# algorithms = {
#     'Bubble Sort': bubble_sort,
#     'Quicksort': quicksort,
#     'Merge Sort': merge_sort
# }
#
# results = {}
#
# for algo_name, algo_func in algorithms.items():
#     results[algo_name] = {}
#     sizes = sizes_bubble if algo_name == 'Bubble Sort' else sizes_fast
#     for dtype in data_types:
#         results[algo_name][dtype] = []
#         for n in sizes:
#             arr = generate_data(n, dtype)
#             t = measure_time(algo_func, arr)
#             results[algo_name][dtype].append((n, t))
#             print(f"{algo_name}, {dtype}, n={n}: {t:.6f} c")
#
# # ---------- Построение графиков ----------
# fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# for ax, dtype in zip(axes.flat, data_types):
#     for algo_name in algorithms:
#         sizes = [x[0] for x in results[algo_name][dtype]]
#         times = [x[1] for x in results[algo_name][dtype]]
#         ax.plot(sizes, times, marker='o', label=algo_name)
#     ax.set_xlabel('Размер массива')
#     ax.set_ylabel('Время (с)')
#     ax.set_title(f'Тип данных: {dtype}')
#     ax.legend()
#     ax.grid(True)
# plt.tight_layout()
# plt.show()
