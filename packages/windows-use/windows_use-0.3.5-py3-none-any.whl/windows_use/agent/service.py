from windows_use.agent.tools.service import click_tool, type_tool, launch_tool, shell_tool, clipboard_tool, done_tool, shortcut_tool, scroll_tool, drag_tool, move_tool, key_tool, wait_tool, scrape_tool, switch_tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from windows_use.agent.views import AgentState, AgentStep, AgentResult
from windows_use.agent.utils import extract_agent_data, image_message
from langchain_core.language_models.chat_models import BaseChatModel
from windows_use.agent.registry.views import ToolResult
from windows_use.agent.registry.service import Registry
from windows_use.agent.prompt.service import Prompt
from live_inspect.watch_cursor import WatchCursor
from langchain_core.tools import BaseTool
from windows_use.desktop import Desktop
from rich.markdown import Markdown
from rich.console import Console
from termcolor import colored
from textwrap import shorten
from typing import Literal
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Agent:
    '''
    Windows Use

    An agent that can interact with GUI elements on Windows

    Args:
        instructions (list[str], optional): Instructions for the agent. Defaults to [].
        browser (Literal['edge', 'chrome', 'firefox'], optional): Browser the agent should use (Make sure this browser is installed). Defaults to 'edge'.
        additional_tools (list[BaseTool], optional): Additional tools for the agent. Defaults to [].
        llm (BaseChatModel): Language model for the agent. Defaults to None.
        consecutive_failures (int, optional): Maximum number of consecutive failures for the agent. Defaults to 3.
        max_steps (int, optional): Maximum number of steps for the agent. Defaults to 100.
        use_vision (bool, optional): Whether to use vision for the agent. Defaults to False.
    
    Returns:
        Agent
    '''
    def __init__(self,instructions:list[str]=[],additional_tools:list[BaseTool]=[],browser:Literal['edge','chrome','firefox']='edge', llm: BaseChatModel=None,consecutive_failures:int=3,max_steps:int=100,use_vision:bool=False):
        self.name='Windows Use'
        self.description='An agent that can interact with GUI elements on Windows' 
        self.registry = Registry([
            click_tool,type_tool, launch_tool, shell_tool, clipboard_tool,
            done_tool, shortcut_tool, scroll_tool, drag_tool, move_tool,
            key_tool, wait_tool, scrape_tool, switch_tool
        ] + additional_tools)
        self.instructions=instructions
        self.browser=browser
        self.consecutive_failures=consecutive_failures
        self.desktop = Desktop()
        self.agent_state = AgentState()
        self.watch_cursor = WatchCursor()
        self.agent_step = AgentStep(max_steps=max_steps)
        self.use_vision=use_vision
        self.llm = llm

    def reason(self):
        message=self.llm.invoke(self.agent_state.messages)
        agent_data = extract_agent_data(message=message)
        self.agent_state.update_state(agent_data=agent_data, messages=[message])
        logger.info(colored(f"💭: Thought: {agent_data.thought}",color='light_magenta',attrs=['bold']))

    def action(self):
        self.agent_state.messages.pop() # Remove the last message to avoid duplication
        last_message = self.agent_state.messages[-1]
        if isinstance(last_message, HumanMessage):
            self.agent_state.messages[-1]=HumanMessage(content=Prompt.previous_observation_prompt(self.agent_state.previous_observation))
        ai_message = AIMessage(content=Prompt.action_prompt(agent_data=self.agent_state.agent_data))
        name = self.agent_state.agent_data.action.name
        params = self.agent_state.agent_data.action.params
        logger.info(colored(f"🔧: Action: {name}({', '.join(f'{k}={v}' for k, v in params.items())})",color='blue',attrs=['bold']))
        tool_result = self.registry.execute(tool_name=name, desktop=self.desktop, **params)
        observation=tool_result.content if tool_result.is_success else tool_result.error
        logger.info(colored(f"🔭: Observation: {shorten(observation,500,placeholder='...')}",color='green',attrs=['bold']))
        desktop_state = self.desktop.get_state(use_vision=self.use_vision)
        prompt=Prompt.observation_prompt(query=self.agent_state.query,agent_step=self.agent_step, tool_result=tool_result, desktop_state=desktop_state)
        human_message=image_message(prompt=prompt,image=desktop_state.screenshot) if self.use_vision and desktop_state.screenshot else HumanMessage(content=prompt)
        self.agent_state.update_state(agent_data=None,observation=observation,messages=[ai_message, human_message])

    def answer(self):
        self.agent_state.messages.pop()  # Remove the last message to avoid duplication
        last_message = self.agent_state.messages[-1]
        if isinstance(last_message, HumanMessage):
            self.agent_state.messages[-1]=HumanMessage(content=Prompt.previous_observation_prompt(self.agent_state.previous_observation))
        name = self.agent_state.agent_data.action.name
        params = self.agent_state.agent_data.action.params
        tool_result = self.registry.execute(tool_name=name, desktop=None, **params)
        ai_message = AIMessage(content=Prompt.answer_prompt(agent_data=self.agent_state.agent_data, tool_result=tool_result))
        logger.info(colored(f"📜: Final Answer: {tool_result.content}",color='cyan',attrs=['bold']))
        self.agent_state.update_state(agent_data=None,observation=None,result=tool_result.content,messages=[ai_message])

    def invoke(self,query: str):
        max_steps = self.agent_step.max_steps
        tools_prompt = self.registry.get_tools_prompt()
        desktop_state = self.desktop.get_state(use_vision=self.use_vision)
        prompt=Prompt.observation_prompt(query=query,agent_step=self.agent_step, tool_result=ToolResult(is_success=True, content="No Action"), desktop_state=desktop_state)
        system_message=SystemMessage(content=Prompt.system_prompt(browser=self.browser,instructions=self.instructions,tools_prompt=tools_prompt,max_steps=max_steps))
        human_message=image_message(prompt=prompt,image=desktop_state.screenshot) if self.use_vision and desktop_state.screenshot else HumanMessage(content=prompt)
        messages=[system_message,human_message]
        self.agent_state.init_state(query=query,messages=messages)
        try:
            self.watch_cursor.start()
            while True:
                if self.agent_step.is_last_step():
                    self.watch_cursor.stop()
                    logger.info("Reached maximum number of steps, stopping execution.")
                    return AgentResult(is_done=False, content=None, error="Maximum steps reached.")
                elif self.agent_state.consecutive_failures==self.consecutive_failures:
                    self.watch_cursor.stop()
                    logger.info("Consecutive failures exceeded limit, stopping execution.")
                    return AgentResult(is_done=False, content=None, error=self.agent_state.error)
                try:
                    self.reason()
                except Exception as err:
                    self.agent_state.consecutive_failures += 1
                    self.agent_state.error = str(err)
                    continue
                if self.agent_state.is_done():
                    self.answer()
                    self.watch_cursor.stop()
                    return AgentResult(is_done=True, content=self.agent_state.result, error=None)
                else:
                    self.action()
                    self.agent_step.increment_step()
        except Exception as error:
            return AgentResult(is_done=False, content=None, error=str(error))
        finally:
            self.watch_cursor.stop()

    def print_response(self,query: str):
        console=Console()
        response=self.invoke(query)
        console.print(Markdown(response.content or response.error))   