from autogen import AssistantAgent, UserProxyAgent, LLMConfig, ConversableAgent
from dotenv import load_dotenv

load_dotenv()

llm_config = LLMConfig.from_json(path="OAI_CONFIG_LIST")


with llm_config:
  # Create an AI agent
  assistant = ConversableAgent(
      name="assistant",
      system_message="You are an assistant that responds concisely.",
  )

  # Create another AI agent
  fact_checker = ConversableAgent(
      name="fact_checker",
      system_message="You are a fact-checking assistant.",
  )

# Start the conversation
assistant.initiate_chat(
    recipient=fact_checker,
    message="What is AG2?",
    max_turns=2
)