from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import Tool
from typing import Type
import json
import os

class WriteFileArgs(BaseModel):
    file_path: str = Field(description="File Path to write to")
    content: str = Field(description="Content to write to file")

class GetDirectoryStructureArgs(BaseModel):
    directory: str = Field(description="Directory to get structure of")

class GetDirectoryStructureTool(BaseTool):
    name = "get_directory_structure"
    description = "Get the directory structure with optional token counts and contents. Usage: get_directory_structure {'directory': '<path>'}"
    args_schema: Type[BaseModel] = GetDirectoryStructureArgs

    def _run(self, directory: str) -> str:
        """Use the tool."""

        def get_directory_structure(directory, indent_level=0):
            structure = []

            try:
                items = os.listdir(directory)
            except PermissionError:
                return " " * indent_level + "[Permission Denied]\n"

            for item in items:
                if item.startswith('.'):
                    continue
                item_path = os.path.join(directory, item)
                structure.append(" " * indent_level + item + "\n")
                if os.path.isdir(item_path):
                    structure.append(get_directory_structure(item_path, indent_level + 2))

            return "".join(structure)
        
        return get_directory_structure(directory)

        


    def _parse_input(self, tool_input: str) -> dict:
        """Parse the input string into arguments."""
        try:
            # Try to parse the input as a JSON string
            args = json.loads(tool_input)
            if not isinstance(args, dict):
                raise ValueError("Input should be a JSON object")
            return args
        except json.JSONDecodeError:
            # If JSON parsing fails, try to evaluate it as a Python dict
            try:
                args = eval(tool_input)
                if not isinstance(args, dict):
                    raise ValueError("Input should be a dictionary")
                return args
            except:
                raise ValueError("Input should be a valid JSON object or Python dictionary")

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write text to a file. Usage: write_file {'file_path': '<path>', 'content': '<content>'}"
    args_schema: Type[BaseModel] = WriteFileArgs

    def _run(self, file_path: str, content: str) -> str:
        """Use the tool."""
        with open(file_path, 'w') as f:
            f.write(content)
        return f"File {file_path} has been modified with content: {content}"

    def _parse_input(self, tool_input: str) -> dict:
        """Parse the input string into arguments."""
        try:
            # Try to parse the input as a JSON string
            args = json.loads(tool_input)
            if not isinstance(args, dict):
                raise ValueError("Input should be a JSON object")
            return args
        except json.JSONDecodeError:
            # If JSON parsing fails, try to evaluate it as a Python dict
            try:
                args = eval(tool_input)
                if not isinstance(args, dict):
                    raise ValueError("Input should be a dictionary")
                return args
            except:
                raise ValueError("Input should be a valid JSON object or Python dictionary")


# Define a very simple tool function that returns the current time
def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime  # Import datetime module to get current time

    now = datetime.datetime.now()  # Get current time
    return now.strftime("%I:%M %p")  # Format time in H:MM AM/PM format


# List of tools available to the agent
tools = [
    Tool(
        name="Time",  # Name of the tool
        func=get_current_time,  # Function that the tool will execute
        # Description of the tool
        description="Useful for when you need to know the current time",
    ),
    GetDirectoryStructureTool(),
    WriteFileTool()
]

# tools = [WriteFileTool()]

# Pull the prompt template from the hub
prompt = hub.pull("hwchase17/react")

# Initialize a ChatOpenAI model
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create the ReAct agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Create an agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True
)

# Run the agent with a test query
response = agent_executor.invoke({"input": "How do I use of /Users/jts/daily/ProjectScout?"})

# Print the response from the agent
print("response:", response) 