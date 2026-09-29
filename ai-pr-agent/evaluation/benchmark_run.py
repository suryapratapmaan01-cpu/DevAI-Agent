import json
import asyncio
from tabulate import tabulate
from app.agent import agent_executor

async def run_evaluation_benchmark():
    print("🚀 Initializing Agentic AI Code Fix Benchmark Pipeline...")
    
    with open("evaluation/test_suite.json", "r") as f:
        benchmarks = json.load(f)
        
    results = []
    
    for test in benchmarks:
        print(f"\nEvaluating Task ID: {test['task_id']} - {test['description']}")
        
        # Inject the broken base state into our Agent's memory execution model
        input_state = {
            "repo_name": "eval/local-sandbox",
            "pr_number": 0,
            "diff": f"Issue Description: {test['description']}\nBase Files Provided:\n{json.dumps(test['base_code'])}",
            "proposed_files": test["base_code"],
            "iteration_count": 0,
            "status": "pending"
        }
        
        # Invoke the LangGraph workflow directly via async runtime execution loops
        output_state = await agent_executor.ainvoke(input_state)
        
        # Inject the gold test validation parameter suite explicitly to see if the fix genuinely worked
        final_files = output_state.get("proposed_files", {})
        final_files[test["gold_test_file"]] = test["gold_test_content"]
        
        # Execute a final standalone safety pass over the updated structures inside our container sandbox
        from app.tools import run_in_sandbox
        eval_run = run_in_sandbox(commands=[test["verification_command"]], code_files=final_files)
        
        is_fixed = eval_run["success"]
        results.append({
            "Task ID": test["task_id"],
            "Description": test["description"],
            "Agent Iterations": output_state.get("iteration_count", 0),
            "Status": "PASSED ✅" if is_fixed else "FAILED ❌"
        })
        
    # Print out beautifully formatted metric outcomes directly onto terminal pipelines
    print("\n📊 FINAL SYSTEM PERFORMANCE SCORES:")
    print(tabulate(results, headers="keys", tablefmt="grid"))
    
    success_rate = (sum(1 for r in results if "PASSED" in r["Status"]) / len(results)) * 100
    print(f"\n🎯 Overall Fix Success Rate: {success_rate:.2f}%")

if __name__ == "__main__":
    asyncio.run(run_evaluation_benchmark())
