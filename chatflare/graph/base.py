import uuid
import networkx as nx 
import warnings
from typing import Union, List, Dict, Any
from chatflare.tracker.base import Branch
from chatflare.graph.memoryinterface import MemoryInterface
from chatflare.tracker import Commit, Branch, Blob
from chatflare.agent.task import SRTask

class GraphState: 
    """AgentState, current state of the agent, including its environment, memory and working_memory"""
    def __init__(self, environment=None, latest_input=None, latest_output=None, memory:MemoryInterface=None, paper_visited_in_commits={}): 
        self.environment = environment
        self.latest_input = latest_input
        self.latest_output = latest_output
        self.memory: MemoryInterface = memory # MemoryBank Object
        self.agent = None 
        self.human_cached_instructions = [] 
        self.paper_visited_in_commits = paper_visited_in_commits # list of papers visited
        self.cached_work = {
            "papers_to_read": [] ## List of EmbeddingDocument
        }

    def add_human_instruction(self, instruction):
        self.human_cached_instructions.append(instruction)

    def update_state(self, output):
        self.latest_output = output

    def register_agent(self, agent):
        """Potentially needed to register the agent to the state."""

    def __repr__(self):
        return f"GraphState(...TO BE IMPLEMENTED...)"

    @classmethod
    def initialize_for_agent(cls, agent):
        """Initialize the state for the agent."""
        return cls(environment=agent.environment, latest_input=None, latest_output=None, memory=None)
    
    def sync_with_branch(self, branch:Branch, inplace=False): 
        """
        Assumption here: the branch contains the commits that are the prefix of the old branch. 
        """
        ## TODO: update environment or think about how to align environment with the branch 
        if inplace:
            commits = branch.commits
            # update documents_visited_in_commits
            for c in self.document_visited_in_commits: 
                if c not in commits:
                    ## remove c.id as key of the dict   
                    self.document_visited_in_commits.pop(c)
            
            target_tasks = [] 
            for c in commits: 
                if c.blobs:
                    target_tasks.extend(c.blobs)
            target_task_ids = [task.id for task in target_tasks]
                     
            current_memory_ids = self.memory.all_document_ids
            ## figure out ones need to be removed 
            docs_ids_to_be_removed = [taskId for taskId in current_memory_ids if taskId not in target_task_ids]
            self.memory.delete(docs_ids_to_be_removed)
            ## TODO: update the lastest_input and latest_output
            return self
        else: 
            commits = branch.commits
            updated_documents_visited_in_commits = {commitId: docs for commitId, docs in self.document_visited_in_commits.items() if commitId in commits}
            
            target_tasks = [] 
            for c in commits: 
                if c.blobs:
                    target_tasks.extend(c.blobs)
            new_memory_docs_ids = [task.id for task in target_tasks] # this should be the id for document as well 
            new_memory = self.memory.get_new_memory_from_ids(new_memory_docs_ids)
            ## TODO: update the lastest_input and latest_output
            return GraphState(environment=self.environment, latest_input=self.latest_input, latest_output=self.latest_output, memory=new_memory, paper_visited_in_commits=paper_visited_in_commits)
        


class GraphTraverseThread: 
    """Thread contains both the actual data: GraphState (memory) and the version tracking: Branch."""
    def __init__(self, graph_state:GraphState = None, branch:Branch = None, agent=None, task: SRTask=None): 
        self.thread_id = uuid.uuid4()
        if graph_state is None:
            graph_state = self.create_default_graph_state()
        self.graph_state: GraphState = graph_state 
        if branch is None:
            branch = self.create_default_branch()
        self.branch = branch
        self.agent = agent
        self.task = task

    def create_default_branch(self):
        return Branch("default")

    def create_default_graph_state(self) -> GraphState:
        warnings.warn("Memory is not initialized.")
        return GraphState()

    def add_commit(self, commit):
        self.branch.add_commit(commit)
        if commit.blobs:
            self.graph_state.memory.add_memory_from_commit(commit)
            ## TODO: update articles_visited_in_commits
        else:
            warnings.warn("Incomplete commit. No blobs found.")

    def rollback(self, commitOrId: Union[str, Commit], inplace=False):
        """
        Roll back the thread to a previous commit and update graphstate.
        """
        if isinstance(commitOrId, Commit):
            commitId = commitOrId.id
        else:
            commitId = commitOrId
            
        if inplace: 
            self.branch.rollback(commitOrId, inplace=True)
            self.graph_state.sync_with_branch(self.branch, inplace=True)
        else:
            ## 1: create a new branch with the rolled back commits
            new_branch = self.branch.rollback(commitOrId, inplace=False)
            ## 2: create a new graphstate with the rolled back memory
            new_graph_state = self.graph_state.sync_with_branch(new_branch, inplace=False)
            ## 3: return the new thread
            return GraphTraverseThread(graph_state=new_graph_state, branch=new_branch, agent=self.agent, task=self.task)
            
    def create_new_thread_from_branch(self, branch:Branch):
        """ 
        Create a new thread from a particular commit in the branch, create a new graphstate, 
        and return the new thread.
        """
        raise NotImplementedError("Method not implemented")



class BaseGraph: 
    def __init__(self, traverse_thread=None): 
        self.graph = nx.DiGraph()
        self.nodes = []
        self.edges = []
        self.start_node = None 
        self.end_node = None 
        self.current_node = None
        self.TRAVERSE_MAX_DEPTH = 20
        self.num_traversed = 0 
        self.traverse_thread = traverse_thread  # Information is a bit redundant, but it is necessary to keep track of the thread state

    def assign_thread(self, thread: GraphTraverseThread):
        self.traverse_thread = thread

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


    def route(self, from_node): 
        """Return the next node to route to."""

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

    async def traverse(self): 
        if self.current_node is None: 
            self.current_node = self.start_node 
        
        while self.current_node != self.end_node and self.num_traversed < self.TRAVERSE_MAX_DEPTH: 
            yield await self.current_node(self.traverse_thread)
            next_node = self.route(current_node, thread_id)
            current_node = next_node
            num_traversed += 1 


    def pause_traverse(self): 
        pass 

    def resume_traverse(self): 
        """"""
        pass

    def compile(self):
        """Automatically compile the graph to a format that can be executed."""
        raise NotImplementedError("Method not implemented") 

    def visualize(self):
        """Visualize the graph."""
        ## traverse the graph from the start_node 
        
        if len(self.nodes) == 0:
            raise ValueError("No nodes in the graph.")
        if self.start_node is None:
            self.start_node = self.nodes[0]
        
        flowchart_mermaid_str = "flowchart TD\n"
        visited = set()
        queue = [self.start_node]
        while queue: 
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                ## if no edges add the single node
                if len(self.graph.out_edges(vertex)) == 0:
                    flowchart_mermaid_str += f"\t{vertex.node_name}\n"
                else: 
                    for edge in self.graph.out_edges(vertex): 
                        _, to_node = edge 
                        queue.append(to_node)
                        flowchart_mermaid_str += f"\t{vertex.node_name} --> {to_node.node_name}\n"             

        import mermaid as md 
        from mermaid.graph import Graph
        graph = Graph('example-flowchart', flowchart_mermaid_str)
        graphe = md.Mermaid(graph)
        return graphe