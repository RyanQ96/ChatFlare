import uuid
import networkx as nx 
import warnings
from typing import Union, List, Dict, Any
from chatflare.tracker.base import Branch
from chatflare.graph.memoryinterface import MemoryInterface
from agent_card_server.ActionChatFlare.report import ReportGenerationAction
from chatflare.tracker import Commit, Branch, Blob
from chatflare.agent.task import SRTask
from .nodes import RouteNode
from chatflare.utils.print import log_action_res


class GraphState: 
    """AgentState, current state of the agent, including its environment, memory and working_memory"""
    def __init__(self, environment=None, latest_input=None, latest_output=None, memory:MemoryInterface=None, paper_visited_in_commits=None, human_cached_instructions=None, agent_current_position=None, conversation_history=None, cached_work=None, agent=None): 
        self.environment = environment
        self.latest_input = latest_input
        self.latest_output = latest_output
        self.memory: MemoryInterface = memory # MemoryBank Object
        self.agent = agent
        self.human_cached_instructions = human_cached_instructions or []
        self.conversation_history = conversation_history or []
        self.agent_current_position = agent_current_position
        self.paper_visited_in_commits = paper_visited_in_commits or {} # list of papers id visited
        self.finish_all_articles = False 
        _default_cached_work = {
            "papers_to_read": [], ## List of EmbeddingDocument
            "papers_to_synthesize": [] ## List of EmbeddingDocument.docstore_id
        }
        self.cached_work = cached_work or _default_cached_work

    @property
    def visited_paperids(self):
        res = set() 
        for commit, docs in self.paper_visited_in_commits.items(): 
            res.update(docs)
        return list(res) 

        
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
        if inplace:
            commits = branch.commits
            commitIds = [commit.id for commit in commits]
            head_commit = branch.head_commit 
            head_blob = head_commit.blobs[0]
            # update documents_visited_in_commits
            remained_paper_visited_in_commits = {commitId: docs for commitId, docs in self.paper_visited_in_commits.items() if commitId in commitIds}
            self.paper_visited_in_commits = remained_paper_visited_in_commits
            target_tasks = [] 
            for c in commits: 
                if c.blobs:
                    target_tasks.extend(c.blobs)
            target_task_ids = [task.id for task in target_tasks]
                     
            current_memory_ids = self.memory.all_document_ids
            ## figure out ones need to be removed 
            docs_ids_to_be_removed = [taskId for taskId in current_memory_ids if taskId not in target_task_ids]
            self.memory.delete(docs_ids_to_be_removed)

            for commit in commits[::-1]:
                if commit.blobs[0].result.get("meta") and commit.blobs[0].result["meta"].get("thought"):
                    self.memory.working_memory = commit.blobs[0].result["meta"]["thought"]
                    break
            
            for commit in commits[::-1]:
                if commit.blobs[0].result.get("meta") and commit.blobs[0].result["meta"].get("inspiration_from_conversation"):
                    self.memory.inspiration_conversation_history = commit.blobs[0].result["meta"]["inspiration_from_conversation"]
                    break
            
            for commit in commits[::-1]:
                if commit.blobs[0].result.get("meta") and commit.blobs[0].result.get("agent_current_position"):
                    self.agent_current_position = commit.blobs[0].result["agent_current_position"]
                    break

            self.finish_all_articles = False
            self.cached_work = head_blob.result.get("cached_work", self.cached_work)
            print("reset cached work")
            return self
        else: 
            commits = branch.commits
            commitIds = [commit.id for commit in commits]
            updated_documents_visited_in_commits = {commitId: docs for commitId, docs in self.paper_visited_in_commits.items() if commitId in commitIds}
            
            target_tasks = [] 
            for c in commits: 
                if c.blobs:
                    target_tasks.extend(c.blobs)
            print("old_memory")
            print(self.memory.docstore._dict) 
            new_memory_docs_ids = [task.id for task in target_tasks] # this should be the id for document as well 
            new_memory = self.memory.get_new_memory_from_ids(new_memory_docs_ids)
            print(type(new_memory))
            print("new_memory")
            print(new_memory.docstore._dict) 
            ## Figure out working memory and inspiration_conversation_history
            for commit in commits[::-1]:
                if commit.blobs[0].result.get("meta") and commit.blobs[0].result["meta"].get("thought"):
                    new_memory.working_memory = commit.blobs[0].result["meta"]["thought"]
                    break
            
            for commit in commits[::-1]:
                if commit.blobs[0].result.get("meta") and commit.blobs[0].result.get("meta").get("inspiration_from_conversation"):
                    new_memory.inspiration_conversation_history = commit.blobs[0].result["meta"]["inspiration_from_conversation"]
                    break
            
            updated_agent_current_position = None
            for commit in commits[::-1]:
                if commit.blobs[0].result.get("agent_current_position"):
                    updated_agent_current_position = commit.blobs[0].result["agent_current_position"]
                    break
            newstate = GraphState(environment=self.environment, latest_input=self.latest_input, latest_output=self.latest_output, memory=new_memory, paper_visited_in_commits=updated_documents_visited_in_commits, agent_current_position=updated_agent_current_position, conversation_history=self.conversation_history, agent=self.agent)
            return newstate
        


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

    @property
    def client_handler(self):
        return self.graph_state.agent.client_handler

    @property 
    def article_processing_history(self):
        res = {} 
        for commit in self.branch.commits:
            if commit.blobs:
                blob = commit.blobs[0]
                task_type = blob.task_type
                if task_type == "retrieve": 
                    reception_field = blob.result["meta"]["reception_field_papers"]
                    for docId in reception_field:
                        res[docId] = "visited"
                elif task_type == "read":
                    decision = 'exclude' if blob.result["content"] == 'exclude' else 'include' 
                    docId = blob.result["meta"]["paper_id"]
                    res[docId] = decision 
                else:
                    continue
            else:
                continue
        return res
    

    def create_default_branch(self) -> Branch:
        return Branch("default", agent_id=self.graph_state.agent.agent_id, client_handler=self.client_handler)

    def create_default_graph_state(self) -> GraphState:
        warnings.warn("Memory is not initialized.")
        return GraphState()

    def add_commit(self, commit):
        self.branch.add_commit(commit)
        if commit.blobs and not commit.human_interaction:
            self.graph_state.memory.add_memory_from_commit(commit)
        

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
        self.retrieve_node = None
        self.synthesis_node = None
        self.read_node = None
        self.TRAVERSE_MAX_DEPTH = 5
        self.human_instruction_node = None        
        self.num_traversed = 0 
        self.traverse_thread = traverse_thread  # Information is a bit redundant, but it is necessary to keep track of the thread state
        self.working_status = "IDLE" # IDLE, RUNNING, PAUSED, COMPLETED

    def assign_thread(self, thread: GraphTraverseThread):
        self.traverse_thread = thread

    def __repr__(self):
        return f"BaseGraph(...TO BE IMPLEMENTED...)"

    def add_node(self, node): 
        self.nodes.append(node)
        self.graph.add_node(node)
        if node._NODE_TYPE == "HUMAN_INSTRUCTION_NODE":
            self.human_instruction_node = node

    def add_edge(self, node1, node2, runnable, priority=0): 
        """adding edge will automatically adding a route node and keep track of the edge runnable."""
        self.edges.append((node1, node2, runnable))
        if not self.graph.has_node(node1): self.graph.add_node(node1) 
        if not self.graph.has_node(node2): self.graph.add_node(node2) 
        if len(self.graph.out_edges(node1)) == 0:
            # create route node 
            route_node = RouteNode(source_node=node1)
            route_node.add_target_node(node2, runnable, priority)
            self.graph.add_node(route_node)
            self.graph.add_edge(node1, route_node)
            self.graph.add_edge(route_node, node2, runnable=runnable, priority=priority)
        else: 
            _, route_node = [edge for edge in self.graph.out_edges(node1)][0] # it supposed to have only a sinlge route node 
            route_node.add_target_node(node2, runnable)
            self.graph.add_edge(route_node, node2, runnable=runnable, priority=priority)
        

    def set_start_node(self, node): 
        self.start_node = node

    def set_end_node(self, node):
        self.end_node = node

    def get_edge_runnable(self, edge):
        return self.graph.edges[edge]['runnable']

    def get_edge_priority(self, edge):
        return self.graph.edges[edge]['priority']

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
        _, router_node = list(candidate_edges)[0]

        candidate_edges = self.graph.out_edges(router_node)
        edge_check_map = {} 
        for edge in candidate_edges: 
            _, to_node = edge
            edge_runnable = self.get_edge_runnable(edge) 
            edge_check_map[to_node] = {
                "result": edge_runnable(self.traverse_thread), 
                "priority": self.get_edge_priority(edge)
            }
        # check if only one edge is True 
        # sort the edges by priority
        sorted_edges = sorted(edge_check_map.items(), key=lambda x: x[1]['priority'], reverse=True)
        true_edges = [node for node, obj in sorted_edges if obj['result']]
        
        if len(true_edges) > 0:
            print(f"Next node: {true_edges[0].node_name}")
            return true_edges[0]
        else:
            print(f"No edge is True from {from_node.node_name} Please check your edge conditions.")
            print(self.traverse_thread.graph_state.cached_work)
            raise ValueError(f"No edge is True from {from_node.node_name}, Please check your edge conditions.")

    async def traverse(self): 
        if self.current_node is None: 
            self.current_node = self.start_node 
        while self.current_node != self.end_node and self.num_traversed < self.TRAVERSE_MAX_DEPTH and self.working_status == "RUNNING": 
            yield await self.current_node(self.traverse_thread)            
            next_node = self.route(self.current_node)
            self.current_node = next_node
            self.num_traversed += 1 
            agent = self.traverse_thread.agent or self.traverse_thread.graph_state.agent
            agent.report_agent_working_progress()

    async def arun(self, node=None): 
        try: 
            self.working_status = "RUNNING"
            
            agent = self.traverse_thread.agent or self.traverse_thread.graph_state.agent
            agent.report_agent_working_progress()
            
            if self.num_traversed >= self.TRAVERSE_MAX_DEPTH:
                self.TRAVERSE_MAX_DEPTH += 5

            if node is not None: 
                self.current_node = node

            async for output in self.traverse():
                
                if self.current_node._NODE_TYPE == "HUMAN_INSTRUCTION_NODE" and (not output.get("whether_to_continue_workflow", False)):             
                    self.working_status = "PAUSED" 
                    break
                elif self.current_node._NODE_TYPE == "HUMAN_INSTRUCTION_NODE" and output.get("whether_to_continue_workflow", False):
                    print("Human instruction node is completed.")
                    continue
                else:
                    continue
            if self.current_node == self.end_node:
                self.working_status = "COMPLETED"
            elif self.num_traversed >= self.TRAVERSE_MAX_DEPTH: 
                self.working_status = "REACHED_MAX_DEPTH"
            
            agent.report_agent_working_progress()
            log_action_res(f"Traverse completed. Working status: {self.working_status}")
        except Exception as e: 
            print(e)
            if self.current_node == self.end_node:
                self.working_status = "COMPLETED"
            elif self.num_traversed >= self.TRAVERSE_MAX_DEPTH: 
                self.working_status = "REACHED_MAX_DEPTH"
            else: 
                self.working_status = "PAUSED"
            agent.report_agent_working_progress()

                
    async def take_human_instruction(self, instruction: str):
        self.traverse_thread.graph_state.human_cached_instructions.append(instruction)
        if self.working_status == "PAUSED" or self.working_status == "IDLE" or self.working_status == "COMPLETED" or self.working_status == "REACHED_MAX_DEPTH":
            if self.num_traversed >= self.TRAVERSE_MAX_DEPTH:
                self.TRAVERSE_MAX_DEPTH += 1
        self.current_node = self.human_instruction_node
        await self.arun() 

    
    async def report_generation(self,  agents, cardId, client_handler, query=None, inclusion_exclusion_criteria=None, user_specified_requirement=None, summarization_requirement=None):
        report_action = ReportGenerationAction() 
        await report_action.arun(
            agents, cardId, client_handler, query=query, inclusion_exclusion_criteria=inclusion_exclusion_criteria, user_specified_requirement=user_specified_requirement, summarization_requirement=summarization_requirement
        ) 

        
    def pause_traverse(self): 
        if self.working_status == "RUNNING":
            self.working_status = "PAUSED"
        else:
            print("The graph is not running.")

    async def resume_traverse(self): 
        """"""
        if self.working_status == "PAUSED":
            self.current_node = self.route(self.current_node)
            await self.arun()
        elif self.working_status == "IDLE": 
            await self.arun()
        elif self.working_status == "REACHED_MAX_DEPTH":
            self.TRAVERSE_MAX_DEPTH += 5 
            await self.arun()
        elif self.working_status == "COMPLETED":
            print("The graph is already completed.")
        else:
            print("The graph is not paused.")
            

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