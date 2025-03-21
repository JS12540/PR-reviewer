from autogen import ConversableAgent, LLMConfig
import os

# Load OpenAI key from environment
api_key = os.getenv("OPENAI_API_KEY")

# LLM Configuration
llm_config = LLMConfig(
    config_list=[
        {
            "model": "gpt-4o-mini",
            "api_key": api_key
        }
    ]
)

def create_agents():
    reviewer = ConversableAgent(
        name="code_reviewer",
        system_message=(
            "You are a highly skilled code reviewer with expertise in best practices, security, and performance optimization.\n"
            "You will review code changes file by file, considering the entire file context. "
            "For each file, provide the following:\n"
            "- **Contextual Overview:** Summarize the file's purpose and its functionality.\n"
            "- **Code Changes Review:** For each change, explain how it affects the code, highlight issues or improvements, and suggest fixes if necessary.\n"
            "- **File-level Suggestions:** Suggest any potential refactoring, optimization, or best practices improvements for the entire file.\n"
            "Be concise and specific in your feedback. If the code follows best practices, acknowledge it."
        ),
        llm_config=llm_config
    )

    return reviewer
