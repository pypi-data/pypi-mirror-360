#!/usr/bin/env python3
"""
PrimVoices Debugger - Python CLI Version

A command-line debugger for PrimVoices agents that provides real-time monitoring
and interaction capabilities similar to the React-based debugger.

Features:
- WebSocket communication with PrimVoices agents
- Real-time audio capture and playback
- Text message sending
- Debug message monitoring and display
- Audio level monitoring
- Session management
- Configuration presets
"""

import asyncio
import base64
import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import threading
import queue
from ..utils.config import (
    API_BASE_URL,
    TITLE_STYLE,
    USER_COLOR,
    AGENT_COLOR,
    ID_STYLE,
    USER_STYLE,
)
from ..utils.utils import (
    print_success, print_warning, print_error, print_info,
    get_authenticated_session
)

try:
    import websockets
    import pyaudio
    import numpy as np
    import sounddevice as sd
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError as e:
    print_error(f"Missing required dependency: {e}")
    print_info("Please install required packages:")
    print_info("pip install websockets pyaudio numpy sounddevice soundfile rich")
    sys.exit(1)

# Commands that are supported by the debugger
SUPPORTED_COMMANDS = [
    "help",
    "status",
    "messages",
    "clear",
    "config",
    "quit",
    "exit",
    "q",
    "x",
    "debug",
    "send"
]


@dataclass
class DebugMessage:
    """Represents a debug message from the agent"""
    type: str
    turn: int
    name: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AudioStats:
    """Audio statistics for monitoring"""
    level: float
    is_speaking: bool
    is_playback: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WebSocketConfig:
    """Configuration for WebSocket connection"""
    agent: dict
    environment: dict
    function: dict
    server_url: Optional[str] = None
    api_url: str = API_BASE_URL
    custom_parameters: Dict[str, str] = field(default_factory=dict)


class AudioProcessor:
    """Handles audio capture, processing, and playback"""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False
        self.audio_queue = queue.Queue()
        self.recording_thread = None
        self.playback_thread = None
        self.play_queue: "list[tuple[np.ndarray,int]]" = []
        
    def start_recording(self):
        """Start recording audio from microphone"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recording(self):
        """Stop recording audio"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=1)
            
    def _record_audio(self):
        """Internal method to record audio"""
        try:
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.is_recording:
                try:
                    data = stream.read(
                        self.chunk_size, 
                        exception_on_overflow=False
                    )
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    self.audio_queue.put(audio_data)
                except Exception as e:
                    logging.error(f"Error reading audio: {e}")
                    break
                    
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logging.error(f"Error in audio recording: {e}")
            
    def get_audio_chunk(self) -> Optional[np.ndarray]:
        """Get the next audio chunk from the queue"""
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None
            
    def play_pcm_bytes(
        self, 
        audio_bytes: bytes, 
        sample_rate: int = 24000
    ):
        """Play raw 16-bit little-endian PCM bytes (mono) asynchronously."""
        if self.is_playing:
            # queue subsequent chunks
            pcm = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32767.0
            pcm = self._trim_silence(pcm)
            self.play_queue.append((pcm, sample_rate))
            return

        def _play(initial_pcm=None):
            try:
                if initial_pcm is not None:
                    pcm = initial_pcm
                else:
                    pcm = np.frombuffer(
                        audio_bytes, 
                        dtype=np.int16
                    ).astype(np.float32) / 32767.0
                pcm = self._trim_silence(pcm)
                sr = sample_rate
                while True:
                    sd.play(pcm, sr)
                    sd.wait()
                    if not self.play_queue:
                        break
                    pcm, sr = self.play_queue.pop(0)
            except Exception as e:
                logging.error(f"Error playing audio: {e}")
            finally:
                self.is_playing = False

        self.is_playing = True
        initial_pcm = np.frombuffer(
            audio_bytes, 
            dtype=np.int16
        ).astype(np.float32) / 32767.0
        initial_pcm = self._trim_silence(initial_pcm)
        t = threading.Thread(target=_play, args=(initial_pcm,), daemon=True)
        t.start()
        
    def get_audio_level(self, audio_data: np.ndarray) -> float:
        """Calculate audio level from audio data"""
        if len(audio_data) == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio_data**2)))
        
    def is_speaking(
        self, 
        audio_data: np.ndarray, 
        threshold: float = 0.01
    ) -> bool:
        """Detect if audio contains speech"""
        level = self.get_audio_level(audio_data)
        return level > threshold
        
    def mu_law_encode(self, audio_data: np.ndarray) -> bytes:
        """Encode audio data to μ-law format"""
        # Convert float32 to int16
        int16_data = (audio_data * 32767).astype(np.int16)
        
        # Simple μ-law encoding (basic implementation)
        mu_law_data = []
        for sample in int16_data:
            # μ-law encoding algorithm
            sign = 1 if sample >= 0 else 0
            sample = abs(sample)
            
            if sample >= 32768:
                sample = 32767
                
            # Find the segment
            segment = 0
            if sample >= 256:
                segment = 1
            if sample >= 512:
                segment = 2
            if sample >= 1024:
                segment = 3
            if sample >= 2048:
                segment = 4
            if sample >= 4096:
                segment = 5
            if sample >= 8192:
                segment = 6
            if sample >= 16384:
                segment = 7
                
            # Calculate quantization
            quantization = (sample >> (segment + 3)) & 0x0F
            
            # Combine into μ-law byte
            mu_law_byte = (sign << 7) | (segment << 4) | quantization
            mu_law_data.append(mu_law_byte)
            
        return bytes(mu_law_data)
        
    def mu_law_decode(self, mu_law_data: bytes) -> np.ndarray:
        """Decode μ-law data to audio"""
        # Simple μ-law decoding (basic implementation)
        audio_data = []
        for byte in mu_law_data:
            # Extract components
            sign = (byte >> 7) & 1
            segment = (byte >> 4) & 0x07
            quantization = byte & 0x0F
            
            # Reconstruct sample
            sample = quantization << (segment + 3)
            if segment > 0:
                sample += 1 << (segment + 2)
                
            if sign == 0:
                sample = -sample
                
            # Convert to float32
            audio_data.append(sample / 32767.0)
            
        return np.array(audio_data, dtype=np.float32)

    @staticmethod
    def _trim_silence(
        pcm: np.ndarray, 
        threshold: float = 0.001
    ) -> np.ndarray:
        """Remove leading and trailing silence to minimise inter-chunk gaps."""
        if pcm.size == 0:
            return pcm

        abs_pcm = np.abs(pcm)
        idx = np.where(abs_pcm > threshold)[0]
        if idx.size == 0:
            return pcm
        start = idx[0]
        end = idx[-1] + 1
        return pcm[start:end]


class PrimVoicesDebugger:
    """Main debugger class that handles WebSocket communication and UI"""
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        self.console = Console()
        self.audio_processor = AudioProcessor()
        self.websocket = None
        self.is_connected = False
        self.is_listening = False
        self.is_playing = False
        
        # Session IDs
        self.call_sid = str(uuid.uuid4())
        self.stream_sid = str(uuid.uuid4())
        
        # Message tracking
        self.debug_messages: List[DebugMessage] = []
        self.current_turn = 0
        self.audio_stats: Optional[AudioStats] = None
        
        # Callbacks
        self.on_message: Optional[Callable] = None
        self.on_audio_stats: Optional[Callable] = None
        self.on_debug_message: Optional[Callable] = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def get_agent_configuration(self) -> Dict[str, Any]:
        """Get agent configuration from API"""
        import aiohttp
        
        query_params = {
            'inputType': 'mic',
            'environment': self.config.environment['name']
        }
        
        # Add custom parameters
        for key, value in self.config.custom_parameters.items():
            query_params[f'custom_{key}'] = value
            
        self.logger.info(
            f"Getting agent configuration for {self.config.agent['name']} in {self.config.environment['name']}"
        )
        url = f"{self.config.api_url}/v1/agents/{self.config.agent['id']}/call"
        self.logger.info(f"API URL: {url}")
        self.logger.info(f"Query params: {query_params}")
        
        # Use authenticated session for consistent auth handling
        session = get_authenticated_session()
        
        try:
            async with aiohttp.ClientSession() as aio_session:
                # Copy auth headers from requests session to aiohttp session
                # if 'Cookie' in session.headers:
                #     headers = {'Cookie': session.headers['Cookie']}
                # else:
                #     headers = {}
                    
                async with aio_session.post(
                    url, 
                    params=query_params, 
                    json={}
                ) as response:
                    self.logger.info(f"API response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Agent configuration: {data}")
                        return data.get('data', {})
                    else:
                        response_text = await response.text()
                        self.logger.error(f"API error response: {response_text}")
                        raise Exception(
                            f"Failed to get agent configuration: {response.status} - {response_text}"
                        )
        except Exception as e:
            # Handle HTTP errors consistently
            print_error(f"Failed to get agent configuration: {e}")
            raise

    async def connect(self):
        """Establish WebSocket connection"""
        try:
            # Production mode - get agent configuration from API first
            agent_config = await self.get_agent_configuration()
            self.config.server_url = agent_config.get('url')
            self.config.custom_parameters.update(
                agent_config.get('parameters', {})
            )
            
            if not self.config.server_url:
                raise Exception("No server URL available from agent configuration")
                
            self.logger.info(
                f"Connecting to production WebSocket server: "
                f"{self.config.server_url}"
            )
            self.logger.info(
                f"Session IDs: call={self.call_sid}, stream={self.stream_sid}"
            )
            self.logger.info(f"Agent ID: {self.config.agent['id']}")
            self.logger.info(f"Environment: {self.config.environment['name']}")
            
            # Connect to WebSocket
            self.logger.info(
                f"Attempting to connect to WebSocket: {self.config.server_url}"
            )
            self.websocket = await websockets.connect(self.config.server_url)
            self.logger.info("WebSocket connection established successfully")
            self.is_connected = True
            
            # Send start message in the format expected by the production server
            start_message = {
                "start": {
                    "streamSid": self.stream_sid,
                    "callSid": self.call_sid,
                    "customParameters": {
                        **self.config.custom_parameters,
                        "agentId": self.config.agent['id'],
                        "environment": self.config.environment['name'],
                        "inputType": "mic",
                        "functionId": self.config.function['id']
                    }
                }
            }
            
            self.logger.info(
                f"Sending start message: {json.dumps(start_message, indent=2)}"
            )
            await self.websocket.send(json.dumps(start_message))
            self.logger.info("Start message sent successfully")
            
            # Start message listener
            asyncio.create_task(self._message_listener())
            
        except Exception as e:
            print_error(f"Failed to connect: {e}")
            raise
            
    async def disconnect(self):
        """Close WebSocket connection"""
        self.is_connected = False
        self.is_listening = False
        self.is_playing = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        self.audio_processor.stop_recording()
        self.logger.info("Disconnected")
        
    async def _message_listener(self):
        """Listen for incoming WebSocket messages"""
        try:
            self.logger.info("Starting message listener...")
            async for message in self.websocket:
                self.logger.info(f"Received raw message: {message}")
                try:
                    parsed_message = json.loads(message)
                    self.logger.info(f"Parsed message: {parsed_message}")
                    await self._handle_message(parsed_message)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse message as JSON: {e}")
                    self.logger.error(f"Raw message: {message}")
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"Error in message listener: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            self.is_connected = False
            
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        try:
            event_type = data.get('event')
            
            if event_type == 'media':
                await self._handle_audio_message(data)
            elif event_type == 'clear':
                await self._handle_clear_message(data)
            elif event_type == 'mark':
                await self._handle_mark_message(data)
            elif event_type == 'debug':
                await self._handle_debug_message(data)
            else:
                self.logger.debug(f"Unknown message type: {event_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            
    async def _handle_audio_message(self, data: Dict[str, Any]):
        """Handle audio messages from server"""
        if 'media' not in data or 'payload' not in data['media']:
            return
            
        try:
            # Decode base64 audio
            base64_data = data['media']['payload']
            audio_bytes = base64.b64decode(base64_data)
            
            # Production servers send raw 16-bit PCM at 24 kHz for mic input.
            self.is_playing = True
            self.audio_processor.play_pcm_bytes(audio_bytes, sample_rate=24000)
            self.is_playing = False
            
            self.logger.debug(f"Played audio chunk: {len(audio_bytes)} bytes")
            
        except Exception as e:
            self.logger.error(f"Error handling audio message: {e}")
            
    async def _handle_clear_message(self, data: Dict[str, Any]):
        """Handle clear messages from server"""
        self.logger.info("Received clear message")
        
    async def _handle_mark_message(self, data: Dict[str, Any]):
        """Handle mark messages from server"""
        mark_name = data.get('mark', {}).get('name', 'unknown')
        self.logger.info(f"Received mark: {mark_name}")
        
    async def _handle_debug_message(self, data: Dict[str, Any]):
        """Handle debug messages from server"""
        debug_msg = DebugMessage(
            type=data.get('type', 'unknown'),
            turn=data.get('turn', 0),
            name=data.get('name', 'unknown'),
            data=data.get('data', {})
        )
        
        self.debug_messages.append(debug_msg)
        self.current_turn = max(self.current_turn, debug_msg.turn)
        
        if self.on_debug_message:
            self.on_debug_message(debug_msg)
            
        self.logger.info(
            f"Debug message: {debug_msg.name} (turn {debug_msg.turn})"
        )
        
    def start_listening(self):
        """Start listening for microphone input"""
        if not self.is_connected:
            raise Exception("Not connected to server")
            
        self.audio_processor.start_recording()
        self.is_listening = True
        self.logger.info("Started listening")
        
    def stop_listening(self):
        """Stop listening for microphone input"""
        self.audio_processor.stop_recording()
        self.is_listening = False
        self.logger.info("Stopped listening")
        
    async def send_text_event(self, text: str):
        """Send text message to agent"""
        if not self.is_connected or not self.websocket:
            raise Exception("Not connected to server")
            
        message = {
            "event": "text",
            "text": text
        }
        
        self.logger.info(
            f"Sending text message: {json.dumps(message, indent=2)}"
        )
        await self.websocket.send(json.dumps(message))
        self.logger.info(f"Text message sent successfully: {text}")
        
    async def send_audio_chunk(self, audio_data: np.ndarray):
        """Send audio chunk to server"""
        if not self.is_connected or not self.websocket:
            return
            
        try:
            # Encode audio to μ-law
            mu_law_data = self.audio_processor.mu_law_encode(audio_data)
            
            # Encode to base64
            base64_data = base64.b64encode(mu_law_data).decode('utf-8')
            
            # Send via WebSocket
            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": base64_data
                }
            }
            
            await self.websocket.send(json.dumps(message))
            
        except Exception as e:
            self.logger.error(f"Error sending audio chunk: {e}")
            
    def get_audio_stats(self) -> AudioStats:
        """Get current audio statistics"""
        # Get latest audio chunk
        audio_data = self.audio_processor.get_audio_chunk()
        
        if audio_data is not None:
            level = self.audio_processor.get_audio_level(audio_data)
            is_speaking = self.audio_processor.is_speaking(audio_data)
            
            self.audio_stats = AudioStats(
                level=level,
                is_speaking=is_speaking,
                is_playback=self.is_playing
            )
            
        return self.audio_stats or AudioStats(level=0.0, is_speaking=False)


class DebuggerUI:
    """User interface for the debugger"""
    
    def __init__(self, debugger: PrimVoicesDebugger):
        self.debugger = debugger
        self.console = Console()
        self.running = False
        
        # Track whether we are waiting for the agent to finish its current turn.
        # When True, the interactive prompt will not be displayed so that the
        # assistant's response appears without the prompt directly above it.
        self.awaiting_response = False
        
        # Setup callbacks
        self.debugger.on_debug_message = self._on_debug_message
        
        # Keep log noise to a minimum while the prompt is active — errors still
        # get through.
        logging.getLogger(__name__).setLevel(logging.ERROR)

    def _print_user(self, message: DebugMessage):
        """Print user text in the user color"""
        user_text = message.data.get("text", "")
        self.console.print(
            f"\n[{USER_COLOR}]You:[/{USER_COLOR}] {user_text}\n"
        )

    def _print_agent(self, message: DebugMessage):
        """Print agent text in the agent color"""
        bot_text = message.data.get("text", "")
        self.console.print(
            f"\n[{AGENT_COLOR}]Agent:[/{AGENT_COLOR}] {bot_text}"
        )

    def _print_generic(self, message: DebugMessage):
        """Print generic debug message"""
        self.console.print(
            f"[{message.type}] {message.name} (turn {message.turn})"
        )
        
    def _on_debug_message(self, message: DebugMessage):
        """Pretty-print incoming debug messages in real time."""
        # Ensure we're on a fresh line (avoids printing in the middle of the prompt)

        if message.type == "input" and message.name == "text":
            self._print_user(message)
        elif message.type == "output" and message.name == "text_to_speech":
            self._print_agent(message)
        else:
            # Fallback generic display
            self._print_generic(message)

        # After a turn ends, re-display the prompt headline so the next Prompt.ask
        # appears on a new line without the user pressing Enter again.
        if message.name == "turn_end":
            # The agent finished its turn; allow the next user command.
            self.awaiting_response = False
        
    def display_status(self):
        """Display current status"""
        status_table = Table(
            show_header=False, 
            show_lines=False, 
            box=None, 
            pad_edge=False
        )
        
        status_table.add_row(
            f"[{TITLE_STYLE}]Connected[/{TITLE_STYLE}]", 
            "✅" if self.debugger.is_connected else "❌"
        )
        status_table.add_row(
            f"[{TITLE_STYLE}]Listening[/{TITLE_STYLE}]", 
            "🎤" if self.debugger.is_listening else "🔇"
        )
        status_table.add_row(
            f"[{TITLE_STYLE}]Playing[/{TITLE_STYLE}]", 
            "🔊" if self.debugger.is_playing else "🔇"
        )
        status_table.add_row(
            f"[{TITLE_STYLE}]Current Turn[/{TITLE_STYLE}]", 
            str(self.debugger.current_turn)
        )
        status_table.add_row(
            f"[{TITLE_STYLE}]Messages[/{TITLE_STYLE}]", 
            str(len(self.debugger.debug_messages))
        )
        
        if self.debugger.audio_stats:
            status_table.add_row(
                f"[{TITLE_STYLE}]Audio Level[/{TITLE_STYLE}]", 
                f"{self.debugger.audio_stats.level:.3f}"
            )
            status_table.add_row(
                f"[{TITLE_STYLE}]Speaking[/{TITLE_STYLE}]", 
                "✅" if self.debugger.audio_stats.is_speaking else "❌"
            )
            
        self.console.print(status_table)
        
    def display_messages(self, limit: int = 10):
        """Display recent debug messages"""
        if not self.debugger.debug_messages:
            print_info("No debug messages yet")
            return
            
        messages_table = Table(
            "ID", "Turn", "Type", "Name", "Data",
            show_header=True, header_style=TITLE_STYLE
        )
        
        recent_messages = self.debugger.debug_messages[-limit:]
        
        for i, msg in enumerate(recent_messages):
            data_str = (
                json.dumps(msg.data, indent=2)[:100] + "..." 
                if len(json.dumps(msg.data)) > 100 
                else json.dumps(msg.data)
            )
            messages_table.add_row(
                f"[{ID_STYLE}]{i}[/{ID_STYLE}]",
                str(msg.turn),
                f"[{USER_COLOR if msg.type == 'input' else AGENT_COLOR}]"
                f"{msg.type}[/{USER_COLOR if msg.type == 'input' else AGENT_COLOR}]",
                msg.name,
                data_str
            )
            
        self.console.print(messages_table)
    
    def display_debug(self, message_index: str):
        """Display debug information"""
        msg_index = int(message_index)
        if msg_index >= len(self.debugger.debug_messages):
            print_error(f"No message with ID {msg_index}.")
            return
        
        msg = self.debugger.debug_messages[msg_index]
        data_str = json.dumps(msg.data, indent=2)
        table = Table(
            show_header=False, 
            show_lines=False, 
            box=None, 
            pad_edge=False
        )
        table.add_row(
            f"[{TITLE_STYLE}]Message Turn[/{TITLE_STYLE}]", 
            f"{msg.turn}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Message Type[/{TITLE_STYLE}]", 
            f"{msg.type}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Message Name[/{TITLE_STYLE}]", 
            f"{msg.name}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Message Data[/{TITLE_STYLE}]", 
            f"{data_str}"
        )
        self.console.print(table)
        
        
    def display_help(self):
        """Display help information"""
        help_text = f"""
[{TITLE_STYLE}]PrimVoices Debugger Commands:[/{TITLE_STYLE}]

[{TITLE_STYLE}]Audio & Messaging:[/{TITLE_STYLE}]
  send <text> - Send text message to agent


[{TITLE_STYLE}]Monitoring:[/{TITLE_STYLE}]
  status      - Show connection status
  messages    - Show recent debug messages
  debug <id>  - Show detailed info for message ID
  clear       - Clear message history
  config      - Show current agent, environment, and function

[{TITLE_STYLE}]Other:[/{TITLE_STYLE}]
  help        - Show this help
  quit/exit   - Exit debugger

[{TITLE_STYLE}]Notes:[/{TITLE_STYLE}]
• Type any text (not a command) to send it as a message
• The debugger auto-connects on startup
• Use Ctrl+C to interrupt, then 'quit' to exit properly
        """
        
        self.console.print(Panel(help_text, title="Help"))
        
    async def run_interactive(self):
        """Run interactive command-line interface"""
        self.running = True
        
        print_success("PrimVoices Debugger")
        print_info("Type 'help' for available commands, or 'quit' to exit")

        # Automatically connect to the agent on startup so the user does not have
        # to type the `connect` command manually.
        try:
            with Progress(
                SpinnerColumn(), 
                TextColumn("[progress.description]{task.description}")
            ) as progress:
                task = progress.add_task("Connecting...", total=None)
                await self.debugger.connect()
                progress.update(task, description="Connected!")

            # Send a quick ping to verify the websocket is healthy
            try:
                await self.debugger.websocket.send(
                    json.dumps({"event": "ping"})
                )
            except Exception as e:
                print_error(
                    f"Failed to send ping: {e}. Please check your connection "
                    f"and restart the debugger."
                )

            # We expect the agent to respond shortly; hold prompt until then.
            self.awaiting_response = True
        except Exception as e:
            print_error(
                f"Auto-connect failed: {e}. Please check your connection "
                f"and restart the debugger."
            )

        while self.running:
            try:
                # Do not prompt the user while we are waiting for the agent to
                # finish its turn (i.e. until a `turn_end` debug message is
                # received).  This prevents a prompt from appearing right
                # before the assistant's response.
                if self.awaiting_response:
                    await asyncio.sleep(0.1)
                    continue

                # Prompt.ask blocks the event loop. Run it in a thread so that
                # background tasks (WebSocket listener, etc.) keep running and
                # messages appear as soon as they arrive.
                command = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.console.input(
                        f"\n[{USER_STYLE}]debugger>[/{USER_STYLE}] "
                    )
                )
                
                if not command.strip():
                    continue
                    
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd not in SUPPORTED_COMMANDS:
                    # Not a command, just a text message
                    if not self.debugger.is_connected:
                        print_error("Not connected. Please restart the debugger.")
                    else:
                        # Pause prompt until agent responds to this text
                        self.awaiting_response = True
                        await self.debugger.send_text_event(command)
                        print_success(f"Sent: {command}")
                    continue

                if cmd == 'quit' or cmd == 'exit' or cmd == 'q' or cmd == 'x':
                    # Disconnect gracefully before exiting
                    if self.debugger.is_connected:
                        await self.debugger.disconnect()
                    self.running = False
                    break

                elif cmd == 'send':
                    if not self.debugger.is_connected:
                        print_error("Not connected. Please restart the debugger.")
                    else:
                        # Pause prompt until agent responds to this text
                        text = " ".join(args)
                        self.awaiting_response = True
                        await self.debugger.send_text_event(text)
                        print_success(f"Sent: {text}")
                    continue
                    
                elif cmd == 'help':
                    self.display_help()
                    
                elif cmd == 'status':
                    self.display_status()
                    
                elif cmd == 'listen':
                    if not self.debugger.is_connected:
                        print_error("Not connected. Please restart the debugger.")
                    else:
                        self.debugger.start_listening()
                        print_success("Started listening")
                        
                elif cmd == 'stop':
                    self.debugger.stop_listening()
                    print_warning("Stopped listening")
                        
                elif cmd == 'messages':
                    self.display_messages()
                    
                elif cmd == 'stats':
                    stats = self.debugger.get_audio_stats()
                    if stats:
                        print_info(f"Audio Level: {stats.level:.3f}")
                        print_info(f"Speaking: {'Yes' if stats.is_speaking else 'No'}")
                        print_info(f"Playback: {'Yes' if stats.is_playback else 'No'}")
                    else:
                        print_info("No audio stats available")
                        
                elif cmd == 'clear':
                    self.debugger.debug_messages.clear()
                    print_warning("Message history cleared")
                        
                elif cmd == 'config':
                    config_table = Table(
                        show_header=False, 
                        show_lines=False, 
                        box=None, 
                        pad_edge=False
                    )
                    config_table.add_row(
                        f"[{TITLE_STYLE}]Agent[/{TITLE_STYLE}]", 
                        f"{self.debugger.config.agent['name']}"
                    )
                    config_table.add_row(
                        f"[{TITLE_STYLE}]Agent ID[/{TITLE_STYLE}]", 
                        f"[{ID_STYLE}]{self.debugger.config.agent['id']}[/{ID_STYLE}]"
                    )
                    config_table.add_row(
                        f"[{TITLE_STYLE}]Environment[/{TITLE_STYLE}]", 
                        f"{self.debugger.config.environment['name']}"
                    )
                    config_table.add_row(
                        f"[{TITLE_STYLE}]Environment ID[/{TITLE_STYLE}]", 
                        f"[{ID_STYLE}]{self.debugger.config.environment['id']}[/{ID_STYLE}]"
                    )
                    config_table.add_row(
                        f"[{TITLE_STYLE}]Function[/{TITLE_STYLE}]", 
                        f"{self.debugger.config.function['name']}"
                    )
                    config_table.add_row(
                        f"[{TITLE_STYLE}]Function ID[/{TITLE_STYLE}]", 
                        f"[{ID_STYLE}]{self.debugger.config.function['id']}[/{ID_STYLE}]"
                    )
                    self.console.print(config_table)

                elif cmd == 'debug':
                    self.display_debug(args[0])
                    
                else:
                    print_error(f"Unknown command: {cmd}")
                    
            except KeyboardInterrupt:
                print_warning("Use 'quit' to exit")
            except Exception as e:
                print_error(e)
                
        # Cleanup
        await self.debugger.disconnect()
        print_success("Goodbye!")

async def run_debugger(agent: dict, environment: dict, function: dict):
    """Main entry point"""
    console = Console()
    
    try:
        # Load configuration
        config = WebSocketConfig(
            agent=agent,
            api_url=API_BASE_URL,
            environment=environment,
            function=function,
        )
        
        # Create debugger
        debugger = PrimVoicesDebugger(config)
        
        # Create UI
        ui = DebuggerUI(debugger)
        
        # Run interactive interface
        await ui.run_interactive()
        
    except Exception as e:
        print_error(e)
        sys.exit(1)
