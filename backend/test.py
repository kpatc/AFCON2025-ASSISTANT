from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

from llm import init_llm
from rag import init_rag
from tools import get_tools
#  Initialize components
llm = init_llm()
qa_chain = init_rag(llm)
tools = get_tools(qa_chain)

# Load and create prompt template
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    template_content = f.read()

# Get tool names and descriptions
tool_names = [tool.name for tool in tools]
tools_str = "\n".join(f"- {tool.name}: {tool.description}" for tool in tools)

prompt = PromptTemplate(
    template=template_content + "\n\nTools available:\n{tools}\n\nTool Names: {tool_names}\n\nRemember to:\n1. Use Web Search first\n2. Visit found webpages for more details\n3. Process the response\n4. Format the final answer with appropriate emojis\n\nQuestion: {input}\n{agent_scratchpad}",
    input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
)

# Initialize the agent with ReAct framework
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Create agent executor with better tool handling
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=8,  # Increased to allow for proper tool sequence
    return_intermediate_steps=True,
    early_stopping_method="generate"
).with_config({"run_name": "Agent"})

query = f"tell me little bit about morocco"

# Get response from agent with all required variables
result = agent_executor.invoke({
    "input": query,
    "tools": tools_str,
    "tool_names": ", ".join(tool_names)
})

def extract_final_answer_generic(steps):
    for step in reversed(steps):
        if hasattr(step, "tool") and step.tool == "Final Answer":
            return getattr(step, "tool_input", None)
        elif isinstance(step, tuple) and len(step) == 2 and hasattr(step[0], "tool"):
            if step[0].tool == "Final Answer":
                return getattr(step[0], "tool_input", None)
        elif isinstance(step, dict) and step.get("tool") == "Final Answer":
            return step.get("tool_input")
    return None



steps = result.get("intermediate_steps", [])
final_answer = extract_final_answer_generic(steps)
print("✅ Final Answer:", final_answer)
