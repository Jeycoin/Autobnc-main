from typing import Any, Callable, TYPE_CHECKING, Coroutine,Union
from autogen import AssistantAgent, UserProxyAgent
import autogen
if TYPE_CHECKING:
  from autobnc.AutoBnc import AutoBnc

class FunctionBase:
  name: str
  description: str

  def build(self, autobnc: 'AutoBnc') -> Union[Callable[..., Any] , Callable[..., Coroutine[Any, Any, Any]]]:
    raise NotImplementedError

  def register(self,autobnc: 'AutoBnc', caller: AssistantAgent, user_proxy: UserProxyAgent)->None:
    func = self.build(autobnc)
    autogen.agentchat.register_function(
      func,
      caller=caller,
      executor=user_proxy,
      description=self.description,
    )