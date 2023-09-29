from dataclasses import dataclass
import openai
import os
from src.config import (
    settings,
)

@dataclass
class OpenAIAPI:
    """
    A class for interacting with the OpenAI API to send algorithm-related emails.

    Attributes:
        api_token (str): The OpenAI API token.
        model (str): The language model to use (default is "gpt-3.5-turbo").
        temperature (float): The sampling temperature for text generation (default is 0).
        max_tokens (int): The maximum number of tokens in the generated response (default is 128).
        top_p (float): The nucleus sampling top-p value (default is 1).
        frequency_penalty (float): The frequency penalty for text generation (default is 0).
        presence_penalty (float): The presence penalty for text generation (default is 0.6).
        stop (str): An optional stop sequence for text generation.

    Methods:
        send_algorithm_email(to: str):
            Sends an algorithm-related email to the specified recipient.

        async_send_algorithm_email(to: str):
            Asynchronously sends an algorithm-related email to the specified recipient.

    Properties:
        _type (str):
            Returns the type of the API (always "openai").
    """

    api_token: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0
    max_tokens: int = 128
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    stop: str = None
    prompt: str = None

    def __post_init__(self):
        """
        Initializes the OpenAIAPI instance and sets the OpenAI API key.
        Raises an exception if the API token is missing.
        """
        if self.api_token is None:
            raise Exception("OpenAI API key is required")
        openai.api_key = self.api_token
        self.prompt = """
            **Task Prompt:**

            As an algorithm expert, your task is to generate a comprehensive algorithm tutorial. The tutorial should cover a specific algorithmic topic of your choice (e.g., sorting algorithms, search algorithms, dynamic programming, graph algorithms, etc.) and provide in-depth explanations, code samples in {programming_language}, and relevant external links for further reading.

            **Instructions:**

            1. Choose an algorithmic topic that you are knowledgeable about or interested in.
            2. Create a tutorial that covers the selected topic in detail.
            3. Your tutorial should be structured as an HTML page and include the following sections:

               - Title: A clear and informative title for the tutorial.
               - Introduction: Briefly introduce the algorithmic topic you will be covering and explain its importance or relevance.
               - Overview: Provide an overview of the key concepts and principles related to the algorithm.
               - Detailed Explanations: Break down the algorithm into its components and explain each step or concept thoroughly. Use clear and concise language.
               - {programming_language} Code Samples: Include {programming_language} code examples that illustrate how the algorithm works. Ensure that the code is well-commented and easy to understand.
               - Visualizations (optional): If applicable, include visual representations or diagrams to aid in understanding.
               - Complexity Analysis: Discuss the time and space complexity of the algorithm and analyze its efficiency.
               - Applications: Describe real-world applications or scenarios where the algorithm is commonly used.
               - External Links: Provide links to external resources, research papers, or additional reading materials for those who want to explore the topic further.
               - Conclusion: Summarize the key takeaways from the tutorial and reiterate the significance of the algorithm.

            4. Ensure that your HTML page is well-structured, with appropriate headings, paragraphs, and code formatting.
            5. Use hyperlinks to connect sections, references, and external links.
            6. Make use of proper HTML tags for formatting and styling, such as headings, lists, and code blocks.
            7. Proofread and edit your tutorial for clarity, accuracy, and completeness.

            **Note:** Make sure to choose a unique algorithmic topic every day. Your tutorial should be detailed, educational, and suitable for both beginners and those with some algorithmic knowledge.
        """

    def send_algorithm_email(self, to: str, language: str):
        """
        Sends an algorithm-related email to the specified recipient.

        Args:
            to (str): The email address of the recipient.

        This method generates an algorithm tutorial email using the OpenAI API
        and sends it to the specified recipient's email address.
        """
        from src.main import code_app
        initial_token = code_app.state.nylas.access_token
        openai.api_key = settings().OPENAI_API_KEY
        code_app.state.nylas.access_token = settings().NYLAS_SYSTEM_TOKEN
        draft = code_app.state.nylas.drafts.create()

        params = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt.replace("{programming_language}", language),
                }
            ],
        }

        response = openai.ChatCompletion.create(**params)
        html_content = response["choices"][0]["message"]["content"]
        draft['subject'] = "Your Daily Dose of Algorithms"
        draft['to'] = [{"email": to}]
        draft['body'] = html_content
        draft['from'] = [{'email': code_app.state.nylas.account.email_address}]
        message = draft.send()
        code_app.state.nylas.access_token = initial_token
        openai.api_key = ""

    async def async_send_algorithm_email(self, to: str, language: str):
        """
        Asynchronously sends an algorithm-related email to the specified recipient.

        Args:
            to (str): The email address of the recipient.

        This method asynchronously generates an algorithm tutorial email using the
        OpenAI API and sends it to the specified recipient's email address.
        """

        self.send_algorithm_email(to, language)
