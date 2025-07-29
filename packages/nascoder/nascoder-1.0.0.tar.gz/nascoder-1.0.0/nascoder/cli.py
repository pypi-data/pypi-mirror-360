#!/usr/bin/env python3
import json
import boto3
import click
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, ClientError

load_dotenv()

console = Console()

# ASCII Art Banner
BANNER = """
███╗   ██╗ █████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
████╗  ██║██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
██╔██╗ ██║███████║███████╗██║     ██║   ██║██║  ██║█████╗  ██████╔╝
██║╚██╗██║██╔══██║╚════██║██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
██║ ╚████║██║  ██║███████║╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

class NasCoder:
    def __init__(self):
        self.bedrock = None
        self.authenticated = False
        self.aws_access_key = None
        self.aws_secret_key = None
        self.aws_region = 'us-east-1'
        self.current_model = 'anthropic.claude-3-opus-20240229-v1:0'
        self.models = {
            'claude-3-opus': 'anthropic.claude-3-opus-20240229-v1:0',
            'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0'
        }
        self.conversation_history = []
        
        # Try to auto-authenticate with existing AWS credentials
        self.try_auto_auth()

    def try_auto_auth(self):
        """Try to authenticate with existing AWS credentials"""
        try:
            # Check for existing AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if credentials:
                self.bedrock = boto3.client('bedrock-runtime', region_name=self.aws_region)
                # Test the connection
                self.bedrock.list_foundation_models()
                self.authenticated = True
                console.print("[green]✓ Authenticated with existing AWS credentials[/green]")
            else:
                console.print("[yellow]⚠ No AWS credentials found. Use /auth to authenticate.[/yellow]")
        except Exception:
            console.print("[yellow]⚠ AWS credentials found but Bedrock access failed. Use /auth to re-authenticate.[/yellow]")

    def authenticate(self):
        """Interactive authentication"""
        console.print(Panel(
            "[bold]AWS Authentication Required[/bold]\n\n"
            "Please provide your AWS credentials with Bedrock access:",
            title="Authentication",
            border_style="yellow"
        ))
        
        access_key = Prompt.ask("AWS Access Key ID", password=False)
        secret_key = Prompt.ask("AWS Secret Access Key", password=True)
        region = Prompt.ask("AWS Region", default="us-east-1")
        
        try:
            # Test credentials
            self.bedrock = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            # Test connection
            self.bedrock.list_foundation_models()
            
            self.authenticated = True
            self.aws_access_key = access_key
            self.aws_secret_key = secret_key
            self.aws_region = region
            
            console.print("[green]✓ Authentication successful![/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Authentication failed: {str(e)}[/red]")
            return False

    def display_banner(self):
        console.print(Text(BANNER, style="bold cyan"))
        auth_status = "[green]Authenticated[/green]" if self.authenticated else "[red]Not Authenticated[/red]"
        console.print(Panel.fit(
            f"[bold green]NasCoder v1.0[/bold green] - AI Assistant powered by AWS Bedrock\n"
            f"Status: {auth_status}\n"
            f"Current Model: [yellow]{self.get_model_name()}[/yellow]\n"
            f"Type [bold]/help[/bold] for commands or [bold]/quit[/bold] to exit",
            border_style="blue"
        ))

    def get_model_name(self):
        for name, model_id in self.models.items():
            if model_id == self.current_model:
                return name
        return "Unknown"

    def send_message(self, message):
        if not self.authenticated:
            return "❌ Please authenticate first using /auth command"
            
        try:
            # Prepare the request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            }

            response = self.bedrock.invoke_model(
                modelId=self.current_model,
                body=json.dumps(body),
                contentType='application/json'
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except Exception as e:
            return f"Error: {str(e)}"

    def handle_command(self, command):
        if command == '/help':
            console.print(Panel(
                "[bold]Available Commands:[/bold]\n"
                "/auth - Authenticate with AWS credentials\n"
                "/models - List available models\n"
                "/switch <model> - Switch to different model\n"
                "/clear - Clear conversation history\n"
                "/status - Show authentication status\n"
                "/quit - Exit NasCoder",
                title="Help",
                border_style="green"
            ))
            return True

        elif command == '/auth':
            self.authenticate()
            return True

        elif command == '/status':
            status = "✅ Authenticated" if self.authenticated else "❌ Not Authenticated"
            console.print(Panel(
                f"Authentication: {status}\n"
                f"Region: {self.aws_region}\n"
                f"Current Model: {self.get_model_name()}",
                title="Status",
                border_style="blue"
            ))
            return True

        elif command == '/models':
            if not self.authenticated:
                console.print("[red]Please authenticate first using /auth[/red]")
                return True
            models_text = "\n".join([f"- {name} {'(current)' if model_id == self.current_model else ''}" 
                                   for name, model_id in self.models.items()])
            console.print(Panel(models_text, title="Available Models", border_style="yellow"))
            return True

        elif command.startswith('/switch '):
            if not self.authenticated:
                console.print("[red]Please authenticate first using /auth[/red]")
                return True
            model_name = command.split(' ', 1)[1]
            if model_name in self.models:
                self.current_model = self.models[model_name]
                console.print(f"[green]Switched to {model_name}[/green]")
            else:
                console.print(f"[red]Model '{model_name}' not found. Use /models to see available options.[/red]")
            return True

        elif command == '/clear':
            self.conversation_history = []
            console.print("[green]Conversation history cleared[/green]")
            return True

        elif command == '/quit':
            console.print("[yellow]Goodbye![/yellow]")
            return False

        return None

    def run(self):
        self.display_banner()
        
        while True:
            try:
                user_input = console.input("\n[bold blue]You:[/bold blue] ").strip()
                
                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    result = self.handle_command(user_input)
                    if result is False:  # /quit command
                        break
                    elif result is True:  # Other commands handled
                        continue

                # Send message to AI
                console.print("\n[bold green]NasCoder:[/bold green]", end=" ")
                
                with console.status("[bold green]Thinking..."):
                    response = self.send_message(user_input)
                
                console.print(response)
                
                # Store in conversation history
                self.conversation_history.append({"user": user_input, "assistant": response})

            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")

@click.command()
def main():
    """NasCoder - AI Assistant powered by AWS Bedrock"""
    nascoder = NasCoder()
    nascoder.run()

if __name__ == "__main__":
    main()
