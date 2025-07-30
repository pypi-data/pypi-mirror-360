from .schema.tool import ToolList
import os


from agno.agent import Agent
from agno.models.openai import OpenAILike
from scmcp_shared.kb import load_kb

model = OpenAILike(
    id=os.getenv("MODEL"),
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)


def rag_agent(task, software=None):
    knowledge_base = load_kb(software=software)
    agent = Agent(
        model=model,
        knowledge=knowledge_base,
        show_tool_calls=True,
        search_knowledge=True,
    )
    query = f"""
    <task>
    {task}
    </task>
    查询知识库，给出一个用于解决任务的代码示例。返回结果格式为：
    <code_example>
        [code_example]
    </code_example>
    """
    rep = agent.run(query)
    return rep.content


def select_tool(query):
    agent = Agent(
        model=model,
        response_model=ToolList,
        use_json_mode=True,
        instructions="""
        you are a bioinformatician, you are given a task and a list of tools, you need to select the most directly relevant tools to use to solve the task
        """,
    )
    rep = agent.run(query)
    return rep.content
