"""A2A Adapter for uAgents."""

import asyncio
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec
)

from a2a.client import A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
import uvicorn
import threading
from pydantic import BaseModel


class QueryMessage(BaseModel):
    """Input message model for A2A agent."""
    query: str


class ResponseMessage(BaseModel):
    """Output message model for A2A agent."""
    response: str


class A2AAdapter:
    """Adapter to integrate A2A agents with uAgents."""
    
    def __init__(
        self,
        agent_executor: AgentExecutor,
        name: str,
        description: str,
        port: int = 8000,
        a2a_port: int = 9999,
        mailbox: bool = True,
        seed: Optional[str] = None
    ):
        self.agent_executor = agent_executor
        self.name = name
        self.description = description
        self.port = port
        self.a2a_port = a2a_port
        self.mailbox = mailbox
        self.seed = seed or f"{name}_seed"
        self.a2a_server = None
        self.server_thread = None
        
        # Create uAgent
        self.uagent = Agent(
            name=name,
            port=port,
            seed=self.seed,
            mailbox=mailbox
        )
        
        # Create chat protocol
        self.chat_proto = Protocol(spec=chat_protocol_spec)
        self._setup_protocols()

    def _setup_protocols(self):
        """Setup uAgent protocols."""
        
        @self.chat_proto.on_message(ChatMessage)
        async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
            for item in msg.content:
                if isinstance(item, TextContent):
                    ctx.logger.info(f"📩 Received message from {sender}: {item.text}")
                    try:
                        # Send to A2A agent and get response
                        response = await self._send_to_a2a_agent(item.text)
                        ctx.logger.info(f"🤖 A2A Response: {response[:100]}...")
                        
                        # Send response back to sender
                        response_msg = ChatMessage(
                            timestamp=datetime.now(timezone.utc),
                            msg_id=uuid4(),
                            content=[TextContent(type="text", text=response)]
                        )
                        await ctx.send(sender, response_msg)
                        ctx.logger.info(f"📤 Sent response back to {sender}")
                        
                        # Send acknowledgment for the original message
                        ack_msg = ChatAcknowledgement(
                            timestamp=datetime.now(timezone.utc),
                            acknowledged_msg_id=msg.msg_id
                        )
                        await ctx.send(sender, ack_msg)
                        ctx.logger.info(f"✅ Sent acknowledgment for message {msg.msg_id}")
                        
                    except Exception as e:
                        ctx.logger.error(f"❌ Error processing message: {str(e)}")
                        # Send error response
                        error_response = ChatMessage(
                            timestamp=datetime.now(timezone.utc),
                            msg_id=uuid4(),
                            content=[TextContent(type="text", text=f"❌ Error: {str(e)}")]
                        )
                        await ctx.send(sender, error_response)

        @self.chat_proto.on_message(ChatAcknowledgement)
        async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
            ctx.logger.info(f"✅ Message acknowledged: {msg.acknowledged_msg_id} from {sender}")

        @self.uagent.on_event("startup")
        async def on_start(ctx: Context):
            ctx.logger.info(f"🚀 A2A uAgent started at address: {self.uagent.address}")
            ctx.logger.info(f"🔗 A2A Server running on port: {self.a2a_port}")

        # Include the chat protocol
        self.uagent.include(self.chat_proto, publish_manifest=True)

    async def _send_to_a2a_agent(self, message: str) -> str:
        """Send message to A2A agent and get response."""
        a2a_url = f"http://localhost:{self.a2a_port}"
        
        async with httpx.AsyncClient(timeout=60.0) as httpx_client:
            try:
                # First, get the agent card to verify the server is running
                card_response = await httpx_client.get(f"{a2a_url}/.well-known/agent.json")
                if card_response.status_code != 200:
                    return f"❌ Could not connect to A2A agent at {a2a_url}"
                
                # Try the correct A2A endpoint format
                payload = {
                    "id": uuid4().hex,
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [
                                {
                                    "type": "text",
                                    "text": message,
                                }
                            ],
                            "messageId": uuid4().hex,
                        },
                    }
                }
                
                # Try different possible endpoints
                endpoints_to_try = [
                    "/send-message",
                    "/",
                    "/message",
                    "/chat"
                ]
                
                for endpoint in endpoints_to_try:
                    try:
                        response = await httpx_client.post(
                            f"{a2a_url}{endpoint}",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            # Extract the response content from A2A format
                            if "result" in result:
                                result_data = result["result"]
                                # Handle artifacts format (streaming responses)
                                if "artifacts" in result_data:
                                    artifacts = result_data["artifacts"]
                                    full_text = ""
                                    for artifact in artifacts:
                                        if "parts" in artifact:
                                            for part in artifact["parts"]:
                                                if part.get("kind") == "text":
                                                    full_text += part.get("text", "")
                                    if full_text.strip():
                                        return full_text.strip()
                                # Handle standard parts format
                                elif "parts" in result_data and len(result_data["parts"]) > 0:
                                    response_text = result_data["parts"][0].get("text", "")
                                    if response_text:
                                        return response_text.strip()
                            # Fallback: return what we got
                            return f"✅ Response received from A2A agent"
                        elif response.status_code == 404:
                            continue  # Try next endpoint
                        else:
                            return f"❌ A2A agent returned HTTP {response.status_code} at {endpoint}"
                    except Exception as e:
                        continue  # Try next endpoint
                
                # If all endpoints failed, try direct executor call
                return await self._call_executor_directly(message)
                
            except Exception as e:
                return f"❌ Error communicating with A2A agent: {str(e)}"

    async def _call_executor_directly(self, message: str) -> str:
        """Call the agent executor directly as fallback."""
        try:
            from a2a.server.events import EventQueue
            from a2a.server.agent_execution import RequestContext
            from a2a.types import Part, TextPart, AgentMessage
            from uuid import uuid4
            
            # Create a mock request context
            agent_message = AgentMessage(
                role="user",
                parts=[Part(root=TextPart(type="text", text=message))],
                messageId=uuid4().hex
            )
            
            context = RequestContext(
                message=agent_message,
                context_id=uuid4().hex,
                task_id=uuid4().hex
            )
            
            # Create event queue to capture responses
            event_queue = EventQueue()
            
            # Execute the agent
            await self.agent_executor.execute(context, event_queue)
            
            # Get the response from the event queue
            events = []
            while not event_queue.empty():
                event = await event_queue.dequeue_event()
                if event:
                    events.append(event)
            
            if events:
                # Get the last event which should be the response
                last_event = events[-1]
                if hasattr(last_event, 'parts') and last_event.parts:
                    return last_event.parts[0].text
                elif hasattr(last_event, 'text'):
                    return last_event.text
                else:
                    return str(last_event)
            
            return "✅ Task completed successfully"
            
        except Exception as e:
            return f"❌ Direct executor call failed: {str(e)}"

    def _start_a2a_server(self):
        """Start the A2A server in a separate thread."""
        def run_server():
            # Create A2A server components
            skill = AgentSkill(
                id=f"{self.name.lower()}_skill",
                name=self.name,
                description=self.description,
                tags=[self.name],
                examples=["hi", "hello", "help"],
            )
            
            agent_card = AgentCard(
                name=self.name,
                description=self.description,
                url=f"http://localhost:{self.a2a_port}/",
                version="1.0.0",
                defaultInputModes=["text"],
                defaultOutputModes=["text"],
                capabilities=AgentCapabilities(),
                skills=[skill],
            )
            
            request_handler = DefaultRequestHandler(
                agent_executor=self.agent_executor,
                task_store=InMemoryTaskStore(),
            )
            
            server = A2AStarletteApplication(
                agent_card=agent_card, 
                http_handler=request_handler
            )
            
            uvicorn.run(
                server.build(), 
                host="0.0.0.0", 
                port=self.a2a_port, 
                timeout_keep_alive=10,
                log_level="info"
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait a bit for server to start
        import time
        time.sleep(2)

    def run(self):
        """Run both A2A server and uAgent."""
        print(f"🚀 Starting A2A Adapter for '{self.name}'")
        print(f"📡 A2A Server will run on port {self.a2a_port}")
        print(f"🤖 uAgent will run on port {self.port}")
        
        # Start A2A server
        self._start_a2a_server()
        
        # Run uAgent (this will block)
        self.uagent.run()


class A2ARegisterTool:
    """Tool to register A2A agents as uAgents."""
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register an A2A agent as a uAgent."""
        # Extract parameters
        agent_executor = params["agent_executor"]
        name = params["name"]
        description = params.get("description", f"A2A Agent: {name}")
        port = params.get("port", 8000)
        a2a_port = params.get("a2a_port", 9999)
        mailbox = params.get("mailbox", True)
        seed = params.get("seed")
        api_token = params.get("api_token")
        return_dict = params.get("return_dict", False)
        
        # Create adapter
        adapter = A2AAdapter(
            agent_executor=agent_executor,
            name=name,
            description=description,
            port=port,
            a2a_port=a2a_port,
            mailbox=mailbox,
            seed=seed
        )
        
        result = {
            "agent_name": name,
            "agent_address": adapter.uagent.address,
            "agent_port": port,
            "a2a_port": a2a_port,
            "description": description,
            "mailbox_enabled": mailbox
        }
        
        if return_dict:
            return result
        else:
            return f"Created A2A uAgent '{name}' with address {adapter.uagent.address}"
