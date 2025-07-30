# reicore_sdk/sdk.py
import requests

class ReiCoreSdk:
    """
    Rei Agent SDK for interacting with the Rei Agent API.
    """

    class Chat: 
        def __init__(self, parent):
            self.parent = parent

        def completion(self, payload: dict):
            """
            Sends a message to the Rei Agent and receives a chat completion.

            :param payload: The chat completion payload to send.
            :return: A dictionary containing the chat completion response.
            """
            url = f"{self.parent.base_url}/agents/chat-completion"
            headers = {"Authorization": f"Bearer {self.parent.agent_key}"}
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error making chat completion request: {str(e)}")
        
    def __init__(self, agent_key: str):
        """
        Initializes the ReiSdk with an API key.

        :param agent_key: The API key for authentication.
        """
        self.agent_key = agent_key
        self.base_url = "https://prod.reinetwork.ai/rei"  # Replace with actual API URL
        self.chat = self.Chat(self)

    def get_agent(self):
        """
        Retrieves details about the Rei Agent.

        :return: A dictionary containing agent details.
        """
        url = f"{self.base_url}/agents"
        headers = {"Authorization": f"Bearer {self.agent_key}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error retrieving agent details: {str(e)}")

