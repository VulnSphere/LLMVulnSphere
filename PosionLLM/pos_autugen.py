from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

OPENAI_API_KEY = 'sk-ef817b356c5b428c913d990c08654e23'
OPENAI_API_BASE = 'http://aisec.today:22234/v1/'
MODEL = "gpt-4o"

config_list = [{'model': MODEL, 'api_key': OPENAI_API_KEY, 'base_url': OPENAI_API_BASE}]


assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding", "use_docker": False})

goal = input("Input your task> ")
try:
  user_proxy.initiate_chat(assistant, message=goal)
except Exception as e:
  print(e)
