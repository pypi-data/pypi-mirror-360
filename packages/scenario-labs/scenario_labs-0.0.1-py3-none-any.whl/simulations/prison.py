import re
from datetime import datetime
from itertools import cycle
from pathlib import Path
from typing import Dict, List


class PrisonSimulation:
    MESSAGE_PATTERN = r"<agent_reply>(.*?)</agent_reply>"

    def __init__(
        self, simulation_name: str, agents: Dict[str, any], max_turns: int = 12
    ):
        """
        Initialize the simulation.

        Args:
            agents (dict): A dictionary mapping agent IDs to LLMAgent instances.
            max_turns (int): The number of turns to run the simulation.
        """
        self.simulation_name = simulation_name
        self.agents = agents
        self.max_turns = max_turns
        self.chat_history = []
        self.world_log = []

    def get_log(self):
        """
        Prints the chat history in a readable format and saves it to a Markdown file in ./logs,
        converting `${...}$` style messages to bold using `**...**` for better Markdown rendering.
        """
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = (
            log_dir
            / f"{self.simulation_name.lower().replace(' ', '_')}_log_{self.max_turns}_{timestamp}.md"
        )

        print(f"\n=== {self.simulation_name} Log ===\n")

        def format_message(text: str) -> str:
            return re.sub(self.MESSAGE_PATTERN, r"**\1**", text)

        for entry in self.chat_history:
            turn = entry.get("turn", "?")
            from_id = entry.get("from_id", "")
            to_id = entry.get("to_id", "N/A")
            message = format_message(entry.get("message", "").strip())
            response = (
                format_message(entry.get("response", "").strip())
                if "response" in entry
                else None
            )

            print(f"Turn {turn}")
            print(f"From: {from_id}")
            print(f"To: {to_id}")
            print(f"Message: {message}")
            if response:
                print(f"Response: {response}")
            print("-" * 40)

        with log_file.open("w") as f:
            f.write(f"# {self.simulation_name} Log\n\n")
            for entry in self.chat_history:
                turn = entry.get("turn", "?")
                from_id = entry.get("from_id", "")
                to_id = entry.get("to_id", "N/A")
                message = format_message(entry.get("message", "").strip())
                response = (
                    format_message(entry.get("response", "").strip())
                    if "response" in entry
                    else None
                )

                f.write(f"## Turn {turn}\n")
                f.write(f"- **From:** {from_id}\n")
                f.write(f"- **To:** {to_id}\n")
                f.write(f"- **Message:** {message}\n")
                if response:
                    f.write(f"- **Response:** {response}\n")
                f.write("\n---\n\n")

        print(f"\nLog written to: {log_file.resolve()}")

    def parse_agent_messages(self, text: str, from_id: str) -> List[Dict[str, str]]:
        """
        Parses messages in the format ${to_id: message}$ from the agent response.

        Args:
            text (str): The content from the agent's response.
            from_id (str): The ID of the agent sending the message.

        Returns:
            List[Dict]: A list of parsed messages with 'from_id', 'to_id', and 'message'.
        """
        responses = []
        matches = re.findall(self.MESSAGE_PATTERN, text)

        for match in matches:
            to_id, msg = match.split(":", 1)
            to_id = to_id.strip()
            msg = msg.strip()

            if to_id and msg:
                responses.append({"from_id": from_id, "to_id": to_id, "message": msg})

        return responses

    def run(self):
        """
        Runs the turn-based simulation between agents.
        """
        agent_cycle = cycle(self.agents.values())

        for turn in range(1, self.max_turns + 1):
            # TODO - Add agent randomization
            agent = next(agent_cycle)
            thinking_message = f"Agent {agent.agent_id} ({agent.role}) is thinking..."

            primary_response = agent.respond(thinking_message)
            # print(f"Turn {turn} - {agent.agent_id}: {primary_response.content}")

            self.chat_history.append(
                {
                    "turn": turn,
                    "from_id": agent.agent_id,
                    "to_id": None,
                    "message": primary_response.content,
                }
            )

            # Handle inter-agent messages
            addressed_messages = self.parse_agent_messages(
                primary_response.content, from_id=agent.agent_id
            )
            for msg in addressed_messages:
                to_agent = self.agents.get(msg["to_id"])
                if to_agent:
                    message_text = f"${{{msg['from_id']}: {msg['message']}}}$"
                    reply = to_agent.respond(message_text)

                    # print(f"{msg['from_id']} -> {msg['to_id']}: {msg['message']}")
                    # print(f"{msg['to_id']} responded: {reply.content}")

                    self.chat_history.append(
                        {
                            "turn": turn,
                            "from_id": msg["from_id"],
                            "to_id": msg["to_id"],
                            "message": msg["message"],
                            "response": reply.content,
                        }
                    )

        self.get_log()
