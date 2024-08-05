from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

OPENAI_API_KEY = 'sk-8GtKGlpT3NNTLAfZj3BX3BffKGlLNZwwT6BmhoGF1UG41ePU'
OPENAI_API_BASE = 'http://aisec.today:22234/v1/'
MODEL = "gpt-4o-mini"

config_list = [{'model': MODEL, 'api_key': OPENAI_API_KEY, 'base_url': OPENAI_API_BASE}]


assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})

goal = input("Input your task> ")
try:
  user_proxy.initiate_chat(assistant, message=goal)
except Exception as e:
  print(e)
