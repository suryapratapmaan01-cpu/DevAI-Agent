from typing import Annotated, TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.tools import fetch_pr_diff, run_in_sandbox, post_pr_review_comment
from app.config import settings

# Define Agent State
class AgentState(TypedDict):
    repo_name: str
    pr_number: int
    diff: str
    plan: str
    proposed_files: Dict[str, str]
    sandbox_logs: str
    iteration_count: int
    status: str

llm = ChatOpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)

def context_retriever_node(state: AgentState) -> Dict:
    diff = fetch_pr_diff(state["repo_name"], state["pr_number"])
    return {"diff": diff, "iteration_count": 0
    # "proposed_files": {}, # Explicitly initialize to prevent KeyErrors
    #     "plan": "",
    #     "sandbox_logs": "",
    #     "status": "pending
        }

def planner_executor_node(state: AgentState) -> Dict:
    prompt = f"""
    Analyze the following Pull Request Diff and suggest bug fixes along with comprehensive unit tests:
    {state['diff']}
    
    Previous sandbox execution history or failures: {state.get('sandbox_logs', 'None')}
    
    Return your output in structured JSON format containing two keys:
    1. "plan": Explanation of modifications
    2. "files": Dict of filename strings to code values.
    """
    # Force JSON evaluation mode
    response = llm.invoke(prompt, response_format={"type": "json_object"})
    import json
    data = json.loads(response.content)
    return {"plan": data.get("plan"), "proposed_files": data.get("files", {})}

def sandbox_verifier_node(state: AgentState) -> Dict:
    files = state["proposed_files"]
    # We automatically target running black/ruff/pytest over the written structures
    commands = ["black --check .", "ruff check .", "pytest"]
    result = run_in_sandbox(commands=commands, code_files=files)
    
    return {
        "sandbox_logs": result["log"], 
        "status": "passed" if result["success"] else "failed",
        "iteration_count": state["iteration_count"] + 1
    }

def route_verification(state: AgentState):
    if state["status"] == "passed" or state["iteration_count"] >= 3:
        return "submit"
    return "plan"

def execution_submittal_node(state: AgentState) -> Dict:
    review_template = f"""
    ### 🤖 Automated Agentic Code Review
    
    **Planning Analysis**:
    {state['plan']}
    
    **Sandbox Verification Status**: `{state['status'].upper()}`
    
    ```text
    {state['sandbox_logs']}
    ```
    
    *Review status needs maintainer validation prior to merging branches.*
    """
    post_pr_review_comment(state["repo_name"], state["pr_number"], review_template)
    return {"status": "completed"}

# Build execution graph topology
workflow = StateGraph(AgentState)
workflow.add_node("retrieve_context", context_retriever_node)
workflow.add_node("plan_and_edit", planner_executor_node)
workflow.add_node("verify_sandbox", sandbox_verifier_node)
workflow.add_node("submit_review", execution_submittal_node)

workflow.set_entry_point("retrieve_context")
workflow.add_edge("retrieve_context", "plan_and_edit")
workflow.add_edge("plan_and_edit", "verify_sandbox")
workflow.add_conditional_edges("verify_sandbox", route_verification, {"plan": "plan_and_edit", "submit": "submit_review"})
workflow.add_edge("submit_review", END)

agent_executor = workflow.compile()
