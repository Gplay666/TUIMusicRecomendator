from collections import deque
class Graph:
    """
    Простая библиотека для работы с графами.
    Поддерживает ориентированные и неориентированные графы, взвешенные рёбра.
    """

    def __init__(self, directed=False):
        """
        Инициализация пустого графа.
        :param directed: True для ориентированного графа, False для неориентированного.
        """
        self.directed = directed
        self.nodes = {}      # список смежности: {узел: [соседи]}
        self.edges = []      # список рёбер: [{'from': a, 'to': b, 'weight': w}]

    def add_node(self, node):
        """Добавляет вершину в граф, если она ещё не существует."""
        if node not in self.nodes:
            self.nodes[node] = []
        # Если вершина уже есть, ничего не делаем (можно было бы кинуть исключение, но по умолчанию игнорируем)

    def add_edge(self, from_node, to_node, weight=1):
        """
        Добавляет ребро между from_node и to_node с заданным весом.
        Если граф неориентированный, добавляется также обратное ребро.
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError("Обе вершины должны существовать в графе. Сначала добавьте их через add_node.")

        # Добавляем в список смежности
        self.nodes[from_node].append(to_node)
        if not self.directed:
            self.nodes[to_node].append(from_node)

        # Добавляем в список рёбер
        self.edges.append({'from': from_node, 'to': to_node, 'weight': weight})
        if not self.directed:
            # Для неориентированного графа храним только одно ребро, но с учётом направленности в матрице оно будет симметричным.
            # Можно добавить и обратное, но это избыточно. Оставим одно.
            pass

    def remove_node(self, node):
        """Удаляет вершину и все связанные с ней рёбра."""
        if node not in self.nodes:
            raise ValueError(f"Вершина {node} не найдена.")

        # Удаляем все рёбра, содержащие эту вершину
        self.edges = [e for e in self.edges if e['from'] != node and e['to'] != node]

        # Удаляем вершину из списка смежности
        del self.nodes[node]

        # Удаляем все упоминания этой вершины в списках смежности других вершин
        for other in self.nodes:
            self.nodes[other] = [n for n in self.nodes[other] if n != node]

    def remove_edge(self, from_node, to_node, weight=None):
        """
        Удаляет ребро между from_node и to_node.
        Если вес указан, удаляется только ребро с таким весом.
        Если не указан, удаляется первое попавшееся ребро между этими вершинами.
        Для неориентированного графа удаляется ребро в любом направлении.
        """
        # Поиск индекса ребра для удаления
        index_to_remove = None
        for i, e in enumerate(self.edges):
            if (e['from'] == from_node and e['to'] == to_node) or \
               (not self.directed and e['from'] == to_node and e['to'] == from_node):
                if weight is None or e['weight'] == weight:
                    index_to_remove = i
                    break

        if index_to_remove is None:
            raise ValueError(f"Ребро между {from_node} и {to_node} не найдено.")

        removed_edge = self.edges.pop(index_to_remove)

        # Удаляем из списков смежности
        # В ориентированном графе удаляем только из from_node
        if from_node in self.nodes:
            self.nodes[from_node] = [n for n in self.nodes[from_node] if n != to_node]
        if not self.directed and to_node in self.nodes:
            self.nodes[to_node] = [n for n in self.nodes[to_node] if n != from_node]

    def adjacency_matrix(self):
        """
        Возвращает матрицу смежности в виде списка списков.
        Строки и столбцы соответствуют вершинам, отсортированным по ключу.
        """
        nodes_list = sorted(self.nodes.keys())
        n = len(nodes_list)
        matrix = [[0] * n for _ in range(n)]
        # Создаём отображение вершина -> индекс
        index_map = {node: i for i, node in enumerate(nodes_list)}

        for edge in self.edges:
            i = index_map[edge['from']]
            j = index_map[edge['to']]
            matrix[i][j] = edge['weight']
            if not self.directed:
                matrix[j][i] = edge['weight']  # симметричность для неориентированного графа

        return matrix

    def display(self):
        """Выводит матрицу смежности на экран."""
        matrix = self.adjacency_matrix()
        nodes_list = sorted(self.nodes.keys())
        print("Матрица смежности:")
        print("   ", "  ".join(str(node) for node in nodes_list))
        for i, row in enumerate(matrix):
            print(f"{nodes_list[i]}  {row}")

    def has_node(self, node):
        return node in self.nodes

    def get_neighbors(self, node):
        return self.nodes.get(node, [])

    def __str__(self):
        """Строковое представление графа (список вершин и рёбер)."""
        nodes_str = ", ".join(str(n) for n in self.nodes)
        edges_str = ", ".join(f"{e['from']}->{e['to']}({e['weight']})" for e in self.edges)
        return f"Graph(nodes=[{nodes_str}], edges=[{edges_str}])"

    def bfs(graph, start, max_depth=2):

        visited = set()
        queue = deque()

        queue.append((start, 0))
        visited.add(start)

        result = []

        while queue:
            node, depth = queue.popleft()

            if depth > 0:
                result.append(node)

            if depth >= max_depth:
                continue

            for neighbor in graph.nodes[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return result
