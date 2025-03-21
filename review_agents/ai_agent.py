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
        system_message="You are an expert code reviewer. Review the provided code line by line. Give concise feedback per line, including suggestions for improvement.",
        llm_config=llm_config
    )

    return reviewer
