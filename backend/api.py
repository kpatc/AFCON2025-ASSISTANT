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

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
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
)

class ChatMessage(BaseModel):
    content: str
    role: str
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    response: str

def format_agent_response(result: Dict[str, Any], language: str) -> str:
    """Format the agent's response ensuring proper tool usage sequence."""
    if not result:
        return "Je m'excuse, je n'ai pas pu traiter votre demande. 🙏"
    
        response = result.get("output", "")
    
    # If no direct output, try to construct from intermediate steps
    if not response and result.get("intermediate_steps"):
        steps = result["intermediate_steps"]
        # Look for the final answer step
        for step in reversed(steps):
            if isinstance(step[1], str) and "Final Answer:" in step[1]:
                    response = step[1].replace("Final Answer:", "").strip()
            break

    if not response:
        response = "Je m'excuse, je n'ai pas pu traiter votre demande. 🙏"
                
    return response.strip()

@app.post("/chat")
async def chat_endpoint(message: ChatMessage) -> ChatResponse:
    try:
        # Format query with language preference
        query = f"Respond in {message.language}. User query: {message.content}"
        
        # Get response from agent with all required variables
        result = agent_executor.invoke({
            "input": query,
            "tools": tools_str,
            "tool_names": ", ".join(tool_names)
        })
        
        # Format the response
        formatted_response = format_agent_response(result, message.language)
        
        return ChatResponse(response=formatted_response)
        
    except Exception as e:
                return ChatResponse(
            response="Je m'excuse, une erreur s'est produite. 🙏"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "llm": "operational",
            "agent": "operational",
            "rag": "operational",
            "timestamp": datetime.now().isoformat()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)