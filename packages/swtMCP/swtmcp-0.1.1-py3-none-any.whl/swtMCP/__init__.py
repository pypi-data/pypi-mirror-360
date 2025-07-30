# server.py
from mcp.server.fastmcp import FastMCP
import sqlite3
from openai import OpenAI
from sklearn.metrics import accuracy_score, precision_score, recall_score
import requests

# Create an MCP server
mcp = FastMCP("CreditRisk")


# Add an addition tool
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a fetching data tool
@mcp.tool()
def fetch_credit_data(database: str, query: str) -> list:
    """Fetch credit data from a database"""
    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data

# Add a tool to generate code using an LLM
@mcp.tool()
def generate_code(description: str) -> str:
    """Generate code for credit risk model tasks using Qwen model"""

    # Define the API details
    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1/',
        api_key='d61c742c-cd80-4c71-9dbd-86908ca57de7'
    )

    # Prepare the prompt for the LLM
    prompt = f"Generate Python code for: {description}"

    # Call the LLM to generate the code
    rsp = client.chat.completions.create(
        model='Qwen/Qwen3-235B-A22B',  # Specify the correct Qwen model
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Return the generated code
    return rsp.choices[0].message.content

# Model Evaluation Tool
@mcp.tool()
def evaluate_model(y_true: list, y_pred: list) -> dict:
    """Evaluate a model for credit risk prediction"""
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall
    }


# API Data Fetching Tool
@mcp.tool()
def fetch_credit_score(api_url: str, user_id: str) -> dict:
    """Fetch credit score data from an API"""
    response = requests.get(f"{api_url}/score/{user_id}")
    data = response.json()  # Assuming the response is in JSON format
    return data


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main() -> None:
    mcp.run(transport = "stdio")
