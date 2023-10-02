from dataclasses import (
    dataclass,
)
import openai

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
    max_tokens: int = 1024
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    stop: str = ""
    prompt: str = ""

    def __post_init__(self) -> None:
        """
        Initializes the OpenAIAPI instance and sets the OpenAI API key.
        Raises an exception if the API token is missing.
        """
        if self.api_token is None:
            raise Exception("OpenAI API key is required")
        openai.api_key = self.api_token
        self.prompt = """ # noqa: E501
            **Task Prompt:**

            As an algorithm expert, your mission is to craft a comprehensive algorithm tutorial. Your tutorial should delve into a specific algorithmic topic of your choice, such as sorting algorithms, search algorithms, dynamic programming, graph algorithms, or any other area of expertise you possess.

            **Instructions:**

            1. **Choose Your Algorithm:** Select a unique, different algorithmic topic each time that piques your interest or falls within your domain of expertise.

            2. **Craft Your Tutorial:** Your tutorial should be structured as an HTML document, and it must encompass the following sections:

               - **Title:** Create a captivating and informative title that encapsulates the essence of your tutorial.

               - **Introduction:** Begin with a concise introduction to the chosen algorithmic topic. Explain why this algorithm is significant and relevant in the world of computer science.

               - **Overview:** Provide an overview that outlines the fundamental principles and concepts related to the algorithm. Offer a high-level understanding before diving into the specifics.

               - **In-Depth Explanation:** Break down the algorithm into its core components, and meticulously elucidate each step or concept. Utilize clear and succinct language to ensure your readers can grasp the material effortlessly.

               - **{programming_language} Code Samples:** Embed code examples written in {programming_language} to illustrate the algorithm's inner workings. Ensure your code is well-commented and easily comprehensible. Make sure that your code samples are written in {programming_language}. Don't use any other programming language.

               - **Visualizations (optional):** If applicable, consider incorporating visual aids such as diagrams or flowcharts to facilitate understanding.

               - **Complexity Analysis:** Engage in a comprehensive discussion about the time and space complexity of the algorithm. Analyze its efficiency and performance.

               - **Real-World Applications:** Explore real-world scenarios and use cases where the algorithm finds common application. Make the algorithm's practicality tangible to your readers.

               - **External Resources:** Enhance your tutorial by offering links to external resources, research papers, or supplementary reading materials for those eager to delve deeper into the subject.

               - **Conclusion:** Summarize the key takeaways from your tutorial, reaffirming the algorithm's importance and relevance.

            3. **Structural Integrity:** Ensure that your HTML page is meticulously structured with appropriate headings, well-organized paragraphs, and clean code formatting.

            4. **Hyperlink Integration:** Employ hyperlinks to seamlessly connect sections, cross-reference content, and provide quick access to external resources.

            5. **HTML Tags for Enhancement:** Utilize proper HTML tags to enhance formatting and styling. Leverage headings, lists, and code blocks to make your content visually appealing and reader-friendly.

            6. **Proofreading and Refinement:** Before finalizing your tutorial, meticulously proofread and edit it to guarantee clarity, accuracy, and comprehensiveness.

            **Note:** Challenge yourself to explore a unique algorithmic topic each day. Your tutorial should serve as an educational resource catering to both beginners and those possessing some prior knowledge of algorithms. Also, make sure that your tutorial code samples are written in {programming_language}. Don't use any other programming language.
        """

    def send_algorithm_email(self, to: str, language: str) -> None:
        """
        Sends an algorithm-related email to the specified recipient.

        Args:
            to (str): The email address of the recipient.

        This method generates an algorithm tutorial email using the OpenAI API
        and sends it to the specified recipient's email address.
        """
        from src.main import (
            code_app,
        )

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
                    "content": self.prompt.replace(
                        "{programming_language}", language
                    ),
                }
            ],
        }

        response = openai.ChatCompletion.create(**params)
        html_content = response["choices"][0]["message"]["content"]
        draft["subject"] = "Your Daily Dose of Algorithms"
        draft["to"] = [{"email": to}]
        draft["body"] = html_content
        draft["from"] = [{"email": code_app.state.nylas.account.email_address}]
        draft.send()
        code_app.state.nylas.access_token = initial_token
        openai.api_key = ""

    async def async_send_algorithm_email(self, to: str, language: str) -> None:
        """
        Asynchronously sends an algorithm-related email to the specified recipient.

        Args:
            to (str): The email address of the recipient.

        This method asynchronously generates an algorithm tutorial email using the
        OpenAI API and sends it to the specified recipient's email address.
        """

        self.send_algorithm_email(to, language)
