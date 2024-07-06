import click
import inspect
from typing import List, Dict, Any, Callable
from langchain.tools import Tool
from cli import cli

def extract_click_commands(cli: click.Command) -> Dict[str, click.Command]:
    commands = {}
    if isinstance(cli, click.Group):
        commands = cli.commands
    elif isinstance(cli, click.Command):
        commands = {cli.name: cli}
    return commands

def command_to_tool(command: click.Command) -> Tool:
    def tool_func(input_string: str) -> str:
        print(f"Debug: tool_func received input: {input_string}")
        
        # Split the input string into arguments
        args = input_string.split()
        
        # Match arguments to parameters
        params = command.params
        bound_args = {}
        for i, param in enumerate(params):
            if i < len(args):
                bound_args[param.name] = args[i]
            elif param.default != inspect.Parameter.empty:
                bound_args[param.name] = param.default
            else:
                raise ValueError(f"Missing required argument: {param.name}")

        print(f"Debug: Bound arguments: {bound_args}")

        ctx = click.Context(command)
        try:
            return ctx.invoke(command, **bound_args)
        except Exception as e:
            print(f"Error invoking command: {e}")
            print(f"Command: {command}")
            print(f"Params: {params}")
            raise

    params = [p.name for p in command.params]
    param_str = " ".join([f"<{p}>" for p in params])
    description = f"{command.help or 'No description'}\nUsage: {command.name} {param_str}\nProvide arguments as a single string, separated by spaces."

    return Tool(
        name=command.name,
        func=tool_func,
        description=description
    )

def cli_to_langchain_tools(cli: click.Command) -> List[Tool]:
    commands = extract_click_commands(cli)
    return [command_to_tool(cmd) for cmd in commands.values()]

def create_langchain_tools_from_cli(cli: click.Command) -> List[Tool]:
    if not isinstance(cli, click.Command):
        raise ValueError("Input must be a Click Command or Group")

    return cli_to_langchain_tools(cli)

# Example usage
if __name__ == "__main__":
    # Define a sample Click CLI
    # @click.group()
    # def cli():
    #     pass

    # @cli.command()
    # @click.argument('name')
    # def hello(name):
    #     """Say hello to NAME."""
    #     click.echo(f"Hello, {name}!")

    # @cli.command()
    # @click.option('--count', default=1, help='Number of greetings.')
    # @click.argument('name')
    # def greet(count, name):
    #     """Greet NAME for COUNT times."""
    #     for _ in range(count):
    #         click.echo(f"Hello, {name}!")

    # Convert CLI to LangChain tools
    tools = create_langchain_tools_from_cli(cli)

    # Print the generated tools
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print("---")

    # Equipt agent with tools
