from xai_sdk.chat import user


class LLMAgent:
    def __init__(self, agent_id: str, role: str, initial_prompt: str, session):
        self.agent_id = agent_id
        self.role = role
        self.initial_prompt = initial_prompt
        self.session = session
        self.chat_history = [{"role": "system", "content": initial_prompt}]

        # Initialize the session with the system prompt
        # self.session.append(user(f"Agent {self.agent_id} ({self.role}) is thinking..."))
        # response = self.session.sample()
        # self.session.append(response)

    def to_log(self):
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "initial_prompt": self.initial_prompt,
            "chat_history": self.session,
        }

    def respond(self, message: str) -> str:
        """
        Generates a response based on the provided message.
        Args:
            message (str): The message to respond to.
        Returns:
            str: The agent's response.
        """
        prompt = f"{self.agent_id} ({self.role}): {message}"
        self.session.append(user(prompt))

        response = self.session.sample()
        self.session.append(response)

        return response
