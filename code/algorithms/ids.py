from code.heartofitall.search_results import SearchResult
import time

class IDS:
    def __init__(self, graph, start, goal):
        self.graph = graph
        self.start = start
        self.goal = goal
        self.nodes_expanded = 0

    def search(self)-> SearchResult:
        depth = 0
        start_time = time.time()
        result = None
        while True:
            #print(depth)
            result = self.depth_limited_search(self.start, depth, [self.start])
            if result is not None or depth>50:
                break
            depth+=1

        #print(result)

        run_time = time.time()-start_time
        cost = 0.0
        for a, b in zip(result, result[1:]):
            cost += self.graph.get_distance(a, b)

        if result:
            return SearchResult(
                algorithm_name="IDS",
                start=self.start,
                goal=self.goal,
                path=result,
                cost=cost,
                nodes_expanded=self.nodes_expanded,
                runtime=run_time,
                is_optimal=False
            )
        else:
            return SearchResult(
                algorithm_name="IDS",
                start=self.start,
                goal=self.goal,
                path=[],
                cost=float("inf"),
                nodes_expanded=self.nodes_expanded,
                runtime=run_time,
                is_optimal=False
            )


    def depth_limited_search(self, node, depth, path):
        if node == self.goal:
            return [node]
        if depth == 0:
            return None
        #print([node])
        self.nodes_expanded+=1
        for neighbor, dist in self.graph.get_neighbors(node).items():
            if neighbor not in path:
                result = self.depth_limited_search(neighbor, depth - 1, path+[neighbor])
                if result is not None:
                    return [node] + result
        return None
