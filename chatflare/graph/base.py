import uuid
import networkx as nx 
from chatflare.tracker.base import Branch

class GraphState: 
    def __init__(self): 
        self.environment = None 
        self.latest_input = None 
        self.latest_output = None 
        self.memory = None # MemoryBank Object

    def __repr__(self):
        return f"GraphState(...TO BE IMPLEMENTED...)"

    def sync_with_branch(self, branch:Branch): 
        pass


class GraphTraverseThread: 
    """Thread contains both the actual data: GraphState and the version tracking: Branch."""
    def __init__(self, graph_state:GraphState = None, branch:Branch = None): 
        self.thread_id = uuid.uuid4()
        if graph_state is None:
            graph_state = self.create_default_graph_state()
        self.graph_state = graph_state 
        if branch is None:
            branch = self.create_default_branch()
        self.branch = branch

    def create_default_branch(self):
        return Branch("default")

    def create_default_graph_state(self):
        return GraphState()

    def commit(self):
        pass

    def rollback(self, commit_id):
        """
        Roll back the thread to a previous commit and update graphstate.
        """
        pass
    
    def create_new_thread_from_branch(self, branch:Branch):
        """ 
        Create a new thread from a particular commit in the branch, create a new graphstate, 
        and return the new thread.
        """
        raise NotImplementedError("Method not implemented")

class RouteNode: 
    def __init__(self, source_node=None, outer_edges=[]):
        self._NODE_TYPE = "ROUTE_NODE"
        self.node_name = f"RouteNode-{str(uuid.uuid4())[:4]}"
        self.source_node = source_node
        self.outer_edges = outer_edges
    
    @property 
    def NODE_TYPE(self):
        return self._NODE_TYPE

    def __repr__(self):
        return f"RouteNode(source_node={self.source_node})"

    def add_target_node(self, edge, runnable):
        if edge not in self.outer_edges:
            self.outer_edges.append(edge)

class BaseGraph: 
    def __init__(self): 
        self.graph = nx.DiGraph()
        self.nodes = []
        self.edges = []
        self.start_node = None 
        self.end_node = None 
        self.TRAVERSE_MAX_DEPTH = 10
        self.traverse_thread = {} 
        # self.graph_state:GraphState = None # state that each node and edges leverage to retrieve input and output information

    def initialize_thread(self, new_thread=None): 
        if new_thread is None: 
            new_thread = GraphTraverseThread()
            self.traverse_thread[new_thread.thread_id] = new_thread
        else:
            self.traverse_thread[new_thread.thread_id] = new_thread

    def __repr__(self):
        return f"BaseGraph(...TO BE IMPLEMENTED...)"

    def add_node(self, node): 
        self.nodes.append(node)
        self.graph.add_node(node)

    def add_edge(self, node1, node2, runnable): 
        """adding edge will automatically adding a route node and keep track of the edge runnable."""
        self.edges.append((node1, node2, runnable))
        if not self.graph.has_node(node1): self.graph.add_node(node1) 
        if not self.graph.has_node(node2): self.graph.add_node(node2) 
        if len(self.graph.out_edges(node1)) == 0:
            # create route node 
            route_node = RouteNode(source_node=node1)
            route_node.add_target_node(node2, runnable)
            self.graph.add_node(route_node)
            self.graph.add_edge(node1, route_node)
            self.graph.add_edge(route_node, node2, runnable=runnable)
        else: 
            _, route_node = [edge for edge in self.graph.out_edges(node1)][0] # it supposed to have only a sinlge route node 
            route_node.add_target_node(node2, runnable)
            self.graph.add_edge(route_node, node2, runnable=runnable)
        

    def set_start_node(self, node): 
        self.start_node = node

    def set_end_node(self, node):
        self.end_node = node

    def get_edge_runnable(self, edge):
        return self.graph.edges[edge]['runnable']

    def _programmic_route_or_llm_route(self, from_node):
        llm_edge = False 
        for edge in self.graph.out_edges(from_node):
            if hasattr(edge, 'llm_edge') and edge.llm_edge:
                llm_edge = True 
                break
        return llm_edge


    def route(self, from_node, thread_id): 
        """Return the next node to route to."""
        if thread_id is None:
            thread_id = list(self.traverse_thread.keys())[0]

        if self._programmic_route_or_llm_route(from_node):
            pass

        candidate_edges = self.graph.out_edges(from_node)
        edge_check_map = {} 
        for edge in candidate_edges: 
            _, to_node = edge
            edge_runnable = self.get_edge_runnable(edge) 
            edge_check_map[to_node] = edge_runnable(self.traverse_thread[thread_id].graph_state)
        # check if only one edge is True 
        true_edges = [node for node, is_true in edge_check_map.items() if is_true]
        if len(true_edges) == 1: 
            return true_edges[0]
        elif len(true_edges) == 0: 
            """Invovlve LLM to generate a response."""
            raise ValueError("No edge is True. Please check your edge conditions.")
        else: 
            """Invovlve LLM to generate a response/make a selection."""
            raise ValueError("Multiple edges are True. Please check your edge conditions.")

    def traverse(self, thread_id=None): 
        if thread_id is None:
            thread_id = list(self.traverse_thread.keys())[0]
        current_node = self.start_node
        num_traversed = 0
        while current_node != self.end_node and num_traversed < self.TRAVERSE_MAX_DEPTH: 
            yield current_node(self.traverse_thread[thread_id].graph_state)
            next_node = self.route(current_node, thread_id)
            current_node = next_node
            num_traversed += 1 


    def pause_traverse(self): 
        pass 

    def resume_traverse(self): 
        pass

    def compile(self):
        """Automatically compile the graph to a format that can be executed."""
        raise NotImplementedError("Method not implemented") 

    def visualize(self):
        """Visualize the graph."""
        ## traverse the graph from the start_node 
        flowchart_mermaid_str = "flowchart TD\n"
        visited = set()
        queue = [self.start_node]
        while queue: 
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                for edge in self.graph.out_edges(vertex): 
                    _, to_node = edge 
                    queue.append(to_node)
                    flowchart_mermaid_str += f"\t{vertex.node_name} --> {to_node.node_name}\n"             

        import mermaid as md 
        from mermaid.graph import Graph
        graph = Graph('example-flowchart', flowchart_mermaid_str)
        graphe = md.Mermaid(graph)
        return graphe