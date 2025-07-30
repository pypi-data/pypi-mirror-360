from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall
import uuid
import json
import logging
from typing import Optional, Dict, Any, List

class P2PNode(Protocol):
    def __init__(self, factory, is_initiator: bool = False):
        self.factory = factory
        self.buffer = ""  # Buffer to hold partial messages
        self.periodic_task: Optional[LoopingCall] = None  # Task to send periodic messages
        self.heartbeat_task: Optional[LoopingCall] = None  # Task to send heartbeat messages
        self.is_initiator = is_initiator  # Track if this node initiated the connection
        self.remote_id: Optional[str] = None  # ID of the remote peer
        self.logger = logging.getLogger(__name__)  # Initialize logger

        self.user_defined_msg_handlers=dict()

    def register_message_handler(self, message_type, func ):
        self.user_defined_msg_handlers[message_type] = func

    def connectionMade(self):
        """Handle new connection."""
        peer = self.transport.getPeer()
        host = self.transport.getHost()

        peer_address = f"{peer.host}:{peer.port}"
        host_address = f"{host.host}:{host.port}"

        self.logger.info(f"Connected to peer at {peer_address} from {host_address}")

        self.send_welcome_info_to_peer()

    def dataReceived(self, data: bytes):
        """Handle incoming data."""
        try:
            decoded_data = data.decode("utf-8")
        except UnicodeDecodeError as e:
            self.logger.error(f"Error decoding data: {e}")
            return

        self.buffer += decoded_data
        lines = self.buffer.split("\n")
        self.buffer = lines.pop()  # Save incomplete data

        for line in lines:  
            self.logger.info("Incoming message: %s",str(line))
            if not line.strip():
                continue  # Skip empty lines
            try:
                parsed_message = json.loads(line)
                self.process_message(parsed_message)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding message: {e}")

    def send_message(self, message: Dict[str, Any], peer_transport: Optional[Any] = None):
        """Send a message to all connected peers or a specific peer."""
        message_id = message.get("message_id")
        if message_id:
            self.factory.seen_messages.add(message_id)
        else:
            self.logger.warning("Message without message_id")

        serialized_message = json.dumps(message) + "\n"
        data = serialized_message.encode("utf-8")

        if peer_transport:
            peer_transport.write(data)
        else:
            for transport in self.get_all_transports():
                transport.write(data)

    def get_all_transports(self) -> List[Any]:
        """Retrieve all connected transports."""
        transports = []
        for peer_info in self.factory.all_peers.get_all_peers_values():
            for location in ["remote", "local"]:
                location_info = peer_info.get(location)
                if location_info and "transport" in location_info:
                    transports.append(location_info["transport"])
        return transports

    def process_message(self, message: Dict[str, Any]):
        """Handle and forward broadcast messages."""

        message_id = message.get("message_id")
        
        if not message_id:
            self.logger.warning("Received message without message_id")
            return

        if message_id in self.factory.seen_messages:
            return  # Deduplicate messages

        self.factory.seen_messages.add(message_id)

        message_type = message.get("message_type")

        if hasattr(self, "pong_message") and hasattr(self, "transport"):
            pong_message = self.pong_message()
            transport = self.transport
        else:
            pong_message = None
            transport = None

        match message_type:
            case "broadcast_peer_list_add":
                self.update_peer_list(message)
                self.send_message(message)
            case "peer_list_add" | "peer_list_update":
                self.update_peer_list(message)
            case "peer_info":
                self.process_peer_info(message)
            case "broadcast_remove_peer":
                self.remove_peer(message)
                self.send_message(message)
            case "broadcast_message":
                self.send_message(message)
            case "ping":
                self.logger.info(f"{message.get('content', '')}")
                if pong_message and transport:
                    self.send_message(pong_message, peer_transport=transport)
            case "pong":
                self.logger.info(f"{message.get('content', '')}")
            case _:
                if message_type in self.user_defined_msg_handlers:
                    func = self.user_defined_msg_handlers[message_type]
                    func(message.get("peer_id",""),message.get("message_body","")) 
                else:
                    print("registered handlers: " % self.user_defined_msg_handlers)
                    self.logger.warning(f"Unknown message type received: {message_type}")

    def process_peer_info(self, message: Dict[str, Any]):
        """Update peer info upon receiving process_peer_info message."""
 
        peer_id = message.get("peer_id")
        peer_universe = message.get("peer_universe")
        peer_type = message.get("peer_type")

        self.logger.info("Received peer_info: {},{},{}".format(peer_id,peer_universe,peer_type))
        if not peer_id:
            self.logger.error("Received process_peer_info without id")
            return

        if not self.factory.all_peers.get_peer_info(peer_id):
            self.logger.info(f"Adding peer {peer_id}")
            self.factory.all_peers.add_peer(peer_id)
        elif self.factory.all_peers.get_peer_info(peer_id)["public"]:
            self.logger.info(f"Peer {peer_id} found with connection details.")
        else:
            self.logger.info(f"Peer {peer_id} found without connection details.")
    
        peer = self.transport.getPeer()

        if self.is_initiator:
            self.factory.all_peers.set_local_info(peer_id, peer.host, peer.port, self.transport)
        else:
            self.factory.all_peers.set_remote_info(peer_id, peer.host, peer.port, self.transport)

        self.remote_id = peer_id
        #Update factory peer count
        self.factory.on_peer_connected()

        if self.is_initiator:
            self.logger.info(f"I ({peer_id}) am initiator. Broadcasting peer list...")
            self.broadcast_peer_list()
        else:
            if peer_type=="ra":
                self.send_peer_list(self.transport)

        #self.start_heartbeat()

    def broadcast_peer_list(self):
        """Broadcast the known peer list to all connected peers."""
        message_id = str(uuid.uuid4())
        peer_list = [
            (peer_id, subdict["public"])
            for peer_id, subdict in self.factory.all_peers.get_all_peers_items()
            if subdict["public"]
        ]
        message = {
            "message_type": "broadcast_peer_list_add",
            "message_id": message_id,
            "peers": peer_list
        }
        self.send_message(message)

    def send_peer_list(self, transport):
        message_id = str(uuid.uuid4())
        peer_list = [
            (peer_id, subdict["public"])
            for peer_id, subdict in self.factory.all_peers.get_all_peers_items()
            if subdict["public"]
        ]
        message = {
            "message_type": "peer_list_add",
            "message_id": message_id,
            "peers": peer_list
        }
        self.send_message(message, transport)

    def broadcast_remove_peer(self, peer_id: str):
        """Broadcast a message to all peers to remove a disconnected peer."""
        message_id = str(uuid.uuid4())
        message = {
            "message_type": "broadcast_remove_peer",
            "message_id": message_id,
            "peer_id": peer_id
        }
        self.send_message(message)

    def send_welcome_info_to_peer(self):
        """Send peer info to the connected peer."""
        message_id = str(uuid.uuid4())
        message = {
            "message_type": "peer_info",
            "message_id": message_id,
            "peer_id": self.factory.id,
            "peer_universe": self.factory.universe,
            "peer_type": self.factory.type
        }
        self.send_message(message, peer_transport=self.transport)

    def update_peer_list(self, message: Dict[str, Any]):
        """Update the known peer list."""
        peers = message.get("peers", [])
        changed = False

        for peer_id, public in peers:
            if not self.factory.all_peers.get_peer_info(peer_id):
                self.logger.info("Recieved new peer public info")
                self.factory.all_peers.set_public_info(peer_id, public["host"], public["port"])
                changed = True
            elif not self.factory.all_peers.get_peer_info(peer_id)["public"]:
                self.factory.all_peers.set_public_info(peer_id, public["host"], public["port"])
                changed = True
            
            """
            if peer_id not in self.factory.all_peers:
                self.factory.all_peers[peer_id] = {
                    "public": public.copy()
                }
                changed = True
            elif "public" not in self.factory.all_peers[peer_id]:
                self.factory.all_peers[peer_id]["public"] = public.copy()
                changed = True
            """

        if changed:
            self.log_public_peer_list()

    def remove_peer(self, message: Dict[str, Any]):
        """Remove a peer from all_peers."""
        peer_id = message.get("peer_id")
        if peer_id:
            if self.factory.all_peers.remove_peer_info(peer_id):
                self.log_public_peer_list(message=f"Peer {peer_id} disconnected. Updated peer list")    
            else:
                self.logger.warning(f"Peer {peer_id} not found in peer list.")

    def pong_message(self) -> Dict[str, Any]:
        """Construct a pong message."""
        message_id = str(uuid.uuid4())
        return {
            "message_type": "pong",
            "message_id": message_id,
            "content": f"Pong from {self.factory.id}"
        }

    def start_periodic_messages(self, interval: int = 3):
        """Start sending periodic messages."""
        def periodic_message():
            message_id = str(uuid.uuid4())
            message = {
                "message_type": "broadcast_message",
                "message_id": message_id,
                "content": f"Hello from {self.factory.id}"
            }
            self.send_message(message)

        self.periodic_task = LoopingCall(periodic_message)
        self.periodic_task.start(interval)

    def start_heartbeat(self, interval: int = 10):
        """Start sending heartbeat messages to check if peers are alive."""
        def send_ping():
            message_id = str(uuid.uuid4())
            message = {
                "message_type": "ping",
                "message_id": message_id,
                "content": f"Ping from {self.factory.id}"
            }
            self.send_message(message)

        self.heartbeat_task = LoopingCall(send_ping)
        self.heartbeat_task.start(interval)

    def connectionLost(self, reason):
        """Handle lost connection."""
        if self.remote_id:
            peer_id = self.remote_id
            if self.factory.all_peers.get_peer_info(peer_id):
                if self.is_initiator:
                    self.factory.all_peers.remove_peer_info(peer_id,"local")
                    #del self.factory.all_peers[peer_id]["local"]
                else:
                    self.factory.all_peers.remove_peer_info(peer_id,"remote")
                    #del self.factory.all_peers[peer_id]["remote"]

                """
                if not (self.factory.all_peers[peer_id].get("local",False) or
                        self.factory.all_peers[peer_id].get("remote",False)):
                        del self.factory.all_peers[peer_id]
                        """
                
                if not (self.factory.all_peers.get_peer_info(peer_id)["local"] or
                        self.factory.all_peers.get_peer_info(peer_id)["remote"]):
                    self.factory.all_peers.remove_peer_info(peer_id)
                    self.log_public_peer_list(message=f"Peer {peer_id} disconnected. Updated peer list")
                    self.broadcast_remove_peer(peer_id)
            
                    # Stop periodic tasks if running
                    if self.periodic_task and self.periodic_task.running:
                        self.periodic_task.stop()
                    if self.heartbeat_task and self.heartbeat_task.running:
                        self.heartbeat_task.stop()

                #update factory peer count
                self.factory.on_peer_disconnected()

    def log_public_peer_list(self, message: str = "Peer list updated"):
        self.logger.info(
            f"\n{'-'*13}\n{message}:\n" +
            "\n".join(f"id: {pid}, host: {info['public']['host']}, port: {info['public']['port']}" 
                    for pid, info in self.factory.all_peers.get_all_peers_items() if info["public"]) +
            f"\n{'-'*13}"
        )

