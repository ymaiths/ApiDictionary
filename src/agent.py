from langchain_openai import ChatOpenAI


class LLM:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0)

    def __call__(self, prompt):
        return self.llm


class Agent:
    def __init__(self, name, role, tools, memory):
        self.name = name
        self.role = role
        self.tools = tools
        self.memory = memory

    def execute_task(self, task):
        pass

    def update_memory(self, new_memory):
        pass

    def get_response(self, user_input):
        pass
