from autogen import AssistantAgent, UserProxyAgent, LLMConfig
from dotenv import load_dotenv

load_dotenv()

llm_config = LLMConfig.from_json(path="OAI_CONFIG_LIST")


with llm_config:
    assistant = AssistantAgent("assistant")
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})
user_proxy.initiate_chat(assistant, message="Plot a chart of NVDA and TESLA stock price change YTD.")