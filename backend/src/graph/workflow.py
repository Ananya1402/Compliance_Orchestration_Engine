'''
This module defines the DAG that orchestrates the video compliance audit process
It connects the nodes using the StateGraph from LangGraph

Start->index_video_node->audit_content_node->End
'''
from langgraph.graph import StateGraph, END
from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import (
    index_video_node,
    audio_content_node
)
#StateGraph is used for building stateful workflows

def create_graph():
    '''
    Constructs and compiles the LangGraph workflow
    Returns:
    Compiled Graph: runnable graph object for execution'''
    workflow = StateGraph(VideoAuditState)
    #add the nodes
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audio_content_node)
    #define the entry point: indexer
    workflow.set_entry_point("indexer")
    #define the edges
    workflow.add_edge("indexer", "auditor")
    #once the audit is completed, the workflow ends
    workflow.add_edge("auditor", "END")
    #compile the graph
    app = workflow.compile()
    return app

#expose this runnable app
app = create_graph()

