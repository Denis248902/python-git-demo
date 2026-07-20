import random
import time

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

def linear_search(arr, target):
    for index, value in enumerate(arr):
        if value == target:
            return index
    return -1

def main():
    # Пункт 02: список из 100 случайных чисел
    numbers = [random.randint(0, 200) for _ in range(100)]
    test_values = [numbers[10], 999, numbers[-1]]

    print("Первые 20 элементов:", numbers[:20])
    results = {val: linear_search(numbers, val) for val in test_values}
    print("Результаты поиска:", results)

    # Пункт 03: замеры времени
    sizes = [10, 100, 1_000, 5_000, 10_000, 50_000]
    times = []

    for n in sizes:
        arr = [random.randint(0, n * 10) for _ in range(n)]
        target = arr[-1]

        start = time.perf_counter()
        linear_search(arr, target)
        end = time.perf_counter()

        t = end - start
        times.append(t)
        print(f"Размер {n:>6}, время {t:.6f} сек")

    if HAS_MATPLOTLIB:
        plt.figure(figsize=(8, 5))
        plt.plot(sizes, times, marker='o')
        plt.title('Зависимость времени линейного поиска от размера списка')
        plt.xlabel('Размер списка (n)')
        plt.ylabel('Время (секунды)')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print("matplotlib не установлен: график не будет построен.")

if __name__ == "__main__":
    main()
