r'''
# Xpander SDK

**Xpander Open Source SDK** empowers developers to build intelligent and reliable AI Agents capable of managing complex, multi‑step tasks across diverse systems and platforms. The SDK simplifies challenges like function calling, schema definition, graph enforcement, and prompt group management.

With first‑class support for leading LLM providers such as **OpenAI**, **Amazon Bedrock**, **Google Gemini**, **Anthropic Claude**, and **NVIDIA NIM**, the **Xpander SDK** seamlessly integrates into your existing systems.

![ai-agents-with-xpander](https://assets.xpanderai.io/xpander-sdk-readme.png)

---


## 📦 Installation

Choose your preferred package manager:

### npm

```bash
npm install xpander-sdk
```

### pip

```bash
pip install xpander-sdk
```

---


## 🚀 Getting Started

### Prerequisites

1. Sign in to [app.xpander.ai](https://app.xpander.ai) and create (or pick) an **Agent**.
2. Copy the **Agent Key** and **Agent ID** from the Agent → **Settings** page.
3. Grab the API key for your preferred LLM provider (e.g. `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.).
4. Install the SDK (see above) **and** make sure you have Node.js installed – the SDK runs a tiny Node.js runtime under the hood.

---


## 🏁 Usage Patterns

Below are the canonical patterns taken from the official documentation for working with LLMs through the Xpander SDK.

### 1. Single Query (Quick Start)

```python
from xpander_sdk import XpanderClient, LLMProvider
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

xpander_client = XpanderClient(api_key=os.getenv("XPANDER_API_KEY"))
agent          = xpander_client.agents.get(agent_id=os.getenv("XPANDER_AGENT_ID"))
openai_client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# A one‑off prompt handled by the agent + tools
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=agent.messages,  # current conversation state
    tools=agent.get_tools(llm_provider=LLMProvider.OPEN_AI),
    tool_choice="auto",
    temperature=0.0,
)

# Let the SDK execute the tool calls & keep state in sync
agent.process_llm_response(response.model_dump(), llm_provider=LLMProvider.OPEN_AI)
```

> **Tip:** `agent.process_llm_response(...)` is the easiest way to both *store* the assistant message **and** immediately run any tool calls it contains – perfect for serverless single‑turn workflows.

---


### 2. Real‑Time Event Listener (xpander‑utils)

```python
from xpander_utils.events import (
    XpanderEventListener,
    AgentExecutionResult,
    ExecutionStatus,
    AgentExecution,

)
from xpander_sdk import XpanderClient, LLMProvider
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

listener = XpanderEventListener(
    api_key=os.getenv("XPANDER_API_KEY"),
    organization_id=os.getenv("XPANDER_ORG_ID"),
    agent_id=os.getenv("XPANDER_AGENT_ID"),
)

# Optional helper clients (LLM + Agent)
openai_client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
xpander_client  = XpanderClient(api_key=os.getenv("XPANDER_API_KEY"))
agent           = xpander_client.agents.get(agent_id=os.getenv("XPANDER_AGENT_ID"))

def on_execution_request(execution_task: AgentExecution) -> AgentExecutionResult:
    """Runs each time your cloud Agent triggers an execution request."""
    # (1) Ask the LLM what to do next
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=agent.messages,
        tools=agent.get_tools(llm_provider=LLMProvider.OPEN_AI),
        tool_choice="auto",
        temperature=0.0,
    )

    # (2) Persist the assistant message *and* execute any tool calls
    agent.process_llm_response(response.model_dump(), llm_provider=LLMProvider.OPEN_AI)

    # (3) Return the final result back to the platform
    return AgentExecutionResult(
        result=execution_status.result,
        is_success=True if execution_status.status == ExecutionStatus.COMPLETED else False,
    )

# Block forever, listening for events via SSE
listener.register(on_execution_request=on_execution_request)
```

> **Why `xpander-utils`?** The `XpanderEventListener` uses a lightweight Server‑Sent Events (SSE) channel to deliver execution requests to your code with sub‑second latency—perfect for Slack, Teams, and other real‑time chat surfaces. ([pypi.org](https://pypi.org/project/xpander-utils/?utm_source=chatgpt.com))

---


### 3. Multi‑Step Tasks (Long‑running autonomous workflows)

```python
# Describe a complex objective for the agent
multi_step_task = """
Find employees of xpander.ai and their roles.
Then check their LinkedIn profiles for recent updates.
"""

agent.add_task(multi_step_task)  # automatically initialises memory

while not agent.is_finished():
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=agent.messages,
        tools=agent.get_tools(llm_provider=LLMProvider.OPEN_AI),
        tool_choice="auto",
        temperature=0.0,
    )

    agent.process_llm_response(response.model_dump(), llm_provider=LLMProvider.OPEN_AI)

# 🚀 Grab the final result once the agent marks itself as finished
execution_result = agent.retrieve_execution_result()
print(execution_result.status)  # e.g. "SUCCEEDED"
print(execution_result.result)  # your task output
```

This loop lets the LLM break the objective into sub‑steps, call tools, update memory and eventually mark the task as **finished**.

---


### 4. Complete Example – Gemini via the OpenAI‑compatible API

```python
from xpander_sdk import XpanderClient, LLMProvider
from openai import OpenAI
from dotenv import load_dotenv
from os import environ

load_dotenv()

xpander_client = XpanderClient(api_key=environ["XPANDER_API_KEY"])
gemini_client  = OpenAI(
    api_key=environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent = xpander_client.agents.get(agent_id=environ["XPANDER_AGENT_ID"])
agent.add_task("Find employees of xpander.ai.")

while not agent.is_finished():
    response = gemini_client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=agent.messages,
        tools=agent.get_tools(llm_provider=LLMProvider.GEMINI_OPEN_AI),
        tool_choice=agent.tool_choice,
        temperature=0.0,
    )

    agent.add_messages(response.model_dump())

    tool_calls = XpanderClient.extract_tool_calls(
        llm_response=response.model_dump(),
        llm_provider=LLMProvider.GEMINI_OPEN_AI,
    )

    agent.run_tools(tool_calls)

print(agent.retrieve_execution_result().result)
```

This demo showcases full multi‑step orchestration **without** writing any provider‑specific glue code.

---


### 5. Local Tools (developer‑executed)

Local tools let you register **your own** functions (Python, TS, C#, …) so the LLM can *request* them. **Important:** the SDK does **not** execute local tools for you. Your code must:

1. Register the tool schema with `agent.add_local_tools()`.
2. Inspect each LLM response with `XpanderClient.extract_tool_calls(...)`.
3. Pick out the pending local calls via `retrieve_pending_local_tool_calls(...)`.
4. Invoke the matching Python/TS function(s).
5. Feed a `ToolCallResult` back with `agent.memory.add_tool_call_results([...])`.

---


#### 5‑a. Python quick path

```python
from xpander_sdk import XpanderClient, LLMProvider, ToolCallResult
from openai import OpenAI
from local_tools import local_tools_declarations, local_tools_by_name

client = XpanderClient(api_key=XPANDER_API_KEY)
agent  = client.agents.get(agent_id=XPANDER_AGENT_ID)
openai = OpenAI(api_key=OPENAI_API_KEY)

# 1️⃣  Tell the agent about your local tools
agent.add_local_tools(local_tools_declarations)

# 2️⃣  Normal chat ‑ the LLM may now reference those tools
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=agent.messages,
    tools=agent.get_tools(llm_provider=LLMProvider.OPEN_AI),
    tool_choice="auto",
    temperature=0.0,
)

# 3️⃣  Extract *all* tool calls & isolate locals
all_calls     = XpanderClient.extract_tool_calls(response.model_dump(), llm_provider=LLMProvider.OPEN_AI)
pending_local = XpanderClient.retrieve_pending_local_tool_calls(all_calls)

# 4️⃣  Run each local call
results = []
for call in pending_local:
    fn   = local_tools_by_name[call.name]
    output_payload = fn(**call.payload)  # your function runs here
    results.append(
        ToolCallResult(
            function_name=call.name,
            tool_call_id=call.tool_call_id,
            payload=call.payload,
            status_code=200,
            result=output_payload,
            is_success=True,
            is_retryable=False,
        )
    )

# 5️⃣  Write the results back so the LLM can continue
agent.memory.add_tool_call_results(results)
```

#### 5‑b. TypeScript pattern (excerpt from SDK tests)

```python
// localTools array holds { decleration, fn }
agent.addLocalTools(localToolsDecleration);

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: agent.messages,
  tools: agent.getTools(),
  tool_choice: agent.toolChoice,
});

const toolCalls          = XpanderClient.extractToolCalls(response);
const pendingLocalCalls  = XpanderClient.retrievePendingLocalToolCalls(toolCalls);

for (const call of pendingLocalCalls) {
  const resultPayload = localToolsByName[call.name](...Object.values(call.payload));
  agent.memory.addToolCallResults([
    new ToolCallResult(
      call.name,
      call.toolCallId,
      call.payload,
      200,
      resultPayload,
      true,
      false,
    ),
  ]);
}
```

The LLM will then see the tool responses in its context and proceed to the next reasoning step. This mirrors the official test‑suite workflow.

---


## 🏆 Best Practices (Provider‑agnostic) (Provider-agnostic) (Provider‑agnostic)

1. **Create a task first** – `agent.add_task()` automatically initialises the agent’s memory and system messages.
2. **Always pass `llm_provider`** when calling `agent.get_tools()` so the SDK can return the correct schema for the target provider.
3. **Store the raw LLM response** with `agent.add_messages(...)` (or implicitly via `agent.process_llm_response`). The SDK will convert fields as required.
4. **Extract tool calls with the same provider flag** you used for `get_tools`: `XpanderClient.extract_tool_calls(llm_response, llm_provider=...)`.

Following these rules ensures your code works consistently across OpenAI, Claude, Gemini, Bedrock, and more.

---


## 📚 Further Reading

* **Official Documentation:** [https://docs.xpander.ai/userguides/overview/introduction](https://docs.xpander.ai/userguides/overview/introduction)
* **LLM SDK Guide:** [https://docs.xpander.ai/docs/01-get-started/03-llm-models](https://docs.xpander.ai/docs/01-get-started/03-llm-models)
* **API Reference:** [https://docs.xpander.ai/api-reference/SDK/getting-started](https://docs.xpander.ai/api-reference/SDK/getting-started)

---


## ⚙️ Technical Note

The library is generated with **Projen** and runs inside a tiny Node.js runtime. Ensure you have a recent **Node.js** version installed for optimal performance.

---


## 🤝 Contributing

We welcome contributions to improve the SDK. Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit improvements and bug fixes.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *


@jsii.enum(jsii_type="xpander-sdk.AgentAccessScope")
class AgentAccessScope(enum.Enum):
    PERSONAL = "PERSONAL"
    ORGANIZATIONAL = "ORGANIZATIONAL"


@jsii.enum(jsii_type="xpander-sdk.AgentDelegationEndStrategy")
class AgentDelegationEndStrategy(enum.Enum):
    RETURN_TO_START = "RETURN_TO_START"
    FINISH_WITH_LAST = "FINISH_WITH_LAST"


@jsii.enum(jsii_type="xpander-sdk.AgentDelegationType")
class AgentDelegationType(enum.Enum):
    ROUTER = "ROUTER"
    SEQUENCE = "SEQUENCE"


@jsii.enum(jsii_type="xpander-sdk.AgentGraphItemSubType")
class AgentGraphItemSubType(enum.Enum):
    SDK = "SDK"
    TASK = "TASK"
    ASSISTANT = "ASSISTANT"
    WEBHOOK = "WEBHOOK"
    OPERATION = "OPERATION"
    CUSTOM_FUNCTION = "CUSTOM_FUNCTION"
    LOCAL_TOOL = "LOCAL_TOOL"


@jsii.enum(jsii_type="xpander-sdk.AgentGraphItemType")
class AgentGraphItemType(enum.Enum):
    SOURCE_NODE = "SOURCE_NODE"
    AGENT = "AGENT"
    TOOL = "TOOL"
    HUMAN_IN_THE_LOOP = "HUMAN_IN_THE_LOOP"
    STORAGE = "STORAGE"
    CODING_AGENT = "CODING_AGENT"
    MCP = "MCP"


@jsii.enum(jsii_type="xpander-sdk.AgentStatus")
class AgentStatus(enum.Enum):
    '''Enum representing the possible statuses of an agent.'''

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@jsii.enum(jsii_type="xpander-sdk.AgentType")
class AgentType(enum.Enum):
    REGULAR = "REGULAR"
    MANAGER = "MANAGER"


class Agents(metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Agents"):
    '''Manages a collection of Agent instances in xpanderAI, providing methods to list, retrieve, and initialize agents, including custom agents.'''

    def __init__(self, configuration: "Configuration") -> None:
        '''Constructs an instance of the Agents manager.

        :param configuration: - Configuration settings for managing agents.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56c927c42c835c774c6f5f1f6f97fed3b3214baccc5c46df58f7f5cf97262992)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
        jsii.create(self.__class__, self, [configuration])

    @jsii.member(jsii_name="create")
    def create(
        self,
        name: builtins.str,
        type: typing.Optional[AgentType] = None,
    ) -> "Agent":
        '''
        :param name: - The name of the agent to be created.
        :param type: - The type of the agent, defaults to Regular.

        :return: The created agent's details.

        :description: Creates a new agent with the given name and type.
        :function: create
        :memberof: xpanderAI
        :throws: {Error} If the creation process fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76702171336bf6b0ea472737a1f7d3c35de102f261244c52f4175ac7a6799b14)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        return typing.cast("Agent", jsii.invoke(self, "create", [name, type]))

    @jsii.member(jsii_name="get")
    def get(
        self,
        agent_id: builtins.str,
        version: typing.Optional[jsii.Number] = None,
    ) -> "Agent":
        '''Retrieves a specific agent by its ID and initializes it.

        :param agent_id: - The unique identifier of the agent to retrieve.
        :param version: -

        :return: The requested Agent instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb382a0499d6ff9252ba35bb8f4c90a05697129cfe9cad98a7f8a1a14da8e1d4)
            check_type(argname="argument agent_id", value=agent_id, expected_type=type_hints["agent_id"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        return typing.cast("Agent", jsii.invoke(self, "get", [agent_id, version]))

    @jsii.member(jsii_name="list")
    def list(self) -> typing.List["UnloadedAgent"]:
        '''Retrieves the list of agents from the API and populates the local agents list.

        :return: An array of Agent instances.
        '''
        return typing.cast(typing.List["UnloadedAgent"], jsii.invoke(self, "list", []))

    @builtins.property
    @jsii.member(jsii_name="agentsList")
    def agents_list(self) -> typing.List["UnloadedAgent"]:
        '''Collection of Agent instances managed by this class.'''
        return typing.cast(typing.List["UnloadedAgent"], jsii.get(self, "agentsList"))

    @agents_list.setter
    def agents_list(self, value: typing.List["UnloadedAgent"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f37932ab42616ef0215f3190c6c4bfa79237ec478d6c77803ea5cc9260af1f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentsList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> "Configuration":
        '''- Configuration settings for managing agents.'''
        return typing.cast("Configuration", jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: "Configuration") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec4b41eaf57993f4b49ed6bc9995e9ed9fa2685fb355f0d948717f7ea7e34c2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuration", value) # pyright: ignore[reportArgumentType]


class Base(metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Base"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromObject")
    @builtins.classmethod
    def from_object(cls, data: typing.Any) -> "Base":
        '''
        :param data: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dab3da5f8c0475ccab1873969e148ad9dcbdb0ddf88c9ecc6b02b751238b6e5)
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
        return typing.cast("Base", jsii.sinvoke(cls, "fromObject", [data]))

    @jsii.member(jsii_name="from")
    def from_(self, data: typing.Mapping[typing.Any, typing.Any]) -> "Base":
        '''
        :param data: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d4d603584cc9880629c407e84565dc862d0614d798748f7556e51d6023943cb)
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
        return typing.cast("Base", jsii.invoke(self, "from", [data]))

    @jsii.member(jsii_name="toDict")
    def to_dict(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "toDict", []))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "toJson", []))


class Configuration(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.Configuration",
):
    '''Manages the configuration settings for the xpanderAI client.

    This class encapsulates settings such as the API key, base URL,
    metrics reporting, and optional organization-specific parameters.
    '''

    def __init__(self, __0: "IConfiguration") -> None:
        '''Constructs a new Configuration instance.

        :param __0: - The API key for xpanderAI.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dafae5b4445df1b4c673783f144d770b151e831e63bc8be999b4708f966d5caa)
            check_type(argname="argument __0", value=__0, expected_type=type_hints["__0"])
        jsii.create(self.__class__, self, [__0])

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''Constructs the full API endpoint URL.

        The URL combines the base URL with the optional organization ID if provided.

        :return: The constructed API endpoint URL.
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        '''API key for authenticating requests to xpanderAI.'''
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135b56998170832cdd7296e91cdddd9c57d7b17d36e505bee4468b800785e5a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        '''Base URL for the xpanderAI API requests.'''
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6025924c03e9981cc1b85f95320de6d369f9970a79f6ee17298111769cddfa5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> typing.Optional[builtins.str]:
        '''Optional organization ID for scoped API requests.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20369269e83a8faf9b0e5c03d8b299c924f1479bf7cf5b8c1b3b9f8bb93c406f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]


class Execution(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Execution"):
    '''Represents an execution of an agent in xpanderAI, including its input, status, memory, and other related details.'''

    def __init__(
        self,
        id: builtins.str,
        agent_id: builtins.str,
        organization_id: builtins.str,
        input: "IExecutionInput",
        status: "ExecutionStatus",
        last_executed_node_id: typing.Optional[builtins.str] = None,
        memory_thread_id: typing.Optional[builtins.str] = None,
        parent_execution: typing.Optional[builtins.str] = None,
        worker_id: typing.Optional[builtins.str] = None,
        result: typing.Optional[builtins.str] = None,
        llm_tokens: typing.Optional["Tokens"] = None,
        agent_version: typing.Any = None,
    ) -> None:
        '''Constructs a new Execution instance.

        :param id: - Unique identifier of the execution.
        :param agent_id: - Identifier of the agent performing the execution.
        :param organization_id: - Identifier of the organization associated with the execution.
        :param input: - Input provided for the execution.
        :param status: - Current status of the execution.
        :param last_executed_node_id: - Identifier of the last executed node.
        :param memory_thread_id: - Identifier of the memory thread associated with the execution.
        :param parent_execution: -
        :param worker_id: - Identifier of the worker associated with the execution.
        :param result: -
        :param llm_tokens: -
        :param agent_version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb3511e5562e6adcbc92f800855d3a0afb25a625d0c55d5485a4a1dce9c4d0f5)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument agent_id", value=agent_id, expected_type=type_hints["agent_id"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument last_executed_node_id", value=last_executed_node_id, expected_type=type_hints["last_executed_node_id"])
            check_type(argname="argument memory_thread_id", value=memory_thread_id, expected_type=type_hints["memory_thread_id"])
            check_type(argname="argument parent_execution", value=parent_execution, expected_type=type_hints["parent_execution"])
            check_type(argname="argument worker_id", value=worker_id, expected_type=type_hints["worker_id"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
            check_type(argname="argument llm_tokens", value=llm_tokens, expected_type=type_hints["llm_tokens"])
            check_type(argname="argument agent_version", value=agent_version, expected_type=type_hints["agent_version"])
        jsii.create(self.__class__, self, [id, agent_id, organization_id, input, status, last_executed_node_id, memory_thread_id, parent_execution, worker_id, result, llm_tokens, agent_version])

    @jsii.member(jsii_name="create")
    @builtins.classmethod
    def create(
        cls,
        agent: "Agent",
        input: builtins.str,
        files: typing.Sequence[builtins.str],
        worker_id: typing.Optional[builtins.str] = None,
        thread_id: typing.Optional[builtins.str] = None,
        parent_execution_id: typing.Optional[builtins.str] = None,
        tool_call_name: typing.Optional[builtins.str] = None,
        agent_version: typing.Any = None,
    ) -> typing.Any:
        '''
        :param agent: -
        :param input: -
        :param files: -
        :param worker_id: -
        :param thread_id: -
        :param parent_execution_id: -
        :param tool_call_name: -
        :param agent_version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28ac71fcc66c47d57a2431d7b9d1ededfeebe4d25d4d76be0af7aea52433b43e)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument files", value=files, expected_type=type_hints["files"])
            check_type(argname="argument worker_id", value=worker_id, expected_type=type_hints["worker_id"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument parent_execution_id", value=parent_execution_id, expected_type=type_hints["parent_execution_id"])
            check_type(argname="argument tool_call_name", value=tool_call_name, expected_type=type_hints["tool_call_name"])
            check_type(argname="argument agent_version", value=agent_version, expected_type=type_hints["agent_version"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "create", [agent, input, files, worker_id, thread_id, parent_execution_id, tool_call_name, agent_version]))

    @jsii.member(jsii_name="fetch")
    @builtins.classmethod
    def fetch(cls, agent: "Agent", execution_id: builtins.str) -> typing.Any:
        '''
        :param agent: -
        :param execution_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5826ee4343bbc6d6fa82b8318fb69ba8915209dc65ef5871fcded50883e01a3b)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument execution_id", value=execution_id, expected_type=type_hints["execution_id"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "fetch", [agent, execution_id]))

    @jsii.member(jsii_name="initExecution")
    @builtins.classmethod
    def init_execution(cls, created_execution: typing.Any) -> "Execution":
        '''
        :param created_execution: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a16dd673599a3466cd88daa634558ce551e5bf88775633c2a1b347c8d331cc4)
            check_type(argname="argument created_execution", value=created_execution, expected_type=type_hints["created_execution"])
        return typing.cast("Execution", jsii.sinvoke(cls, "initExecution", [created_execution]))

    @jsii.member(jsii_name="retrievePendingExecution")
    @builtins.classmethod
    def retrieve_pending_execution(
        cls,
        agent: "Agent",
        worker_id: builtins.str,
    ) -> typing.Any:
        '''
        :param agent: -
        :param worker_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77c3a6862ed0afbaef96d1fb83314e009abc247417477fc19054c75929da550d)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument worker_id", value=worker_id, expected_type=type_hints["worker_id"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "retrievePendingExecution", [agent, worker_id]))

    @jsii.member(jsii_name="update")
    @builtins.classmethod
    def update(
        cls,
        agent: "Agent",
        execution_id: builtins.str,
        delta: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Any:
        '''Updates an execution with the specified delta changes.

        :param agent: - The agent associated with the execution.
        :param execution_id: - The ID of the execution to update.
        :param delta: - A record of changes to apply to the execution.

        :return: The updated execution object.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cee0f42d8d8dd5f66e986850120e23b19cc68cac936f98a8dd25fb36353d17a)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument execution_id", value=execution_id, expected_type=type_hints["execution_id"])
            check_type(argname="argument delta", value=delta, expected_type=type_hints["delta"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "update", [agent, execution_id, delta]))

    @builtins.property
    @jsii.member(jsii_name="inputMessage")
    def input_message(self) -> "IMemoryMessage":
        '''Retrieves the input message formatted as a memory message.

        Combines text and file references into a single message object.

        :return: An object representing the user's input message.
        '''
        return typing.cast("IMemoryMessage", jsii.get(self, "inputMessage"))

    @builtins.property
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        '''- Identifier of the agent performing the execution.'''
        return typing.cast(builtins.str, jsii.get(self, "agentId"))

    @agent_id.setter
    def agent_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b03ca08f9b2b069041973b39cf02c9a0068d90548e5ddee63b20fe94c7012609)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="agentVersion")
    def agent_version(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "agentVersion"))

    @agent_version.setter
    def agent_version(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b8ae0a9930209f40a66e2e42b95dd021cdd8ddba299929a31caa19ae08d4cf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''- Unique identifier of the execution.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d868b6b5ce250193ce443b9016b04756769b83eeba535e78241ec0ff3f83d51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> "IExecutionInput":
        '''- Input provided for the execution.'''
        return typing.cast("IExecutionInput", jsii.get(self, "input"))

    @input.setter
    def input(self, value: "IExecutionInput") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf2cbec0d7a7f57322611349ee6da80c76ffc15d17073f0a02db00de934ea18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "input", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastExecutedNodeId")
    def last_executed_node_id(self) -> builtins.str:
        '''- Identifier of the last executed node.'''
        return typing.cast(builtins.str, jsii.get(self, "lastExecutedNodeId"))

    @last_executed_node_id.setter
    def last_executed_node_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f14ab38fd58bcb6df93f21afda177a617f7ba0d607127377b3613011486dd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastExecutedNodeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="llmTokens")
    def llm_tokens(self) -> "Tokens":
        return typing.cast("Tokens", jsii.get(self, "llmTokens"))

    @llm_tokens.setter
    def llm_tokens(self, value: "Tokens") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b8ec1c80577669cd65855b4bfcc994db091cf6f987b85815778246c461c834f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "llmTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryThreadId")
    def memory_thread_id(self) -> builtins.str:
        '''- Identifier of the memory thread associated with the execution.'''
        return typing.cast(builtins.str, jsii.get(self, "memoryThreadId"))

    @memory_thread_id.setter
    def memory_thread_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71b5fe859564b314681ecc8ec189116efd662d6e84e6ac8185c34215670ec574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryThreadId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''- Identifier of the organization associated with the execution.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cdb7bc0e59f92fdd53d0635a8fca37266c786acca82dac2cbfc332ac269981)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentExecution")
    def parent_execution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentExecution"))

    @parent_execution.setter
    def parent_execution(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98eb70fdda04bc040f99a78963bf4c39b92357daed49526791876d5d160ac033)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentExecution", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="result")
    def result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "result"))

    @result.setter
    def result(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cba55b034120440ccd908317158f72c44d2b7322aebe344934e7495df875f5bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "result", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> "ExecutionStatus":
        '''- Current status of the execution.'''
        return typing.cast("ExecutionStatus", jsii.get(self, "status"))

    @status.setter
    def status(self, value: "ExecutionStatus") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ea35b2f322e75bd9b6c5f06edfbe93b6c622ef9bc2c373933a362ffe4af250)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workerId")
    def worker_id(self) -> builtins.str:
        '''- Identifier of the worker associated with the execution.'''
        return typing.cast(builtins.str, jsii.get(self, "workerId"))

    @worker_id.setter
    def worker_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b54b957eb2ffee3bc5db4dc5843d7381ada868fa8b19457c6ae7bb85e5235834)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workerId", value) # pyright: ignore[reportArgumentType]


@jsii.enum(jsii_type="xpander-sdk.ExecutionStatus")
class ExecutionStatus(enum.Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"


class Graph(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Graph"):
    '''Represents a graph structure containing nodes related to an agent.

    :class: Graph
    :extends: Base *
    :memberof: xpander.ai
    '''

    def __init__(self, agent: "Agent", items: typing.Sequence["GraphItem"]) -> None:
        '''
        :param agent: -
        :param items: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05c62bde7fdbe61c5e8a021bd34dd2caa05004f9b05f08679285c1916bbac5c0)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument items", value=items, expected_type=type_hints["items"])
        jsii.create(self.__class__, self, [agent, items])

    @jsii.member(jsii_name="addNode")
    def add_node(self, node: typing.Union["Agent", "GraphItem"]) -> "GraphItem":
        '''Adds a new node to the graph.

        :param node: - The node to add, which can be an agent or a graph item.

        :return: The newly added graph item.

        :throws: {Error} If adding the node fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa425681e3f5e5317e5e11364c4e8fd5e072b73205f40342eb460fdc7c769fa5)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast("GraphItem", jsii.invoke(self, "addNode", [node]))

    @jsii.member(jsii_name="findNodeByItemId")
    def find_node_by_item_id(
        self,
        item_id: builtins.str,
    ) -> typing.Optional["GraphItem"]:
        '''Finds a node in the graph by its item ID.

        :param item_id: - The item ID to search for.

        :return: The found graph item or undefined if not found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b1d141f90de09eccb807109ef6536ff2c9788996c910b07bd8d1e73db2d04a6)
            check_type(argname="argument item_id", value=item_id, expected_type=type_hints["item_id"])
        return typing.cast(typing.Optional["GraphItem"], jsii.invoke(self, "findNodeByItemId", [item_id]))

    @jsii.member(jsii_name="findNodeByName")
    def find_node_by_name(self, name: builtins.str) -> typing.Optional["GraphItem"]:
        '''Finds a node in the graph by its name.

        :param name: - The item ID to search for.

        :return: The found graph item or undefined if not found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3507c211c7595e5c0f4712af30156e3ff1d0137bf46f41ae16951f52221f66a9)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(typing.Optional["GraphItem"], jsii.invoke(self, "findNodeByName", [name]))

    @jsii.member(jsii_name="findNodeByNodeId")
    def find_node_by_node_id(
        self,
        node_id: builtins.str,
    ) -> typing.Optional["GraphItem"]:
        '''Finds a node in the graph by its node ID.

        :param node_id: - The node ID to search for.

        :return: The found graph item or undefined if not found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e5c908c03ffa1a741480d3abd5a079bcf0c1ac187699aed7deb5ab56fce6529)
            check_type(argname="argument node_id", value=node_id, expected_type=type_hints["node_id"])
        return typing.cast(typing.Optional["GraphItem"], jsii.invoke(self, "findNodeByNodeId", [node_id]))

    @jsii.member(jsii_name="reset")
    def reset(self) -> None:
        '''Resets the graph for the associated agent.

        :throws: {Error} If resetting the graph fails.
        '''
        return typing.cast(None, jsii.invoke(self, "reset", []))

    @builtins.property
    @jsii.member(jsii_name="isEmpty")
    def is_empty(self) -> builtins.bool:
        '''Checks whether the graph is empty.

        :return: True if the graph is empty, false otherwise.
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isEmpty"))

    @builtins.property
    @jsii.member(jsii_name="mcpNodes")
    def mcp_nodes(self) -> typing.List["GraphItem"]:
        return typing.cast(typing.List["GraphItem"], jsii.get(self, "mcpNodes"))

    @builtins.property
    @jsii.member(jsii_name="nodes")
    def nodes(self) -> typing.List["GraphItem"]:
        '''Gets the list of nodes in the graph.

        :return: The list of graph items.
        '''
        return typing.cast(typing.List["GraphItem"], jsii.get(self, "nodes"))

    @builtins.property
    @jsii.member(jsii_name="textual")
    def textual(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "textual"))

    @builtins.property
    @jsii.member(jsii_name="lastNode")
    def last_node(self) -> typing.Optional["GraphItem"]:
        '''Gets the last node in the graph.

        :return: The last graph item or undefined if the graph is empty.
        '''
        return typing.cast(typing.Optional["GraphItem"], jsii.get(self, "lastNode"))

    @builtins.property
    @jsii.member(jsii_name="lastNodeInSequence")
    def last_node_in_sequence(self) -> typing.Optional["GraphItem"]:
        '''Gets the last node in sequence.

        :return: The last graph item or undefined if the graph is empty.
        '''
        return typing.cast(typing.Optional["GraphItem"], jsii.get(self, "lastNodeInSequence"))

    @builtins.property
    @jsii.member(jsii_name="rootNode")
    def root_node(self) -> typing.Optional["GraphItem"]:
        return typing.cast(typing.Optional["GraphItem"], jsii.get(self, "rootNode"))


class GraphItem(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.GraphItem"):
    '''Represents a single item (node) in an agent's graph structure.

    :class: GraphItem
    :extends: Base *
    :memberof: xpander.ai
    '''

    def __init__(
        self,
        agent: "Agent",
        id: typing.Optional[builtins.str] = None,
        item_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[AgentGraphItemType] = None,
        is_local_tool: typing.Optional[builtins.bool] = None,
        targets: typing.Optional[typing.Sequence[builtins.str]] = None,
        settings: typing.Any = None,
    ) -> None:
        '''
        :param agent: -
        :param id: -
        :param item_id: -
        :param name: -
        :param type: -
        :param is_local_tool: -
        :param targets: -
        :param settings: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15160dba22952263e9151beef520c9612beb9cb07eed594d7bb4d56d5119adb4)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument item_id", value=item_id, expected_type=type_hints["item_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument is_local_tool", value=is_local_tool, expected_type=type_hints["is_local_tool"])
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
            check_type(argname="argument settings", value=settings, expected_type=type_hints["settings"])
        jsii.create(self.__class__, self, [agent, id, item_id, name, type, is_local_tool, targets, settings])

    @jsii.member(jsii_name="connect")
    def connect(self, targets: typing.Sequence["GraphItem"]) -> "GraphItem":
        '''Connects this graph item to other graph items, creating edges in the graph.

        :param targets: - The target graph items to connect to.

        :return: The updated graph item after establishing connections.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f56ab7aacb7878e1d39e5898ac1427926bfc05426f15db694d3fc0ff734dedad)
            check_type(argname="argument targets", value=targets, expected_type=type_hints["targets"])
        return typing.cast("GraphItem", jsii.invoke(self, "connect", [targets]))

    @jsii.member(jsii_name="save")
    def save(self) -> "GraphItem":
        '''Saves the current graph item state to the server.

        :return: The updated graph item after saving.

        :throws: {Error} If saving the graph item fails.
        '''
        return typing.cast("GraphItem", jsii.invoke(self, "save", []))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74968991c9a0c8c387a3fd1115e9e2ee1dcfc781eafd41ea456f2215d517ff05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isLocalTool")
    def is_local_tool(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isLocalTool"))

    @is_local_tool.setter
    def is_local_tool(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad4d6791c897c3b4cba72154de942bf44559197ad1162bd5610ffe8e1672b11f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isLocalTool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="itemId")
    def item_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "itemId"))

    @item_id.setter
    def item_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebba065518cc99903325a7584e1d0747cc5bcfea4a9cd32a741ae37d3f91b2f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3a4981d71edb62a9f18e2559a8e1c3ce4c8234ae77ce043029575f4d94187c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targets")
    def targets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targets"))

    @targets.setter
    def targets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac535ec8b6e6592e8b1da2efcbcc433463a94dc3f8b822fc0ffbae7245e36820)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> AgentGraphItemType:
        return typing.cast(AgentGraphItemType, jsii.get(self, "type"))

    @type.setter
    def type(self, value: AgentGraphItemType) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fefc2e34cc9c85d0ecc86ca114ee5d300ccf9e14fe00bb70821a4796b530eb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="settings")
    def settings(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "settings"))

    @settings.setter
    def settings(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66d78e4b33ae25244cb7b81ee8ec05b2cc6797c8ff01f37b427240985f25f7c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "settings", value) # pyright: ignore[reportArgumentType]


@jsii.interface(jsii_type="xpander-sdk.IAgentGraphItemAdvancedFilteringOption")
class IAgentGraphItemAdvancedFilteringOption(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="returnables")
    def returnables(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @returnables.setter
    def returnables(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="searchables")
    def searchables(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @searchables.setter
    def searchables(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...


class _IAgentGraphItemAdvancedFilteringOptionProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IAgentGraphItemAdvancedFilteringOption"

    @builtins.property
    @jsii.member(jsii_name="returnables")
    def returnables(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "returnables"))

    @returnables.setter
    def returnables(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c37442176fd38f417112ebe47d309cfbcd7730390b5e828c327831187383b0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "returnables", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="searchables")
    def searchables(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "searchables"))

    @searchables.setter
    def searchables(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a22b984d43570db7290f1372800735e3ac718279f0b81723ed1d35d12bc3e7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "searchables", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAgentGraphItemAdvancedFilteringOption).__jsii_proxy_class__ = lambda : _IAgentGraphItemAdvancedFilteringOptionProxy


@jsii.interface(jsii_type="xpander-sdk.IAgentGraphItemMCPSettings")
class IAgentGraphItemMCPSettings(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        ...

    @url.setter
    def url(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="allowedTools")
    def allowed_tools(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @allowed_tools.setter
    def allowed_tools(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> typing.Optional[builtins.str]:
        ...

    @api_key.setter
    def api_key(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAgentGraphItemMCPSettingsProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IAgentGraphItemMCPSettings"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fb360ef1fd0dcf7f3a19dca1e9bfda4864bf9b2135ee0b3e2c58cdbdd93c5a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b925c95748b3345b4bb550bf691c8bf2ed25b265328e9941c7ea089164779ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedTools")
    def allowed_tools(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedTools"))

    @allowed_tools.setter
    def allowed_tools(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06b0f2790ca7d605344b619d76ee541c60899dc5da95e03d5fb1f909b4d3142f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedTools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d01f08d3c62996d9ee3cb22120fdd61c8bb47a41dd73e73eddaed059f977795c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAgentGraphItemMCPSettings).__jsii_proxy_class__ = lambda : _IAgentGraphItemMCPSettingsProxy


@jsii.interface(jsii_type="xpander-sdk.IAgentGraphItemSchema")
class IAgentGraphItemSchema(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        ...

    @input.setter
    def input(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        ...

    @output.setter
    def output(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        ...


class _IAgentGraphItemSchemaProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IAgentGraphItemSchema"

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "input"))

    @input.setter
    def input(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d83a27065ff688296f54a2b4a7b7bd9e2cf50799491f1783c29eecaa4fb598e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "input", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.get(self, "output"))

    @output.setter
    def output(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10c09b4778194db94a8d00c666b7a1871afdce4091cd3cac67e6f78ea507904a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "output", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAgentGraphItemSchema).__jsii_proxy_class__ = lambda : _IAgentGraphItemSchemaProxy


@jsii.interface(jsii_type="xpander-sdk.IAgentGraphItemSettings")
class IAgentGraphItemSettings(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="advancedFilteringOptions")
    def advanced_filtering_options(
        self,
    ) -> typing.Optional[typing.List[IAgentGraphItemAdvancedFilteringOption]]:
        ...

    @advanced_filtering_options.setter
    def advanced_filtering_options(
        self,
        value: typing.Optional[typing.List[IAgentGraphItemAdvancedFilteringOption]],
    ) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        ...

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="instructions")
    def instructions(self) -> typing.Optional[builtins.str]:
        ...

    @instructions.setter
    def instructions(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="mcpSettings")
    def mcp_settings(self) -> typing.Optional[IAgentGraphItemMCPSettings]:
        ...

    @mcp_settings.setter
    def mcp_settings(self, value: typing.Optional[IAgentGraphItemMCPSettings]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="schemas")
    def schemas(self) -> typing.Optional[IAgentGraphItemSchema]:
        ...

    @schemas.setter
    def schemas(self, value: typing.Optional[IAgentGraphItemSchema]) -> None:
        ...


class _IAgentGraphItemSettingsProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IAgentGraphItemSettings"

    @builtins.property
    @jsii.member(jsii_name="advancedFilteringOptions")
    def advanced_filtering_options(
        self,
    ) -> typing.Optional[typing.List[IAgentGraphItemAdvancedFilteringOption]]:
        return typing.cast(typing.Optional[typing.List[IAgentGraphItemAdvancedFilteringOption]], jsii.get(self, "advancedFilteringOptions"))

    @advanced_filtering_options.setter
    def advanced_filtering_options(
        self,
        value: typing.Optional[typing.List[IAgentGraphItemAdvancedFilteringOption]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82ddafee8c7509fd377d08cd4dcb4bd75f290d6cfee8836b9158c69a50a8d205)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "advancedFilteringOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48133c207df167a1e2ac7d22c1e6b7159bb3845cf34a55f28a9c340e4b17b5a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instructions")
    def instructions(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instructions"))

    @instructions.setter
    def instructions(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5abe35889371107b0a28dc1777a7eed9117daefb0245778d0a219398b8b30de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instructions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mcpSettings")
    def mcp_settings(self) -> typing.Optional[IAgentGraphItemMCPSettings]:
        return typing.cast(typing.Optional[IAgentGraphItemMCPSettings], jsii.get(self, "mcpSettings"))

    @mcp_settings.setter
    def mcp_settings(self, value: typing.Optional[IAgentGraphItemMCPSettings]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa56cad7247d597ff8e8db1d3e9b3ea9e18e1b3943bb31502832624d61e9b55a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mcpSettings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schemas")
    def schemas(self) -> typing.Optional[IAgentGraphItemSchema]:
        return typing.cast(typing.Optional[IAgentGraphItemSchema], jsii.get(self, "schemas"))

    @schemas.setter
    def schemas(self, value: typing.Optional[IAgentGraphItemSchema]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c048394bfb4cd680c4e606cd9f9da38990e641593522bda31ffc5307812b9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schemas", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAgentGraphItemSettings).__jsii_proxy_class__ = lambda : _IAgentGraphItemSettingsProxy


@jsii.interface(jsii_type="xpander-sdk.IAgentTool")
class IAgentTool(typing_extensions.Protocol):
    '''Interface representing a tool available to an agent.'''

    @builtins.property
    @jsii.member(jsii_name="functionDescription")
    def function_description(self) -> builtins.str:
        '''Function-level description for the tool.'''
        ...

    @function_description.setter
    def function_description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Unique identifier for the tool.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        '''HTTP method used to call the tool.'''
        ...

    @method.setter
    def method(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''Name of the tool.'''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Parameters required for executing the tool.'''
        ...

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''Endpoint path for the tool.'''
        ...

    @path.setter
    def path(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pathParams")
    def path_params(self) -> typing.Any:
        '''Parameters for path in the tool’s endpoint.'''
        ...

    @path_params.setter
    def path_params(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="queryParams")
    def query_params(self) -> typing.Any:
        '''Parameters for query in the tool’s endpoint.'''
        ...

    @query_params.setter
    def query_params(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="rawDescription")
    def raw_description(self) -> builtins.str:
        '''Raw description of the tool.'''
        ...

    @raw_description.setter
    def raw_description(self, value: builtins.str) -> None:
        ...


class _IAgentToolProxy:
    '''Interface representing a tool available to an agent.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IAgentTool"

    @builtins.property
    @jsii.member(jsii_name="functionDescription")
    def function_description(self) -> builtins.str:
        '''Function-level description for the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "functionDescription"))

    @function_description.setter
    def function_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__013ed94cf5075f5bf0c5bc74a0e8036501c284d35e4392ea6f15080eddc2a7ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Unique identifier for the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1b25237ddc5e6038acd2ee375459e97263388f5a79c9b19df1509b8ad33817e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        '''HTTP method used to call the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ba86af1a111c4132196288035231114364f7fd5846ba31b895e28cf0263f6b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''Name of the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdd4d28b7b8f38ee90640906c0dfa66779e13f1537479bfac62236199af53599)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Parameters required for executing the tool.'''
        return typing.cast(typing.Any, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfb31aa04b21eb4806b8482aa225a11b478a08f9a3d8fe6ed1ff02f818c62244)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''Endpoint path for the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7629b10507753cd17f8a141e1f5acf42aa3ad6279b11466521e8e879158f1c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathParams")
    def path_params(self) -> typing.Any:
        '''Parameters for path in the tool’s endpoint.'''
        return typing.cast(typing.Any, jsii.get(self, "pathParams"))

    @path_params.setter
    def path_params(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c1639f3cf0ce4876316784b66d4eb55d50082b87dcaa56347a0ebcb4c5be615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathParams", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryParams")
    def query_params(self) -> typing.Any:
        '''Parameters for query in the tool’s endpoint.'''
        return typing.cast(typing.Any, jsii.get(self, "queryParams"))

    @query_params.setter
    def query_params(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76420473c4800542a5c924d1375223fda76771d1a194354c646c87a134351b2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryParams", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rawDescription")
    def raw_description(self) -> builtins.str:
        '''Raw description of the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "rawDescription"))

    @raw_description.setter
    def raw_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94d18303f76ca1cea7f0333afa6e171a5ff4c99c53601d4772e5d916b00ae6de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rawDescription", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAgentTool).__jsii_proxy_class__ = lambda : _IAgentToolProxy


@jsii.interface(jsii_type="xpander-sdk.IBedrockTool")
class IBedrockTool(typing_extensions.Protocol):
    '''Interface representing a Bedrock tool.'''

    @builtins.property
    @jsii.member(jsii_name="toolSpec")
    def tool_spec(self) -> "IBedrockToolSpec":
        '''Specification details for the Bedrock tool.'''
        ...

    @tool_spec.setter
    def tool_spec(self, value: "IBedrockToolSpec") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="execute")
    def execute(self) -> typing.Any:
        '''Function to execute the tool, if defined.'''
        ...

    @execute.setter
    def execute(self, value: typing.Any) -> None:
        ...


class _IBedrockToolProxy:
    '''Interface representing a Bedrock tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IBedrockTool"

    @builtins.property
    @jsii.member(jsii_name="toolSpec")
    def tool_spec(self) -> "IBedrockToolSpec":
        '''Specification details for the Bedrock tool.'''
        return typing.cast("IBedrockToolSpec", jsii.get(self, "toolSpec"))

    @tool_spec.setter
    def tool_spec(self, value: "IBedrockToolSpec") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__686bee2f9cc4cb8e5e46bd20309c912c48752fa01feec49d211288fe414d9879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolSpec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="execute")
    def execute(self) -> typing.Any:
        '''Function to execute the tool, if defined.'''
        return typing.cast(typing.Any, jsii.get(self, "execute"))

    @execute.setter
    def execute(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50442d45bad8e7fa927b6be3feac263e79712091c62056e831a391b5a17c13bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "execute", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBedrockTool).__jsii_proxy_class__ = lambda : _IBedrockToolProxy


@jsii.interface(jsii_type="xpander-sdk.IBedrockToolOutput")
class IBedrockToolOutput(typing_extensions.Protocol):
    '''Output interface for a Bedrock tool.'''

    @builtins.property
    @jsii.member(jsii_name="toolSpec")
    def tool_spec(self) -> "IBedrockToolSpec":
        '''Specification of the Bedrock tool.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="execute")
    def execute(self) -> typing.Any:
        '''Function to execute the Bedrock tool.'''
        ...


class _IBedrockToolOutputProxy:
    '''Output interface for a Bedrock tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IBedrockToolOutput"

    @builtins.property
    @jsii.member(jsii_name="toolSpec")
    def tool_spec(self) -> "IBedrockToolSpec":
        '''Specification of the Bedrock tool.'''
        return typing.cast("IBedrockToolSpec", jsii.get(self, "toolSpec"))

    @builtins.property
    @jsii.member(jsii_name="execute")
    def execute(self) -> typing.Any:
        '''Function to execute the Bedrock tool.'''
        return typing.cast(typing.Any, jsii.get(self, "execute"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBedrockToolOutput).__jsii_proxy_class__ = lambda : _IBedrockToolOutputProxy


@jsii.interface(jsii_type="xpander-sdk.IBedrockToolSpec")
class IBedrockToolSpec(typing_extensions.Protocol):
    '''Interface representing the specification for a Bedrock tool.'''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''Description of what the Bedrock tool does.'''
        ...

    @description.setter
    def description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="inputSchema")
    def input_schema(self) -> "IBedrockToolSpecInputSchema":
        '''Input schema detailing required parameters for the tool.'''
        ...

    @input_schema.setter
    def input_schema(self, value: "IBedrockToolSpecInputSchema") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the Bedrock tool.'''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...


class _IBedrockToolSpecProxy:
    '''Interface representing the specification for a Bedrock tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IBedrockToolSpec"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''Description of what the Bedrock tool does.'''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bab15f7ad29e9cbdf37869d4d12b1eca4937a0130eb1409bb74f1149d0dfc26b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inputSchema")
    def input_schema(self) -> "IBedrockToolSpecInputSchema":
        '''Input schema detailing required parameters for the tool.'''
        return typing.cast("IBedrockToolSpecInputSchema", jsii.get(self, "inputSchema"))

    @input_schema.setter
    def input_schema(self, value: "IBedrockToolSpecInputSchema") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39dfbf6fa195f65cf55b428cbf9c7e700af738bcd9c47ebdda318cfedf78e70a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inputSchema", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the Bedrock tool.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0534d2b1daae9caffc87b99f4b6cc09e1a9eac3888374c04e9c619375c2f1b35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBedrockToolSpec).__jsii_proxy_class__ = lambda : _IBedrockToolSpecProxy


@jsii.interface(jsii_type="xpander-sdk.IBedrockToolSpecInputSchema")
class IBedrockToolSpecInputSchema(typing_extensions.Protocol):
    '''Interface representing the input schema for a Bedrock tool.'''

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.Mapping[builtins.str, "IToolParameter"]:
        '''JSON schema defining the parameters for the tool.'''
        ...

    @json.setter
    def json(self, value: typing.Mapping[builtins.str, "IToolParameter"]) -> None:
        ...


class _IBedrockToolSpecInputSchemaProxy:
    '''Interface representing the input schema for a Bedrock tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IBedrockToolSpecInputSchema"

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.Mapping[builtins.str, "IToolParameter"]:
        '''JSON schema defining the parameters for the tool.'''
        return typing.cast(typing.Mapping[builtins.str, "IToolParameter"], jsii.get(self, "json"))

    @json.setter
    def json(self, value: typing.Mapping[builtins.str, "IToolParameter"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1454322c6f1b39bdf36a5d88226526fce2d55d1e13ada58cf00d44f12fd64366)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "json", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBedrockToolSpecInputSchema).__jsii_proxy_class__ = lambda : _IBedrockToolSpecInputSchemaProxy


@jsii.interface(jsii_type="xpander-sdk.IConfiguration")
class IConfiguration(typing_extensions.Protocol):
    '''Interface representing configuration settings for the xpanderAI client.'''

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        '''API key for authenticating with xpanderAI.'''
        ...

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> typing.Optional[builtins.str]:
        '''Optional base URL for the xpanderAI API.'''
        ...

    @base_url.setter
    def base_url(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> typing.Optional[builtins.str]:
        '''Custom parameters for client-specific settings.'''
        ...

    @organization_id.setter
    def organization_id(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IConfigurationProxy:
    '''Interface representing configuration settings for the xpanderAI client.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IConfiguration"

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        '''API key for authenticating with xpanderAI.'''
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3e8b15e3c3381cc6704c1ee29aa4c16d1b4a86e2ac011b6e441b3e0b431f930)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> typing.Optional[builtins.str]:
        '''Optional base URL for the xpanderAI API.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07a526e81165d7b0acee70572029a007577d042379f52fcd7844f14a292ff14e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> typing.Optional[builtins.str]:
        '''Custom parameters for client-specific settings.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df183128da8ce312ade8f62d98d9db3bba128d9acf1d9f56955baae69e409c37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IConfiguration).__jsii_proxy_class__ = lambda : _IConfigurationProxy


@jsii.interface(jsii_type="xpander-sdk.IExecutionInput")
class IExecutionInput(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> "UserDetails":
        ...

    @user.setter
    def user(self, value: "UserDetails") -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="files")
    def files(self) -> typing.Optional[typing.List[builtins.str]]:
        ...

    @files.setter
    def files(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.Optional[builtins.str]:
        ...

    @text.setter
    def text(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IExecutionInputProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IExecutionInput"

    @builtins.property
    @jsii.member(jsii_name="user")
    def user(self) -> "UserDetails":
        return typing.cast("UserDetails", jsii.get(self, "user"))

    @user.setter
    def user(self, value: "UserDetails") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da3a818f4694a99ea585b769eb098754a7fe2d1868cc0704ace9d8e92ba7f3f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "user", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="files")
    def files(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "files"))

    @files.setter
    def files(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ded72ddaf5f71f91ade05bb19c950ea501c6e1e1233100d5f19c597947e7d3aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "files", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="text")
    def text(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "text"))

    @text.setter
    def text(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8eb39d06928f51e090591017e234f9560633786e66b238d3b42531c3252f0eea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "text", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExecutionInput).__jsii_proxy_class__ = lambda : _IExecutionInputProxy


@jsii.interface(jsii_type="xpander-sdk.ILocalTool")
class ILocalTool(typing_extensions.Protocol):
    '''Interface for a local tool.'''

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> "ILocalToolFunction":
        '''Function specification for the local tool.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''Specifies the tool type as a 'function'.'''
        ...


class _ILocalToolProxy:
    '''Interface for a local tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.ILocalTool"

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> "ILocalToolFunction":
        '''Function specification for the local tool.'''
        return typing.cast("ILocalToolFunction", jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''Specifies the tool type as a 'function'.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILocalTool).__jsii_proxy_class__ = lambda : _ILocalToolProxy


@jsii.interface(jsii_type="xpander-sdk.ILocalToolFunction")
class ILocalToolFunction(typing_extensions.Protocol):
    '''Interface for a function within a local tool.'''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''Description of the local tool's purpose.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the local tool function.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Parameters used by the local tool function.'''
        ...


class _ILocalToolFunctionProxy:
    '''Interface for a function within a local tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.ILocalToolFunction"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''Description of the local tool's purpose.'''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the local tool function.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Parameters used by the local tool function.'''
        return typing.cast(typing.Any, jsii.get(self, "parameters"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILocalToolFunction).__jsii_proxy_class__ = lambda : _ILocalToolFunctionProxy


@jsii.interface(jsii_type="xpander-sdk.IMemoryMessage")
class IMemoryMessage(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        ...

    @role.setter
    def role(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="completionResponse")
    def completion_response(self) -> typing.Any:
        ...

    @completion_response.setter
    def completion_response(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> typing.Optional[builtins.str]:
        ...

    @content.setter
    def content(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> typing.Optional[builtins.str]:
        ...

    @node_name.setter
    def node_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="toolCallId")
    def tool_call_id(self) -> typing.Optional[builtins.str]:
        ...

    @tool_call_id.setter
    def tool_call_id(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="toolCalls")
    def tool_calls(self) -> typing.Optional[typing.List["IToolCall"]]:
        ...

    @tool_calls.setter
    def tool_calls(self, value: typing.Optional[typing.List["IToolCall"]]) -> None:
        ...


class _IMemoryMessageProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IMemoryMessage"

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12e375f6294f1a5448700c974b2c29d93eaac36a1dea798ca8ded9b92594d10b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="completionResponse")
    def completion_response(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "completionResponse"))

    @completion_response.setter
    def completion_response(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c40dff0d9263c5102becbce5d5ea18378e769c964c924a052f6c023b15b889e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completionResponse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "content"))

    @content.setter
    def content(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2af096115236a1c0df0e3b558acc615c594ec3a2f016074ae50c4c83fcb2600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "content", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeName"))

    @node_name.setter
    def node_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__221c82f5a357c0f118efe86c29a8a97b2a8f51d955265c9972dc156543547bb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolCallId")
    def tool_call_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "toolCallId"))

    @tool_call_id.setter
    def tool_call_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d263d1c0fb18bd7e903fe0d0af692e3808ac21c99197a495a3f6c62acba8a50b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolCallId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolCalls")
    def tool_calls(self) -> typing.Optional[typing.List["IToolCall"]]:
        return typing.cast(typing.Optional[typing.List["IToolCall"]], jsii.get(self, "toolCalls"))

    @tool_calls.setter
    def tool_calls(self, value: typing.Optional[typing.List["IToolCall"]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25eaf42500bdb62a0efcb583df3587ae560b4f99f9d9214b8ebebc6131aec02e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolCalls", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMemoryMessage).__jsii_proxy_class__ = lambda : _IMemoryMessageProxy


@jsii.interface(jsii_type="xpander-sdk.INodeDescription")
class INodeDescription(typing_extensions.Protocol):
    '''Represents a prompt group + node name node's description override.'''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="promptGroupId")
    def prompt_group_id(self) -> builtins.str:
        ...


class _INodeDescriptionProxy:
    '''Represents a prompt group + node name node's description override.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.INodeDescription"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeName"))

    @builtins.property
    @jsii.member(jsii_name="promptGroupId")
    def prompt_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "promptGroupId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INodeDescription).__jsii_proxy_class__ = lambda : _INodeDescriptionProxy


@jsii.interface(jsii_type="xpander-sdk.INodeSchema")
class INodeSchema(typing_extensions.Protocol):
    '''Represents the schema of a single node with defined input and output structures.'''

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> typing.Any:
        ...

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Any:
        ...


class _INodeSchemaProxy:
    '''Represents the schema of a single node with defined input and output structures.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.INodeSchema"

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "input"))

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeName"))

    @builtins.property
    @jsii.member(jsii_name="output")
    def output(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "output"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INodeSchema).__jsii_proxy_class__ = lambda : _INodeSchemaProxy


@jsii.interface(jsii_type="xpander-sdk.IOpenAIToolFunctionOutput")
class IOpenAIToolFunctionOutput(typing_extensions.Protocol):
    '''Output interface for an OpenAI tool function.'''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''Description of the tool function's purpose.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the tool function.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="execute")
    def execute(self) -> typing.Any:
        '''Secondary execution function for Bedrock compatibility.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="func")
    def func(self) -> typing.Any:
        '''Primary function to execute the tool.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional["IToolParameter"]:
        '''Parameters required for the tool function.'''
        ...


class _IOpenAIToolFunctionOutputProxy:
    '''Output interface for an OpenAI tool function.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IOpenAIToolFunctionOutput"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''Description of the tool function's purpose.'''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the tool function.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="execute")
    def execute(self) -> typing.Any:
        '''Secondary execution function for Bedrock compatibility.'''
        return typing.cast(typing.Any, jsii.get(self, "execute"))

    @builtins.property
    @jsii.member(jsii_name="func")
    def func(self) -> typing.Any:
        '''Primary function to execute the tool.'''
        return typing.cast(typing.Any, jsii.get(self, "func"))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Optional["IToolParameter"]:
        '''Parameters required for the tool function.'''
        return typing.cast(typing.Optional["IToolParameter"], jsii.get(self, "parameters"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOpenAIToolFunctionOutput).__jsii_proxy_class__ = lambda : _IOpenAIToolFunctionOutputProxy


@jsii.interface(jsii_type="xpander-sdk.IOpenAIToolOutput")
class IOpenAIToolOutput(typing_extensions.Protocol):
    '''Output interface for an OpenAI tool.'''

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> IOpenAIToolFunctionOutput:
        '''Function specification for the OpenAI tool.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''Type of the tool, typically 'function'.'''
        ...


class _IOpenAIToolOutputProxy:
    '''Output interface for an OpenAI tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IOpenAIToolOutput"

    @builtins.property
    @jsii.member(jsii_name="function")
    def function(self) -> IOpenAIToolFunctionOutput:
        '''Function specification for the OpenAI tool.'''
        return typing.cast(IOpenAIToolFunctionOutput, jsii.get(self, "function"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''Type of the tool, typically 'function'.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOpenAIToolOutput).__jsii_proxy_class__ = lambda : _IOpenAIToolOutputProxy


@jsii.interface(jsii_type="xpander-sdk.IPGSchema")
class IPGSchema(typing_extensions.Protocol):
    '''Represents a schema group for a prompt group session (PGSchema), containing multiple node schemas.'''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="schemas")
    def schemas(self) -> typing.List[INodeSchema]:
        ...


class _IPGSchemaProxy:
    '''Represents a schema group for a prompt group session (PGSchema), containing multiple node schemas.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IPGSchema"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="schemas")
    def schemas(self) -> typing.List[INodeSchema]:
        return typing.cast(typing.List[INodeSchema], jsii.get(self, "schemas"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPGSchema).__jsii_proxy_class__ = lambda : _IPGSchemaProxy


@jsii.interface(jsii_type="xpander-sdk.ISourceNode")
class ISourceNode(typing_extensions.Protocol):
    '''Interface representing a source node in the agent's graph.'''

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Unique identifier for the source node.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Any:
        '''Metadata associated with the source node.'''
        ...

    @metadata.setter
    def metadata(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceNodeType":
        '''Type of the source node (e.g., SDK, TASK).'''
        ...

    @type.setter
    def type(self, value: "SourceNodeType") -> None:
        ...


class _ISourceNodeProxy:
    '''Interface representing a source node in the agent's graph.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.ISourceNode"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Unique identifier for the source node.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6782cb166f668691a7b4be7b743380ed50722ee1549291808eee66d6a811fed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Any:
        '''Metadata associated with the source node.'''
        return typing.cast(typing.Any, jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf5d7d569b37ac0c974cabb49c4e85f99273856f9fc2bdac40d66bc3412561d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "SourceNodeType":
        '''Type of the source node (e.g., SDK, TASK).'''
        return typing.cast("SourceNodeType", jsii.get(self, "type"))

    @type.setter
    def type(self, value: "SourceNodeType") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b0db8ab6f32bead8676f5d65edb0c8465aea43ef940f7b1d7b2ba9d2d577c39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISourceNode).__jsii_proxy_class__ = lambda : _ISourceNodeProxy


@jsii.interface(jsii_type="xpander-sdk.ITool")
class ITool(typing_extensions.Protocol):
    '''Interface representing a general tool.'''

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''A description of the tool's functionality.'''
        ...

    @description.setter
    def description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the tool.'''
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="func")
    def func(self) -> typing.Any:
        '''Function to execute the tool's logic.'''
        ...

    @func.setter
    def func(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "IToolParameter"]]:
        '''Parameters required by the tool.'''
        ...

    @parameters.setter
    def parameters(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, "IToolParameter"]],
    ) -> None:
        ...


class _IToolProxy:
    '''Interface representing a general tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.ITool"

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''A description of the tool's functionality.'''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f56ea2b548b4cdfe22f0f80bf2c3f88697c04aedd2bf7fe61755b4eb9cee55b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5396ff1ffb06161e7b92840a35a663b1f418ffdcc7dde0e2593addf6ca31936a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="func")
    def func(self) -> typing.Any:
        '''Function to execute the tool's logic.'''
        return typing.cast(typing.Any, jsii.get(self, "func"))

    @func.setter
    def func(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__682720a04a90eb0d29239c0baf8e36b53b239f76f1079edf9cd418a69ddb97ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "func", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "IToolParameter"]]:
        '''Parameters required by the tool.'''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "IToolParameter"]], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, "IToolParameter"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bf23d7676e5d1c7e307b10d99651d3e323b4741175a001eec3d04daa9f6a063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITool).__jsii_proxy_class__ = lambda : _IToolProxy


@jsii.interface(jsii_type="xpander-sdk.IToolCall")
class IToolCall(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        ...

    @name.setter
    def name(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="toolCallId")
    def tool_call_id(self) -> builtins.str:
        ...

    @tool_call_id.setter
    def tool_call_id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="payload")
    def payload(self) -> typing.Optional[builtins.str]:
        ...

    @payload.setter
    def payload(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IToolCallProxy:
    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IToolCall"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5219f06879c23f3e080fc36ccd3ecf3404dfc6994def97d5e4ec94ce59d72bb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolCallId")
    def tool_call_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "toolCallId"))

    @tool_call_id.setter
    def tool_call_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__039a35d67dfcf0e4fcf0d24c95fae7adcb68a33fbc193c12840c321781f41670)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolCallId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="payload")
    def payload(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payload"))

    @payload.setter
    def payload(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c4f34dbc98830433192bba8d2c699a1cb8148d1491b27977e6d346e261fb913)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payload", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IToolCall).__jsii_proxy_class__ = lambda : _IToolCallProxy


@jsii.interface(jsii_type="xpander-sdk.IToolCallPayload")
class IToolCallPayload(typing_extensions.Protocol):
    '''Interface representing the payload for a tool call.'''

    @builtins.property
    @jsii.member(jsii_name="bodyParams")
    def body_params(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Parameters for the request body.'''
        ...

    @body_params.setter
    def body_params(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Headers for the tool call request.'''
        ...

    @headers.setter
    def headers(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="pathParams")
    def path_params(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Parameters for the URL path.'''
        ...

    @path_params.setter
    def path_params(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="queryParams")
    def query_params(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Parameters for the URL query string.'''
        ...

    @query_params.setter
    def query_params(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...


class _IToolCallPayloadProxy:
    '''Interface representing the payload for a tool call.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IToolCallPayload"

    @builtins.property
    @jsii.member(jsii_name="bodyParams")
    def body_params(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Parameters for the request body.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "bodyParams"))

    @body_params.setter
    def body_params(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9832f75123fcf9d9b942f4c173edc15dd68204b28ad5d4260488d6c5c649f9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bodyParams", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Headers for the tool call request.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a367c116b987fb49136a9814177e4d056c61593dd022f63355bb894da7fc9988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathParams")
    def path_params(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Parameters for the URL path.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "pathParams"))

    @path_params.setter
    def path_params(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e21845a97036e31f029489182b71f645274dafcc99c56e102732ed75019f377)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathParams", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="queryParams")
    def query_params(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Parameters for the URL query string.'''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "queryParams"))

    @query_params.setter
    def query_params(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__893f015e220df05bf7b08ec5d24e2064db840604744494f599f33b596f114ee0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryParams", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IToolCallPayload).__jsii_proxy_class__ = lambda : _IToolCallPayloadProxy


@jsii.interface(jsii_type="xpander-sdk.IToolExecutionResult")
class IToolExecutionResult(typing_extensions.Protocol):
    '''Represents the result of a tool execution, including status, data, and success indicator.'''

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Any:
        ...

    @data.setter
    def data(self, value: typing.Any) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Mapping[builtins.str, typing.Any]:
        ...

    @headers.setter
    def headers(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="isSuccess")
    def is_success(self) -> builtins.bool:
        ...

    @is_success.setter
    def is_success(self, value: builtins.bool) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        ...

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        ...


class _IToolExecutionResultProxy:
    '''Represents the result of a tool execution, including status, data, and success indicator.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IToolExecutionResult"

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "data"))

    @data.setter
    def data(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a45442afc737189c680b610029e36c0388f812ca6addfc20d90f2255236a7a1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "data", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f74a57170964ac6f2225d4a42e688907f1b3fc6d5dcc4cefae60ba4c69e6a205)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSuccess")
    def is_success(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isSuccess"))

    @is_success.setter
    def is_success(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f354465848d57d08212584493a7b8ebb70e6a4185a12514d09d39089267cc34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSuccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd332b88cb4f7bb75ce8e88200df9b702232ca7807d466896031bba1bac55a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statusCode", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IToolExecutionResult).__jsii_proxy_class__ = lambda : _IToolExecutionResultProxy


@jsii.interface(jsii_type="xpander-sdk.IToolInstructions")
class IToolInstructions(typing_extensions.Protocol):
    '''Interface representing instructions for a tool.'''

    @builtins.property
    @jsii.member(jsii_name="functionDescription")
    def function_description(self) -> builtins.str:
        '''Description of the tool's function.'''
        ...

    @function_description.setter
    def function_description(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Identifier for the tool.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Parameters required by the tool.'''
        ...

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        ...


class _IToolInstructionsProxy:
    '''Interface representing instructions for a tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IToolInstructions"

    @builtins.property
    @jsii.member(jsii_name="functionDescription")
    def function_description(self) -> builtins.str:
        '''Description of the tool's function.'''
        return typing.cast(builtins.str, jsii.get(self, "functionDescription"))

    @function_description.setter
    def function_description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbdc5a25cd119bc40de0970a3da5a996792b481e3623e5692f2220f66858eaff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionDescription", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Identifier for the tool.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__116d46c0c30294630e565344bb001679a311f6d4bdf7fde9def35de5f5e69bff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''Parameters required by the tool.'''
        return typing.cast(typing.Any, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09181db93f9b9267ab92d06c025f7bac4699c1fdac9ca798c651a63559aa913f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IToolInstructions).__jsii_proxy_class__ = lambda : _IToolInstructionsProxy


@jsii.interface(jsii_type="xpander-sdk.IToolParameter")
class IToolParameter(typing_extensions.Protocol):
    '''Interface representing a parameter for a tool.'''

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Mapping[builtins.str, "IToolParameter"]:
        '''Properties of the parameter, if it is an object type.'''
        ...

    @properties.setter
    def properties(self, value: typing.Mapping[builtins.str, "IToolParameter"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of the parameter (e.g., string, object).'''
        ...

    @type.setter
    def type(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of required properties within this parameter, if any.'''
        ...

    @required.setter
    def required(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        ...


class _IToolParameterProxy:
    '''Interface representing a parameter for a tool.'''

    __jsii_type__: typing.ClassVar[str] = "xpander-sdk.IToolParameter"

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.Mapping[builtins.str, IToolParameter]:
        '''Properties of the parameter, if it is an object type.'''
        return typing.cast(typing.Mapping[builtins.str, IToolParameter], jsii.get(self, "properties"))

    @properties.setter
    def properties(self, value: typing.Mapping[builtins.str, IToolParameter]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187dae4a63a6fee1ee6e1cb395b2f91742bd245c20c13ab04570590726c5ef61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of the parameter (e.g., string, object).'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16039ce6185f742cd5865e412fc0342905a7a6d458331abeea0c8aea52fd0eb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of required properties within this parameter, if any.'''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "required"))

    @required.setter
    def required(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52b13164b7161ac045d14f7c4212e2fc304cf9b4c0234c2221c11807a860fee0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "required", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IToolParameter).__jsii_proxy_class__ = lambda : _IToolParameterProxy


class KnowledgeBase(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.KnowledgeBase",
):
    def __init__(
        self,
        id: builtins.str,
        name: builtins.str,
        description: builtins.str,
        strategy: "KnowledgeBaseStrategy",
        documents: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param id: -
        :param name: -
        :param description: -
        :param strategy: -
        :param documents: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51e3a6f2086f6f694ae00811d3c8cfbc7998d5e84bc5e953097d209d2b1d9e8e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument strategy", value=strategy, expected_type=type_hints["strategy"])
            check_type(argname="argument documents", value=documents, expected_type=type_hints["documents"])
        jsii.create(self.__class__, self, [id, name, description, strategy, documents])

    @jsii.member(jsii_name="loadByAgent")
    @builtins.classmethod
    def load_by_agent(cls, agent: "Agent") -> typing.List["KnowledgeBase"]:
        '''
        :param agent: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd9e1109152304880a099fddab37e97bb8a4b8eac7d4eaeb9ba5b64b7d20f6c)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
        return typing.cast(typing.List["KnowledgeBase"], jsii.sinvoke(cls, "loadByAgent", [agent]))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5346ca86b97d9beb023662f6917773322c22dd333b4088d0a3e1aa3f9b863f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="documents")
    def documents(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "documents"))

    @documents.setter
    def documents(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f91030cf0630f559d66490e3f6115e32fa737afa26a254c624598a4473424178)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "documents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b1a6bd536d05cb8f737d34d1a5470e5cbffbae2b7b39eabd405ec3a83750f39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec5f1b09e3bf37c8db0a7e8a770f79ae3a608fbcf53ae579ab368ca80ea281b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="strategy")
    def strategy(self) -> "KnowledgeBaseStrategy":
        return typing.cast("KnowledgeBaseStrategy", jsii.get(self, "strategy"))

    @strategy.setter
    def strategy(self, value: "KnowledgeBaseStrategy") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c985cb1467f7bafe537bc1fe177d04bb3967730f168ac32ce862f8c3d39dbe95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "strategy", value) # pyright: ignore[reportArgumentType]


class KnowledgeBaseDocument(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.KnowledgeBaseDocument",
):
    '''Represents a knowledge base document in the xpander.ai system. This is used to reference a document within a knowledge base.'''

    def __init__(
        self,
        configuration: Configuration,
        id: builtins.str,
        kb_id: builtins.str,
        document_url: builtins.str,
    ) -> None:
        '''Creates a new KnowledgeBaseDocument instance.

        :param configuration: - The configuration instance used for interacting with the xpander.ai API.
        :param id: - The unique identifier of the document.
        :param kb_id: - The identifier of the knowledge base this document belongs to.
        :param document_url: - The URL of the document stored in the knowledge base.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fd6fc1bc899c30f952acad91b807e3c07f73510da89adfa97a770eb79ad5064)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument kb_id", value=kb_id, expected_type=type_hints["kb_id"])
            check_type(argname="argument document_url", value=document_url, expected_type=type_hints["document_url"])
        jsii.create(self.__class__, self, [configuration, id, kb_id, document_url])

    @jsii.member(jsii_name="delete")
    def delete(self) -> None:
        '''Deletes the document from the knowledge base via the xpander.ai API.

        :return: void

        :throws: Will throw an error if the deletion request fails or the response status code is not in the 2xx range.
        '''
        return typing.cast(None, jsii.invoke(self, "delete", []))

    @builtins.property
    @jsii.member(jsii_name="documentUrl")
    def document_url(self) -> builtins.str:
        '''- The URL of the document stored in the knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "documentUrl"))

    @document_url.setter
    def document_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__494bbd93c6a5e9ca1966bbc40e8be3d234451861d89fcd53b23cb0e2ab4dcb02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "documentUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''- The unique identifier of the document.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f8f7ae67842812194c8b5491d2274fd0b073b0f89f63dcdfb61542b7ca735fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kbId")
    def kb_id(self) -> builtins.str:
        '''- The identifier of the knowledge base this document belongs to.'''
        return typing.cast(builtins.str, jsii.get(self, "kbId"))

    @kb_id.setter
    def kb_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a423960f6ac18af623ce08adfef52d521928c2ae5142dc93ac90cfdaed08e932)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kbId", value) # pyright: ignore[reportArgumentType]


class KnowledgeBaseItem(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.KnowledgeBaseItem",
):
    '''Represents a knowledge base in the xpander.ai system. Used to manage documents stored within the knowledge base.'''

    def __init__(
        self,
        configuration: Configuration,
        id: builtins.str,
        name: builtins.str,
        description: builtins.str,
        type: "KnowledgeBaseType",
        organization_id: builtins.str,
        total_documents: jsii.Number,
    ) -> None:
        '''Creates a new KnowledgeBaseItem instance.

        :param configuration: - The configuration instance used for interacting with the xpander.ai API.
        :param id: - The unique identifier of the knowledge base.
        :param name: - The name of the knowledge base.
        :param description: - The description of the knowledge base.
        :param type: - The type of the knowledge base.
        :param organization_id: - The ID of the organization to which the knowledge base belongs.
        :param total_documents: - The total number of documents in the knowledge base.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a16c0152501f00605cd56315921ddaa33d77f9545dc90ec0750945db59f8e57f)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument total_documents", value=total_documents, expected_type=type_hints["total_documents"])
        jsii.create(self.__class__, self, [configuration, id, name, description, type, organization_id, total_documents])

    @jsii.member(jsii_name="addDocuments")
    def add_documents(
        self,
        urls: typing.Sequence[builtins.str],
        sync: typing.Optional[builtins.bool] = None,
    ) -> typing.List[KnowledgeBaseDocument]:
        '''Adds new documents to the knowledge base using the xpander.ai API.

        :param urls: - An array of document URLs to be added to the knowledge base.
        :param sync: - Optional. If true, documents are added synchronously; otherwise, they are added asynchronously. Default is false.

        :return: An array of KnowledgeBaseDocument instances representing the added documents.

        :throws: Will throw an error if the request fails or the response status code is not in the 2xx range.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3e0c23fe2c94485ca3f32b3957337ab50312aee88a1d61e71032a2e5e55034)
            check_type(argname="argument urls", value=urls, expected_type=type_hints["urls"])
            check_type(argname="argument sync", value=sync, expected_type=type_hints["sync"])
        return typing.cast(typing.List[KnowledgeBaseDocument], jsii.invoke(self, "addDocuments", [urls, sync]))

    @jsii.member(jsii_name="listDocuments")
    def list_documents(self) -> typing.List[KnowledgeBaseDocument]:
        '''Retrieves the list of documents in the knowledge base from the xpander.ai API.

        :return: An array of KnowledgeBaseDocument instances representing the documents in the knowledge base.

        :throws: Will throw an error if the request fails or the response status code is not in the 2xx range.
        '''
        return typing.cast(typing.List[KnowledgeBaseDocument], jsii.invoke(self, "listDocuments", []))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        '''- The description of the knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__145b0ae5ea807889d0359e8b982d1eda720a42f19f365eb9d7f4c99c1779536b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''- The unique identifier of the knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f85c313f85cc78ccb4fe6b4e1f8233e113b17260168de6d9f869d554cc3a662)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''- The name of the knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5103538f7d91ad0c411c0d92613beba1e18a1ea49de878d886873d975664c0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''- The ID of the organization to which the knowledge base belongs.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20428b0e41f89ed6975763d5d75f7a678fbd8256f48c74972d3a5bf85af161f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDocuments")
    def total_documents(self) -> jsii.Number:
        '''- The total number of documents in the knowledge base.'''
        return typing.cast(jsii.Number, jsii.get(self, "totalDocuments"))

    @total_documents.setter
    def total_documents(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a81285873a8d10bdc1952072273f2ed5ddfbac0610f731bdcce75452a4014a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDocuments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "KnowledgeBaseType":
        '''- The type of the knowledge base.'''
        return typing.cast("KnowledgeBaseType", jsii.get(self, "type"))

    @type.setter
    def type(self, value: "KnowledgeBaseType") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bfc8a098157fa3cf0f23a3b0f6b364ceb07639375ef856b2763787b63f87d0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.enum(jsii_type="xpander-sdk.KnowledgeBaseStrategy")
class KnowledgeBaseStrategy(enum.Enum):
    VANILLA = "VANILLA"
    AGENTIC_RAG = "AGENTIC_RAG"


@jsii.enum(jsii_type="xpander-sdk.KnowledgeBaseType")
class KnowledgeBaseType(enum.Enum):
    MANAGED = "MANAGED"
    EXTERNAL = "EXTERNAL"


class KnowledgeBases(metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.KnowledgeBases"):
    '''Manages a collection of knowledge bases in the xpander.ai system, providing methods to list, retrieve, and create individual knowledge bases.'''

    def __init__(self, configuration: Configuration) -> None:
        '''Constructs an instance of the KnowledgeBases manager.

        :param configuration: - Configuration settings for managing knowledge bases.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c6e2dab357d715d7f0d00dc77fe0087fe20869271615fc96a075d0c48596c79)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
        jsii.create(self.__class__, self, [configuration])

    @jsii.member(jsii_name="create")
    def create(
        self,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> KnowledgeBaseItem:
        '''Creates a new knowledge base using the xpander.ai API.

        :param name: - The name of the new knowledge base.
        :param description: - Optional. The description of the knowledge base. Defaults to an empty string.

        :return: A new KnowledgeBaseItem instance representing the created knowledge base.

        :throws: Will throw an error if the creation request fails or the response status code is not in the 2xx range.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eeed02486950f43c36c0410e8a502b926d979648d745c558aa0aaad4202b149)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        return typing.cast(KnowledgeBaseItem, jsii.invoke(self, "create", [name, description]))

    @jsii.member(jsii_name="get")
    def get(self, knowledge_base_id: builtins.str) -> KnowledgeBaseItem:
        '''Retrieves a specific knowledge base by its ID from the xpander.ai API.

        :param knowledge_base_id: - The unique identifier of the knowledge base to retrieve.

        :return: The requested KnowledgeBaseItem instance.

        :throws: Will throw an error if the knowledge base is not found or if the retrieval fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22e41d43ad93e4b06027bd610f379a1454b2ed9f72ede507ae3ed2a9271d39db)
            check_type(argname="argument knowledge_base_id", value=knowledge_base_id, expected_type=type_hints["knowledge_base_id"])
        return typing.cast(KnowledgeBaseItem, jsii.invoke(self, "get", [knowledge_base_id]))

    @jsii.member(jsii_name="list")
    def list(self) -> typing.List[KnowledgeBaseItem]:
        '''Retrieves the list of knowledge bases from the xpander.ai API.

        :return: An array of KnowledgeBaseItem instances.

        :throws: Will throw an error if the request fails or the response status code is not in the 2xx range.
        '''
        return typing.cast(typing.List[KnowledgeBaseItem], jsii.invoke(self, "list", []))

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> Configuration:
        '''- Configuration settings for managing knowledge bases.'''
        return typing.cast(Configuration, jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: Configuration) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b22ff5d2628f8ec12d17053d91f6bab123c69072d3226b5a5b47a3f47993ffe2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuration", value) # pyright: ignore[reportArgumentType]


@jsii.enum(jsii_type="xpander-sdk.LLMProvider")
class LLMProvider(enum.Enum):
    '''Enum representing different Large Language Model (LLM) providers.

    This enum lists various LLM service providers integrated with xpanderAI, enabling
    selection of the desired LLM provider for specific tasks.
    '''

    LANG_CHAIN = "LANG_CHAIN"
    '''Represents the 'langchain' provider.'''
    OPEN_AI = "OPEN_AI"
    '''Represents the 'openai' provider.'''
    GEMINI_OPEN_AI = "GEMINI_OPEN_AI"
    '''Represents the 'gemini-openai' provider.'''
    REAL_TIME_OPEN_AI = "REAL_TIME_OPEN_AI"
    '''Represents the 'openai' provider.'''
    NVIDIA_NIM = "NVIDIA_NIM"
    '''Represents the 'nvidiaNim' provider.'''
    AMAZON_BEDROCK = "AMAZON_BEDROCK"
    '''Represents the 'amazonBedrock' provider.'''
    OLLAMA = "OLLAMA"
    '''Represents the 'ollama' provider.'''
    FRIENDLI_AI = "FRIENDLI_AI"
    '''Represents the 'FriendliAI' provider.'''


class LLMTokens(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.LLMTokens"):
    '''Represents token usage statistics for a language model interaction.

    :class: LLMTokens
    :extends: Base

    Example::

        const tokens = new LLMTokens(100, 50, 150);
    '''

    def __init__(
        self,
        completion_tokens: typing.Optional[jsii.Number] = None,
        prompt_tokens: typing.Optional[jsii.Number] = None,
        total_tokens: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param completion_tokens: -
        :param prompt_tokens: -
        :param total_tokens: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e1b070d38acba21af9e85835b7f9505be50edca1af2b7ad290db29d26ba43e1)
            check_type(argname="argument completion_tokens", value=completion_tokens, expected_type=type_hints["completion_tokens"])
            check_type(argname="argument prompt_tokens", value=prompt_tokens, expected_type=type_hints["prompt_tokens"])
            check_type(argname="argument total_tokens", value=total_tokens, expected_type=type_hints["total_tokens"])
        jsii.create(self.__class__, self, [completion_tokens, prompt_tokens, total_tokens])

    @builtins.property
    @jsii.member(jsii_name="completionTokens")
    def completion_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "completionTokens"))

    @completion_tokens.setter
    def completion_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbb7f6dd98655a57ace2277474663dd657f6cee9c3240d690e3ac8f55ac13697)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completionTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="promptTokens")
    def prompt_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "promptTokens"))

    @prompt_tokens.setter
    def prompt_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__840ce298a0bc1fb999a434f981e1e65d101bd12087b3f2612a39bad3edc90613)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "promptTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalTokens")
    def total_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalTokens"))

    @total_tokens.setter
    def total_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c70699746506dd558549f075a6264324f040037434e4d0e45e629d7206702463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalTokens", value) # pyright: ignore[reportArgumentType]


class Memory(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Memory"):
    '''Represents a memory thread in xpanderAI, handling storage, retrieval, and processing of memory messages and related operations.'''

    def __init__(
        self,
        agent: "Agent",
        id: builtins.str,
        messages: typing.Sequence[IMemoryMessage],
        user_details: builtins.str,
        memory_type: "MemoryType",
        metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param agent: -
        :param id: -
        :param messages: -
        :param user_details: -
        :param memory_type: -
        :param metadata: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81920271697ae42e098719be39b49bcd21415f983a883772a893c601ddaee6dd)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument messages", value=messages, expected_type=type_hints["messages"])
            check_type(argname="argument user_details", value=user_details, expected_type=type_hints["user_details"])
            check_type(argname="argument memory_type", value=memory_type, expected_type=type_hints["memory_type"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
        jsii.create(self.__class__, self, [agent, id, messages, user_details, memory_type, metadata])

    @jsii.member(jsii_name="create")
    @builtins.classmethod
    def create(
        cls,
        agent: "Agent",
        user_details: typing.Optional["UserDetails"] = None,
        thread_metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> "Memory":
        '''Creates a new memory thread for the specified agent.

        :param agent: - The agent for which the memory thread is created.
        :param user_details: - Optional user details associated with the memory thread.
        :param thread_metadata: -

        :return: A new instance of the Memory class.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac0cdf9d3941968c7d1fb460252d03479b6f845bc6ba305a0180fce4bcdb71b)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument user_details", value=user_details, expected_type=type_hints["user_details"])
            check_type(argname="argument thread_metadata", value=thread_metadata, expected_type=type_hints["thread_metadata"])
        return typing.cast("Memory", jsii.sinvoke(cls, "create", [agent, user_details, thread_metadata]))

    @jsii.member(jsii_name="deleteThreadById")
    @builtins.classmethod
    def delete_thread_by_id(cls, agent: typing.Any, thread_id: builtins.str) -> None:
        '''Deletes a memory thread by its ID.

        :param agent: - The agent instance containing configuration details.
        :param thread_id: - The ID of the thread to delete.

        :throws: {Error} If the request fails.
        :xpander: .ai
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e7a3cc44823e0bd1074b9528f2bb8474d492df6b5ba552251aee89336e1ef0b)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
        return typing.cast(None, jsii.sinvoke(cls, "deleteThreadById", [agent, thread_id]))

    @jsii.member(jsii_name="fetch")
    @builtins.classmethod
    def fetch(cls, agent: typing.Any, thread_id: builtins.str) -> "Memory":
        '''Fetches an existing memory thread by its ID.

        :param agent: - The agent associated with the memory thread.
        :param thread_id: - The ID of the memory thread to fetch.

        :return: An instance of the Memory class representing the fetched thread.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e2e59e4d3fb03b2220fd16d51c1c03d26c81217aecbc900c19d672d4777df78)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
        return typing.cast("Memory", jsii.sinvoke(cls, "fetch", [agent, thread_id]))

    @jsii.member(jsii_name="fetchUserThreads")
    @builtins.classmethod
    def fetch_user_threads(cls, agent: typing.Any) -> typing.List["MemoryThread"]:
        '''Fetches the memory threads associated with a given agent.

        :param agent: - The agent whose memory threads are to be retrieved.

        :return: - An array of memory threads belonging to the agent.

        :throws: {Error} - Throws an error if the request fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__071fa16b048875d36af2a392e9eff4fa516175617a7f3aae94775da15db152fe)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
        return typing.cast(typing.List["MemoryThread"], jsii.sinvoke(cls, "fetchUserThreads", [agent]))

    @jsii.member(jsii_name="renameThreadById")
    @builtins.classmethod
    def rename_thread_by_id(
        cls,
        agent: typing.Any,
        thread_id: builtins.str,
        name: builtins.str,
    ) -> None:
        '''Renames a memory thread by its ID.

        :param agent: - The agent instance containing configuration details.
        :param thread_id: - The ID of the thread to rename.
        :param name: - The new name for the thread.

        :throws: {Error} If the request fails.
        :xpander: .ai
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba863dd52fe282ca9d0689fe6f56343e5b24266d122c7bc67f845d1680d79f4)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast(None, jsii.sinvoke(cls, "renameThreadById", [agent, thread_id, name]))

    @jsii.member(jsii_name="update")
    @builtins.classmethod
    def update(
        cls,
        agent: "Agent",
        thread_id: builtins.str,
        delta: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> "Memory":
        '''Updates an existing memory thread for a specified agent.

        Sends a PATCH request to the agent's memory endpoint to update an existing thread
        with the provided ``delta`` object. The updated thread is returned as a new
        instance of the ``Memory`` class.

        :param agent: - The agent for which the memory thread should be updated. Must contain valid configuration including ``url`` and ``apiKey``.
        :param thread_id: - The unique identifier of the memory thread to update.
        :param delta: - Optional object containing the fields and values to update in the memory thread.

        :return: A new instance of the ``Memory`` class representing the updated thread.

        :throws: Error - Throws if the server response status code is not successful (non-2xx).

        Example::

            const memory = Memory.update(agent, 'thread-id-123', { status: 'active' });
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3b9699df3510508554ad78d3dbc8cdcdf487a52850c8d30148c0a56992f7092)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument delta", value=delta, expected_type=type_hints["delta"])
        return typing.cast("Memory", jsii.sinvoke(cls, "update", [agent, thread_id, delta]))

    @jsii.member(jsii_name="addKnowledgeBase")
    def add_knowledge_base(self) -> None:
        return typing.cast(None, jsii.invoke(self, "addKnowledgeBase", []))

    @jsii.member(jsii_name="addMessages")
    def add_messages(self, _messages: typing.Any) -> None:
        '''Adds messages to the memory thread.

        Converts non-standard messages to a compatible format before storing.

        :param _messages: - An array of messages to be added to the memory thread.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a51857d33f65b0aeb1e47a32821416678e02e9977e28bcf191def00e1de1385)
            check_type(argname="argument _messages", value=_messages, expected_type=type_hints["_messages"])
        return typing.cast(None, jsii.invoke(self, "addMessages", [_messages]))

    @jsii.member(jsii_name="addToolCallResults")
    def add_tool_call_results(
        self,
        tool_call_results: typing.Sequence["ToolCallResult"],
    ) -> None:
        '''Adds tool call results as messages to the memory thread.

        :param tool_call_results: - An array of tool call results to be added as messages.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__371bbac48ab4303b8878745ba398512a7e9b2282fcdf6e8b9dd183b48b03488e)
            check_type(argname="argument tool_call_results", value=tool_call_results, expected_type=type_hints["tool_call_results"])
        return typing.cast(None, jsii.invoke(self, "addToolCallResults", [tool_call_results]))

    @jsii.member(jsii_name="initInstructions")
    def init_instructions(self, instructions: "AgentInstructions") -> None:
        '''Initializes the memory thread with system instructions if no messages exist.

        :param instructions: - Instructions to initialize the memory thread.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce51eb3bc0f66424dc100907e6b8645a78f014da089334b5683929638780555)
            check_type(argname="argument instructions", value=instructions, expected_type=type_hints["instructions"])
        return typing.cast(None, jsii.invoke(self, "initInstructions", [instructions]))

    @jsii.member(jsii_name="initMessages")
    def init_messages(
        self,
        input: IMemoryMessage,
        instructions: "AgentInstructions",
        llm_provider: typing.Optional[LLMProvider] = None,
        files: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Initializes the thread with input and instructions.

        :param input: - Initial user input message.
        :param instructions: - Instructions to initialize the memory thread.
        :param llm_provider: -
        :param files: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3820bd4aa216fc45c11762598045b405bfcb54d55efafa184a988ea86af9191c)
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument instructions", value=instructions, expected_type=type_hints["instructions"])
            check_type(argname="argument llm_provider", value=llm_provider, expected_type=type_hints["llm_provider"])
            check_type(argname="argument files", value=files, expected_type=type_hints["files"])
        return typing.cast(None, jsii.invoke(self, "initMessages", [input, instructions, llm_provider, files]))

    @jsii.member(jsii_name="retrieveMessages")
    def retrieve_messages(self) -> typing.List[typing.Any]:
        '''Retrieves the messages stored in the memory thread.

        Applies the agent's memory strategy to refresh the messages if needed.

        :return: An array of messages formatted for the selected LLM provider.
        '''
        return typing.cast(typing.List[typing.Any], jsii.invoke(self, "retrieveMessages", []))

    @jsii.member(jsii_name="updateMessages")
    def update_messages(self, _messages: typing.Any) -> None:
        '''Updates the message history for the agent by sending the provided messages to the server.

        If the messages are not in the expected "xpander.ai" message format, they are converted.

        :param _messages: - The messages to be updated. Can be in various formats. If not in the "xpander.ai" format, they will be converted.

        :throws: {Error} - Throws an error if the request to update messages fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43486da039b91b09744e42b7b31901476e80049c84ef6f5a1e8c12946e5fca9a)
            check_type(argname="argument _messages", value=_messages, expected_type=type_hints["_messages"])
        return typing.cast(None, jsii.invoke(self, "updateMessages", [_messages]))

    @builtins.property
    @jsii.member(jsii_name="systemMessage")
    def system_message(self) -> typing.List[typing.Any]:
        return typing.cast(typing.List[typing.Any], jsii.get(self, "systemMessage"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbe18b88e2660e8696c14f8f8e6d7a160be4e10f351309c88ad1ef59993830d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="llmProvider")
    def llm_provider(self) -> LLMProvider:
        '''The LLM provider to be used for message processing.'''
        return typing.cast(LLMProvider, jsii.get(self, "llmProvider"))

    @llm_provider.setter
    def llm_provider(self, value: LLMProvider) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__480c9de0d56a727b6080606ffa19389e9a950f96e37f7f9a97200fd43981ce7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "llmProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryType")
    def memory_type(self) -> "MemoryType":
        return typing.cast("MemoryType", jsii.get(self, "memoryType"))

    @memory_type.setter
    def memory_type(self, value: "MemoryType") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b4f084a61d1e17795026fdf0d8050b34b2f09eea03d6dfbb5809384ca99e18c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messages")
    def messages(self) -> typing.List[IMemoryMessage]:
        return typing.cast(typing.List[IMemoryMessage], jsii.get(self, "messages"))

    @messages.setter
    def messages(self, value: typing.List[IMemoryMessage]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__061b6a073f962d6437ad5fafa99b961231c85f17625aa93e208f2ab144777953)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c32eb529c2827d1d2d5e8eafc00e7e04a06df1f90b3e6d59b9a6ca51e3c2f77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userDetails")
    def user_details(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userDetails"))

    @user_details.setter
    def user_details(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e929e79b7b59a892685c04ee233be1c732bd06c519447292cd87e096540451a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userDetails", value) # pyright: ignore[reportArgumentType]


@jsii.enum(jsii_type="xpander-sdk.MemoryStrategy")
class MemoryStrategy(enum.Enum):
    FULL = "FULL"
    SUMMARIZATION = "SUMMARIZATION"
    BUFFERING = "BUFFERING"
    MOVING_WINDOW = "MOVING_WINDOW"
    CONTEXT = "CONTEXT"
    CLEAN_TOOL_CALLS = "CLEAN_TOOL_CALLS"


class MemoryThread(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.MemoryThread"):
    def __init__(
        self,
        id: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param id: -
        :param created_at: -
        :param name: -
        :param metadata: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02fc4d33a917e0e6da8b5cedc5b5080dd3e329d0f585c0df82a28bed9dffacb4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
        jsii.create(self.__class__, self, [id, created_at, name, metadata])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__351136a3c6205f7a6ca7271ab89aad37aacb8db2760c9193ab183f176568cf3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d98421cc7fa1aaa0659076e6f9368e1832f4c5e26a01072da4049125970ce3eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Mapping[builtins.str, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc2b13099f398ab092fae2f0168bb07bb9f7d8bec9f1d7da95a4675d1a787bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c7828f395f2671c9dc6587ce6ced2e48ec9fd11f89af3abbaa88d27472962b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.enum(jsii_type="xpander-sdk.MemoryType")
class MemoryType(enum.Enum):
    LONG_TERM = "LONG_TERM"
    SHORT_TERM = "SHORT_TERM"


class MetricsBase(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.MetricsBase"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="report")
    def report(self, agent: "Agent", report_type: builtins.str) -> None:
        '''
        :param agent: -
        :param report_type: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f94fa5a937bc0bc1bcaa5ec59fd11112a5478a8d1b1dd6aef138b9d0d30a30f7)
            check_type(argname="argument agent", value=agent, expected_type=type_hints["agent"])
            check_type(argname="argument report_type", value=report_type, expected_type=type_hints["report_type"])
        return typing.cast(None, jsii.invoke(self, "report", [agent, report_type]))


@jsii.enum(jsii_type="xpander-sdk.SourceNodeType")
class SourceNodeType(enum.Enum):
    '''Enum representing different source node types for agents.'''

    SDK = "SDK"
    TASK = "TASK"
    ASSISTANT = "ASSISTANT"
    WEBHOOK = "WEBHOOK"


class Tokens(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Tokens"):
    '''Encapsulates token usage for different components of a task, typically an internal process and a worker/agent execution.

    :class: Tokens
    :extends: Base

    Example::

        const tokens = new Tokens(
          new LLMTokens(30, 20, 50),
          new LLMTokens(80, 40, 120)
        );
    '''

    def __init__(
        self,
        inner: typing.Optional[LLMTokens] = None,
        worker: typing.Optional[LLMTokens] = None,
    ) -> None:
        '''
        :param inner: -
        :param worker: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd35ef6de1c9651bc7d151f4efc8c1f0db15088148591bc019d5cea3dd7a8bc2)
            check_type(argname="argument inner", value=inner, expected_type=type_hints["inner"])
            check_type(argname="argument worker", value=worker, expected_type=type_hints["worker"])
        jsii.create(self.__class__, self, [inner, worker])

    @builtins.property
    @jsii.member(jsii_name="inner")
    def inner(self) -> LLMTokens:
        return typing.cast(LLMTokens, jsii.get(self, "inner"))

    @inner.setter
    def inner(self, value: LLMTokens) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b3c2c0548517a31cc05aa0d6e475ade9f2a9dec96fd9a34d4bc3edbdabbd7d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="worker")
    def worker(self) -> LLMTokens:
        return typing.cast(LLMTokens, jsii.get(self, "worker"))

    @worker.setter
    def worker(self, value: LLMTokens) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__298b6757d19c9f36a1df243177e78409e0c8bed0b905c0ebcaadf9a658276b48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "worker", value) # pyright: ignore[reportArgumentType]


class ToolCall(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.ToolCall"):
    '''Represents a tool call with its metadata and payload.

    :class: ToolCall
    :extends: Base *
    :memberof: xpander.ai
    '''

    def __init__(
        self,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional["ToolCallType"] = None,
        payload: typing.Any = None,
        tool_call_id: typing.Optional[builtins.str] = None,
        graph_approved: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param name: -
        :param type: -
        :param payload: -
        :param tool_call_id: -
        :param graph_approved: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5b1512c48e4c0a4b618d417e46f7c83b02989356f2412aa0eae9d63b626ce0e)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument tool_call_id", value=tool_call_id, expected_type=type_hints["tool_call_id"])
            check_type(argname="argument graph_approved", value=graph_approved, expected_type=type_hints["graph_approved"])
        jsii.create(self.__class__, self, [name, type, payload, tool_call_id, graph_approved])

    @builtins.property
    @jsii.member(jsii_name="graphApproved")
    def graph_approved(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "graphApproved"))

    @graph_approved.setter
    def graph_approved(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fa618f493b9f124cef109e56d0f709f1b78016dbeb7ed55a9eb8cdc733dba99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "graphApproved", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7cce041752b4e95ae25466ea39d32f51ec0301e64015b66ccf20bb9b23db25e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="payload")
    def payload(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "payload"))

    @payload.setter
    def payload(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1940e09fdc14592acfce7003f99bcc770eb4b17ea62e53e30d6cbfd4d3d3707)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payload", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolCallId")
    def tool_call_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "toolCallId"))

    @tool_call_id.setter
    def tool_call_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d9b994824033489cb2b3b806044405bcb06c1d72048f017c89bb422b16b35e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolCallId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "ToolCallType":
        return typing.cast("ToolCallType", jsii.get(self, "type"))

    @type.setter
    def type(self, value: "ToolCallType") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2059ec549c7384dd73be7be379faf6256c60a8ec7b55fdb9082692bbdc4bac54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


class ToolCallResult(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.ToolCallResult",
):
    '''Represents the result of a tool call execution.

    :class: ToolCallResult
    :extends: Base *
    :memberof: xpander.ai
    '''

    def __init__(
        self,
        function_name: typing.Optional[builtins.str] = None,
        tool_call_id: typing.Optional[builtins.str] = None,
        payload: typing.Any = None,
        status_code: typing.Optional[jsii.Number] = None,
        result: typing.Any = None,
        is_success: typing.Optional[builtins.bool] = None,
        is_error: typing.Optional[builtins.bool] = None,
        is_local: typing.Optional[builtins.bool] = None,
        graph_approved: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param function_name: -
        :param tool_call_id: -
        :param payload: -
        :param status_code: -
        :param result: -
        :param is_success: -
        :param is_error: -
        :param is_local: -
        :param graph_approved: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2debc725768136a46976eacab873877fdcc3efbb47c357e0973193213896e283)
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
            check_type(argname="argument tool_call_id", value=tool_call_id, expected_type=type_hints["tool_call_id"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument status_code", value=status_code, expected_type=type_hints["status_code"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
            check_type(argname="argument is_success", value=is_success, expected_type=type_hints["is_success"])
            check_type(argname="argument is_error", value=is_error, expected_type=type_hints["is_error"])
            check_type(argname="argument is_local", value=is_local, expected_type=type_hints["is_local"])
            check_type(argname="argument graph_approved", value=graph_approved, expected_type=type_hints["graph_approved"])
        jsii.create(self.__class__, self, [function_name, tool_call_id, payload, status_code, result, is_success, is_error, is_local, graph_approved])

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fffc9823e52bc6b5b2f4aa72f7ed94614aad7d55b77f29de8574547aa73f28f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="graphApproved")
    def graph_approved(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "graphApproved"))

    @graph_approved.setter
    def graph_approved(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d03c735e160319bb8f7ff2043b62a07dc4ac091a1eb43c315b5be4128fcf92a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "graphApproved", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isError")
    def is_error(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isError"))

    @is_error.setter
    def is_error(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e12e85757c6557cdf77248e76a660df04102b8873b38236827fb882d1fa6439a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isError", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isLocal")
    def is_local(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isLocal"))

    @is_local.setter
    def is_local(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6923af36e794b8a5e685b7b5409aa9d63e048e0dde8cd5691e95250ecc939bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isLocal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSuccess")
    def is_success(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isSuccess"))

    @is_success.setter
    def is_success(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e0ae8339ae925874f36d96caaf593a776e69a5def415e6cd597660d7e9c011e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSuccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="payload")
    def payload(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "payload"))

    @payload.setter
    def payload(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2de087a3432f7b811bf4e98dd110380b61cb2d0cdcd014af55ea9c493c5e516)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payload", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="result")
    def result(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "result"))

    @result.setter
    def result(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b512e8cc2e3d13362bf29e552b8dff26b147cd4cf7b3fc2ac09efd5bd6e5bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "result", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d7de4c43b1bcc39cb1dbd154a581a3c2a35f429555b50d12f81d0c6662c787a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statusCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="toolCallId")
    def tool_call_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "toolCallId"))

    @tool_call_id.setter
    def tool_call_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e548be6ee41a966ad4e21e38458b2dc18fde679b9017e65e4f088b5b0d8c3580)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "toolCallId", value) # pyright: ignore[reportArgumentType]


@jsii.enum(jsii_type="xpander-sdk.ToolCallType")
class ToolCallType(enum.Enum):
    '''Enum representing types of tool calls.'''

    XPANDER = "XPANDER"
    LOCAL = "LOCAL"


class UnloadedAgent(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.UnloadedAgent",
):
    '''Represents an unloaded agent in the xpander.ai system. Used to reference agents that are not yet fully loaded.'''

    def __init__(
        self,
        configuration: Configuration,
        id: builtins.str,
        name: builtins.str,
        status: AgentStatus,
        organization_id: builtins.str,
    ) -> None:
        '''Creates a new UnloadedAgent instance.

        :param configuration: - The configuration instance used for loading the agent.
        :param id: - The unique identifier of the agent.
        :param name: - The name of the agent.
        :param status: - The current status of the agent.
        :param organization_id: - The ID of the organization to which the agent belongs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ad0f4ee2a8ddc83f945f89e3e6d713c8feaf7a7396b6b0435b3d8b01dbcd30d)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
        jsii.create(self.__class__, self, [configuration, id, name, status, organization_id])

    @jsii.member(jsii_name="load")
    def load(self) -> "Agent":
        '''Loads the full Agent instance from the xpander.ai system using its ID.

        :return: The fully loaded Agent instance.
        '''
        return typing.cast("Agent", jsii.invoke(self, "load", []))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''- The unique identifier of the agent.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be6af203e065a2e78c58c607874e4f2b9549d01bf66e0c563b5608336cef17cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''- The name of the agent.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a97a3b5f071d297b2aac0ac9cd726e2808c590639e3d4ef730ebb20756c9ec7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''- The ID of the organization to which the agent belongs.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6027724ba7ab5ddecadd02d711569a0a4806fb8d2f046ecc2c2c7de68ce56b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> AgentStatus:
        '''- The current status of the agent.'''
        return typing.cast(AgentStatus, jsii.get(self, "status"))

    @status.setter
    def status(self, value: AgentStatus) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9d4d1b15e40e35739183c3453f29a7c40b620d1efc759a89e3b8c4de7de7541)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]


class UserDetails(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.UserDetails"):
    def __init__(
        self,
        id: builtins.str,
        first_name: typing.Optional[builtins.str] = None,
        last_name: typing.Optional[builtins.str] = None,
        email: typing.Optional[builtins.str] = None,
        additional_attributes: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param id: -
        :param first_name: -
        :param last_name: -
        :param email: -
        :param additional_attributes: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7329314fccee5b9ac6ae21377aed20b3b58b8e4362fdaaf73481b787b7e9ccb1)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument first_name", value=first_name, expected_type=type_hints["first_name"])
            check_type(argname="argument last_name", value=last_name, expected_type=type_hints["last_name"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument additional_attributes", value=additional_attributes, expected_type=type_hints["additional_attributes"])
        jsii.create(self.__class__, self, [id, first_name, last_name, email, additional_attributes])

    @builtins.property
    @jsii.member(jsii_name="additionalAttributes")
    def additional_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "additionalAttributes"))

    @additional_attributes.setter
    def additional_attributes(
        self,
        value: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f6ada61e6a476091ed3b896af2bb30412b2b21546fc1ec5dc82eced56299576)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ef5a82a2d4441cfe90fc0bba0711ecdcc126060fa2f12156f85a20ffb451f40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "email", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firstName")
    def first_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firstName"))

    @first_name.setter
    def first_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cc2c69cac56a0d499cc6b3fe05b85180c760de9596f0d95fa23899dacc67bc3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firstName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63911c605dfb76017dd111da3d0eb2759d4281365e645a3f6be942b03ef98003)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastName")
    def last_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastName"))

    @last_name.setter
    def last_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5446210d9c39a301ae2ac61861be554ae17304401c3de63f874241cda248e456)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastName", value) # pyright: ignore[reportArgumentType]


class XpanderClient(metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.XpanderClient"):
    '''XpanderClient provides methods for configuring and interacting with xpanderAI tools, managing agents, and extracting tool calls from LLM responses.'''

    def __init__(
        self,
        api_key: builtins.str,
        base_url: typing.Any = None,
        organization_id: typing.Optional[builtins.str] = None,
        should_reset_cache: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new XpanderClient instance.

        :param api_key: -
        :param base_url: -
        :param organization_id: -
        :param should_reset_cache: -

        :throws: Will throw an error if an invalid API key is specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ada04f0df01e9b462e0b973aee5f69eda17ab0f22e7345f33423f0acca9ad36)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument should_reset_cache", value=should_reset_cache, expected_type=type_hints["should_reset_cache"])
        jsii.create(self.__class__, self, [api_key, base_url, organization_id, should_reset_cache])

    @jsii.member(jsii_name="extractToolCalls")
    @builtins.classmethod
    def extract_tool_calls(
        cls,
        llm_response: typing.Any,
        llm_provider: typing.Optional[LLMProvider] = None,
    ) -> typing.List[ToolCall]:
        '''Extracts tool calls from an LLM response based on the specified LLM provider.

        :param llm_response: - The LLM response to analyze for tool calls.
        :param llm_provider: - The LLM provider, defaults to OPEN_AI.

        :return: An array of tool calls extracted from the LLM response.

        :throws: Error if the specified LLM provider is not supported.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d89a5c88d1a2ed62ab765c38358d4adda81980f27657e34b4fe23fc61eca9217)
            check_type(argname="argument llm_response", value=llm_response, expected_type=type_hints["llm_response"])
            check_type(argname="argument llm_provider", value=llm_provider, expected_type=type_hints["llm_provider"])
        return typing.cast(typing.List[ToolCall], jsii.sinvoke(cls, "extractToolCalls", [llm_response, llm_provider]))

    @jsii.member(jsii_name="retrievePendingLocalToolCalls")
    @builtins.classmethod
    def retrieve_pending_local_tool_calls(
        cls,
        tool_calls: typing.Sequence[ToolCall],
    ) -> typing.List[ToolCall]:
        '''Filters and retrieves local tool calls from a given list of tool calls.

        :param tool_calls: - The list of tool calls to filter.

        :return: An array of tool calls that are of type LOCAL.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f435d83beaf0c0d7ba5fac4b14d448f0cd185e5af1d9aff81d5cfc4147374b61)
            check_type(argname="argument tool_calls", value=tool_calls, expected_type=type_hints["tool_calls"])
        return typing.cast(typing.List[ToolCall], jsii.sinvoke(cls, "retrievePendingLocalToolCalls", [tool_calls]))

    @builtins.property
    @jsii.member(jsii_name="agents")
    def agents(self) -> Agents:
        '''Instance of Agents to manage xpanderAI agents.'''
        return typing.cast(Agents, jsii.get(self, "agents"))

    @agents.setter
    def agents(self, value: Agents) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50de96ce44613a7f9044134d55c384c9cbc69918873535eed55a2d9c1f2cafbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> Configuration:
        '''Configuration settings for the xpanderAI client.'''
        return typing.cast(Configuration, jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: Configuration) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f24bf46a0a96d6e069bcfdce151aa22264da15a80125c376dbad457bf91d1c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="knowledgeBases")
    def knowledge_bases(self) -> KnowledgeBases:
        '''Instance of Knowledgebases to manage xpanderAI knowledge bases.'''
        return typing.cast(KnowledgeBases, jsii.get(self, "knowledgeBases"))

    @knowledge_bases.setter
    def knowledge_bases(self, value: KnowledgeBases) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b3090998ec2c8bf3ca3548a14caaf6de4971b4c774603a66cee58c84379ce22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knowledgeBases", value) # pyright: ignore[reportArgumentType]


class Agent(Base, metaclass=jsii.JSIIMeta, jsii_type="xpander-sdk.Agent"):
    '''Represents an agent in xpanderAI, managing tools, sessions, and operational workflows.

    This class facilitates loading agents, handling tool executions, and managing prompt groups.
    '''

    def __init__(
        self,
        configuration: Configuration,
        id: builtins.str,
        name: builtins.str,
        organization_id: builtins.str,
        status: AgentStatus,
        delegation_type: AgentDelegationType,
        delegation_end_strategy: AgentDelegationEndStrategy,
        memory_type: MemoryType,
        memory_strategy: MemoryStrategy,
        instructions: "AgentInstructions",
        access_scope: AgentAccessScope,
        source_nodes: typing.Sequence[ISourceNode],
        prompts: typing.Sequence[builtins.str],
        tools: typing.Optional[typing.Sequence[IAgentTool]] = None,
        _graph: typing.Optional[typing.Sequence[typing.Any]] = None,
        knowledge_bases: typing.Optional[typing.Sequence[KnowledgeBase]] = None,
        oas: typing.Any = None,
        version: typing.Any = None,
    ) -> None:
        '''Constructs a new Agent instance.

        :param configuration: - Configuration settings for the agent.
        :param id: - Unique identifier for the agent.
        :param name: - Human-readable name of the agent.
        :param organization_id: - Organization ID to which the agent belongs.
        :param status: - Current status of the agent.
        :param delegation_type: - The agent's delegation type (Router/Sequence).
        :param delegation_end_strategy: -
        :param memory_type: - Type of memory the agent utilizes.
        :param memory_strategy: - Strategy for memory management.
        :param instructions: - Instructions for the agent's operation.
        :param access_scope: - Scope of the agent's access permissions.
        :param source_nodes: - Source nodes associated with the agent.
        :param prompts: - Prompts used by the agent.
        :param tools: - Tools available to the agent.
        :param _graph: -
        :param knowledge_bases: - Knowledge bases associated with the agent.
        :param oas: -
        :param version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed3ca6ba27cec860aa869deb2eaf5d80822747214c50652c074c1fd995c12295)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument delegation_type", value=delegation_type, expected_type=type_hints["delegation_type"])
            check_type(argname="argument delegation_end_strategy", value=delegation_end_strategy, expected_type=type_hints["delegation_end_strategy"])
            check_type(argname="argument memory_type", value=memory_type, expected_type=type_hints["memory_type"])
            check_type(argname="argument memory_strategy", value=memory_strategy, expected_type=type_hints["memory_strategy"])
            check_type(argname="argument instructions", value=instructions, expected_type=type_hints["instructions"])
            check_type(argname="argument access_scope", value=access_scope, expected_type=type_hints["access_scope"])
            check_type(argname="argument source_nodes", value=source_nodes, expected_type=type_hints["source_nodes"])
            check_type(argname="argument prompts", value=prompts, expected_type=type_hints["prompts"])
            check_type(argname="argument tools", value=tools, expected_type=type_hints["tools"])
            check_type(argname="argument _graph", value=_graph, expected_type=type_hints["_graph"])
            check_type(argname="argument knowledge_bases", value=knowledge_bases, expected_type=type_hints["knowledge_bases"])
            check_type(argname="argument oas", value=oas, expected_type=type_hints["oas"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        jsii.create(self.__class__, self, [configuration, id, name, organization_id, status, delegation_type, delegation_end_strategy, memory_type, memory_strategy, instructions, access_scope, source_nodes, prompts, tools, _graph, knowledge_bases, oas, version])

    @jsii.member(jsii_name="getById")
    @builtins.classmethod
    def get_by_id(
        cls,
        configuration: Configuration,
        agent_id: builtins.str,
        version: typing.Optional[jsii.Number] = None,
    ) -> "Agent":
        '''
        :param configuration: -
        :param agent_id: -
        :param version: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76b6cdc7eb3f36024a9c7754118375ea2bc37265acbea46b1152c2be8dc1072d)
            check_type(argname="argument configuration", value=configuration, expected_type=type_hints["configuration"])
            check_type(argname="argument agent_id", value=agent_id, expected_type=type_hints["agent_id"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        return typing.cast("Agent", jsii.sinvoke(cls, "getById", [configuration, agent_id, version]))

    @jsii.member(jsii_name="addLocalTools")
    def add_local_tools(
        self,
        tools: typing.Union[typing.Sequence[typing.Any], typing.Sequence[ILocalTool]],
    ) -> None:
        '''Adds local tools to the agent with prefixed function names.

        :param tools: - The list of local tools to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1a4e9d238bcd6575542fe126282fe717dabbed97bd4b5d5f0906439f6debd49)
            check_type(argname="argument tools", value=tools, expected_type=type_hints["tools"])
        return typing.cast(None, jsii.invoke(self, "addLocalTools", [tools]))

    @jsii.member(jsii_name="addMessages")
    def add_messages(self, messages: typing.Any) -> None:
        '''Adds messages to the memory thread.

        Converts non-standard messages to a compatible format before storing.

        :param messages: - An array of messages to be added to the memory thread.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c763e76e4ecb7f7a77fe6c2dba333b644ea0abddac2e6c51dcad464709b85e)
            check_type(argname="argument messages", value=messages, expected_type=type_hints["messages"])
        return typing.cast(None, jsii.invoke(self, "addMessages", [messages]))

    @jsii.member(jsii_name="addTask")
    def add_task(
        self,
        input: typing.Optional[builtins.str] = None,
        thread_id: typing.Optional[builtins.str] = None,
        files: typing.Optional[typing.Sequence[builtins.str]] = None,
        use_worker: typing.Optional[builtins.bool] = None,
    ) -> Execution:
        '''
        :param input: -
        :param thread_id: -
        :param files: -
        :param use_worker: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d16546c5c195ddef4391e46da78707938e8cd6d85040e33d40bc00a7120446e)
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument thread_id", value=thread_id, expected_type=type_hints["thread_id"])
            check_type(argname="argument files", value=files, expected_type=type_hints["files"])
            check_type(argname="argument use_worker", value=use_worker, expected_type=type_hints["use_worker"])
        return typing.cast(Execution, jsii.invoke(self, "addTask", [input, thread_id, files, use_worker]))

    @jsii.member(jsii_name="addToolCallResults")
    def add_tool_call_results(
        self,
        tool_call_results: typing.Sequence[ToolCallResult],
    ) -> None:
        '''Adds tool call results as messages to the memory thread.

        :param tool_call_results: - An array of tool call results to be added as messages.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b6b5a079da787d90c8d00f39c55c743d24f5ed3b67480566451861a7cd9ec9)
            check_type(argname="argument tool_call_results", value=tool_call_results, expected_type=type_hints["tool_call_results"])
        return typing.cast(None, jsii.invoke(self, "addToolCallResults", [tool_call_results]))

    @jsii.member(jsii_name="attachOperations")
    def attach_operations(
        self,
        operations: typing.Sequence["AgenticOperation"],
    ) -> None:
        '''Attaches a list of agentic operations to the agent.

        :param operations: - The list of agentic operations to attach.

        :memberof: xpander.ai
        :throws: {Error} If the attachment process fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__714c96a4dcb9157921296811cd8edcf9f84bf337706dac7c155320ff730bcbf2)
            check_type(argname="argument operations", value=operations, expected_type=type_hints["operations"])
        return typing.cast(None, jsii.invoke(self, "attachOperations", [operations]))

    @jsii.member(jsii_name="disableAgentEndTool")
    def disable_agent_end_tool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "disableAgentEndTool", []))

    @jsii.member(jsii_name="enableAgentEndTool")
    def enable_agent_end_tool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "enableAgentEndTool", []))

    @jsii.member(jsii_name="extractToolCalls")
    def extract_tool_calls(self, llm_response: typing.Any) -> typing.List[ToolCall]:
        '''Extracts tool calls from an LLM response based on the specified LLM provider.

        :param llm_response: - The LLM response to analyze for tool calls.

        :return: An array of tool calls extracted from the LLM response.

        :throws: Error if the specified LLM provider is not supported.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3052afdc5d1b5b60445cf51a8879fbae2c027aae54558102a8ddab28b0963d8a)
            check_type(argname="argument llm_response", value=llm_response, expected_type=type_hints["llm_response"])
        return typing.cast(typing.List[ToolCall], jsii.invoke(self, "extractToolCalls", [llm_response]))

    @jsii.member(jsii_name="getTools")
    def get_tools(
        self,
        llm_provider: typing.Optional[LLMProvider] = None,
    ) -> typing.List[typing.Any]:
        '''Retrieves tools compatible with a specified LLM provider.

        :param llm_provider: - The LLM provider to filter tools by (default: ``OPEN_AI``).

        :return: A list of tools matching the specified provider.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__773e3afa26f8b79fe00973c69c9983fbf523bfd2f52c02c0a473df8878934452)
            check_type(argname="argument llm_provider", value=llm_provider, expected_type=type_hints["llm_provider"])
        return typing.cast(typing.List[typing.Any], jsii.invoke(self, "getTools", [llm_provider]))

    @jsii.member(jsii_name="initTask")
    def init_task(self, execution: typing.Any) -> None:
        '''Initializes the task execution for the agent.

        :param execution: - The execution details.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16872029ef2ca9a4aea1671c278ba6987a5be977e7311f29693d64313ecee69b)
            check_type(argname="argument execution", value=execution, expected_type=type_hints["execution"])
        return typing.cast(None, jsii.invoke(self, "initTask", [execution]))

    @jsii.member(jsii_name="isFinished")
    def is_finished(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isFinished", []))

    @jsii.member(jsii_name="load")
    def load(
        self,
        agent_id: typing.Optional[builtins.str] = None,
        ignore_cache: typing.Optional[builtins.bool] = None,
        raw_agent_data: typing.Any = None,
    ) -> None:
        '''Loads the agent data from its source node type.

        :param agent_id: -
        :param ignore_cache: -
        :param raw_agent_data: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__083e27f1b35697c0dc5dd7bec052ea93d4a2fd3d2ee05d66ed6dfd7754537ddb)
            check_type(argname="argument agent_id", value=agent_id, expected_type=type_hints["agent_id"])
            check_type(argname="argument ignore_cache", value=ignore_cache, expected_type=type_hints["ignore_cache"])
            check_type(argname="argument raw_agent_data", value=raw_agent_data, expected_type=type_hints["raw_agent_data"])
        return typing.cast(None, jsii.invoke(self, "load", [agent_id, ignore_cache, raw_agent_data]))

    @jsii.member(jsii_name="reportExecutionMetrics")
    def report_execution_metrics(
        self,
        llm_tokens: Tokens,
        ai_model: typing.Optional[builtins.str] = None,
        source_node_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param llm_tokens: -
        :param ai_model: -
        :param source_node_type: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4315e33d477848f207013139088ddfe589c01ac5fe3ac40fe3887eda68a8c81)
            check_type(argname="argument llm_tokens", value=llm_tokens, expected_type=type_hints["llm_tokens"])
            check_type(argname="argument ai_model", value=ai_model, expected_type=type_hints["ai_model"])
            check_type(argname="argument source_node_type", value=source_node_type, expected_type=type_hints["source_node_type"])
        return typing.cast(None, jsii.invoke(self, "reportExecutionMetrics", [llm_tokens, ai_model, source_node_type]))

    @jsii.member(jsii_name="reportLlmUsage")
    def report_llm_usage(
        self,
        llm_response: typing.Any,
        llm_inference_duration: typing.Optional[jsii.Number] = None,
        llm_provider: typing.Optional[LLMProvider] = None,
        source_node_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param llm_response: -
        :param llm_inference_duration: -
        :param llm_provider: -
        :param source_node_type: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a96e0f5f5b59da335f12b0146213acc128807a6c3137a890fed7ed76a04562)
            check_type(argname="argument llm_response", value=llm_response, expected_type=type_hints["llm_response"])
            check_type(argname="argument llm_inference_duration", value=llm_inference_duration, expected_type=type_hints["llm_inference_duration"])
            check_type(argname="argument llm_provider", value=llm_provider, expected_type=type_hints["llm_provider"])
            check_type(argname="argument source_node_type", value=source_node_type, expected_type=type_hints["source_node_type"])
        return typing.cast(None, jsii.invoke(self, "reportLlmUsage", [llm_response, llm_inference_duration, llm_provider, source_node_type]))

    @jsii.member(jsii_name="retrieveAgenticInterfaces")
    def retrieve_agentic_interfaces(
        self,
        ignore_cache: typing.Optional[builtins.bool] = None,
    ) -> typing.List["AgenticInterface"]:
        '''Retrieves a list of available agentic interfaces.

        :param ignore_cache: - Whether to ignore cached data and fetch fresh data.

        :return: A list of agentic interfaces.

        :memberof: xpander.ai
        :throws: {Error} If retrieval fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0958d9b6b5bfc800ebaa305539fc9dcd3ddf83cfd3fd110883c1698d297f6349)
            check_type(argname="argument ignore_cache", value=ignore_cache, expected_type=type_hints["ignore_cache"])
        return typing.cast(typing.List["AgenticInterface"], jsii.invoke(self, "retrieveAgenticInterfaces", [ignore_cache]))

    @jsii.member(jsii_name="retrieveAgenticOperations")
    def retrieve_agentic_operations(
        self,
        agentic_interface: "AgenticInterface",
        ignore_cache: typing.Optional[builtins.bool] = None,
    ) -> typing.List["AgenticOperation"]:
        '''Retrieves a list of operations for a given agentic interface.

        :param agentic_interface: - The agentic interface to retrieve operations for.
        :param ignore_cache: - Whether to ignore cached data and fetch fresh data.

        :return: A list of agentic operations.

        :memberof: xpander.ai
        :throws: {Error} If retrieval fails.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b9086ebd87942a70c9515c8974e8d9cab5772e11bb9fcb24a227d204d9923f9)
            check_type(argname="argument agentic_interface", value=agentic_interface, expected_type=type_hints["agentic_interface"])
            check_type(argname="argument ignore_cache", value=ignore_cache, expected_type=type_hints["ignore_cache"])
        return typing.cast(typing.List["AgenticOperation"], jsii.invoke(self, "retrieveAgenticOperations", [agentic_interface, ignore_cache]))

    @jsii.member(jsii_name="retrieveExecutionResult")
    def retrieve_execution_result(self) -> Execution:
        return typing.cast(Execution, jsii.invoke(self, "retrieveExecutionResult", []))

    @jsii.member(jsii_name="retrieveNodeFromGraph")
    def retrieve_node_from_graph(
        self,
        item_id: builtins.str,
    ) -> typing.Optional[GraphItem]:
        '''Retrieves a node from the graph by its ID.

        :param item_id: - The ID of the graph node to retrieve.

        :return: The matching graph node, or undefined if not found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b76974a0e120e8cf7b77d0deb9b609235bfbb31f7bb65ad41e928422ab50a6b3)
            check_type(argname="argument item_id", value=item_id, expected_type=type_hints["item_id"])
        return typing.cast(typing.Optional[GraphItem], jsii.invoke(self, "retrieveNodeFromGraph", [item_id]))

    @jsii.member(jsii_name="retrievePendingLocalToolCalls")
    def retrieve_pending_local_tool_calls(
        self,
        tool_calls: typing.Sequence[ToolCall],
    ) -> typing.List[ToolCall]:
        '''Filters and retrieves local tool calls from a given list of tool calls.

        :param tool_calls: - The list of tool calls to filter.

        :return: An array of tool calls that are of type LOCAL.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c8bd19cf7540125e9b8a693e01fca0f177512d77ee3bab418456eeeef90162f)
            check_type(argname="argument tool_calls", value=tool_calls, expected_type=type_hints["tool_calls"])
        return typing.cast(typing.List[ToolCall], jsii.invoke(self, "retrievePendingLocalToolCalls", [tool_calls]))

    @jsii.member(jsii_name="retrieveThreadsList")
    def retrieve_threads_list(self) -> typing.List[MemoryThread]:
        '''Retrieves the list of memory threads for the current user.

        :return: An array of memory threads associated with the user.

        :throws: {Error} If user details are missing, instructing to update user details first.
        '''
        return typing.cast(typing.List[MemoryThread], jsii.invoke(self, "retrieveThreadsList", []))

    @jsii.member(jsii_name="runTool")
    def run_tool(
        self,
        tool: ToolCall,
        payload_extension: typing.Any = None,
        is_multiple: typing.Optional[builtins.bool] = None,
    ) -> ToolCallResult:
        '''Executes a single tool call and returns the result.

        :param tool: - The tool call to execute.
        :param payload_extension: - Additional payload data to merge.
        :param is_multiple: -

        :return: The result of the tool execution.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e1ca0e533f7a6dc6cf8465ad7809ba4a450abee064ca45429a80a258a5e2e65)
            check_type(argname="argument tool", value=tool, expected_type=type_hints["tool"])
            check_type(argname="argument payload_extension", value=payload_extension, expected_type=type_hints["payload_extension"])
            check_type(argname="argument is_multiple", value=is_multiple, expected_type=type_hints["is_multiple"])
        return typing.cast(ToolCallResult, jsii.invoke(self, "runTool", [tool, payload_extension, is_multiple]))

    @jsii.member(jsii_name="runTools")
    def run_tools(
        self,
        tool_calls: typing.Sequence[ToolCall],
        payload_extension: typing.Any = None,
    ) -> typing.List[ToolCallResult]:
        '''Executes multiple tool calls sequentially and returns their results.

        :param tool_calls: - The list of tool calls to execute.
        :param payload_extension: - Additional payload data to merge.

        :return: A list of results for each tool execution.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__307c287f13e8189f59310f2e5a43f33ebb271c35e1502a531966c06bbe13ef32)
            check_type(argname="argument tool_calls", value=tool_calls, expected_type=type_hints["tool_calls"])
            check_type(argname="argument payload_extension", value=payload_extension, expected_type=type_hints["payload_extension"])
        return typing.cast(typing.List[ToolCallResult], jsii.invoke(self, "runTools", [tool_calls, payload_extension]))

    @jsii.member(jsii_name="selectLLMProvider")
    def select_llm_provider(self, llm_provider: LLMProvider) -> None:
        '''
        :param llm_provider: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9740847c802111e1e7ecb2c787f36456764d241fc1e2b504620eb68c38f2beab)
            check_type(argname="argument llm_provider", value=llm_provider, expected_type=type_hints["llm_provider"])
        return typing.cast(None, jsii.invoke(self, "selectLLMProvider", [llm_provider]))

    @jsii.member(jsii_name="stop")
    def stop(self) -> None:
        return typing.cast(None, jsii.invoke(self, "stop", []))

    @jsii.member(jsii_name="stopExecution")
    def stop_execution(
        self,
        is_success: builtins.bool,
        result: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Stops execution and reports the final result to the controller via a tool call.

        :param is_success: - Indicates whether the execution was successful.
        :param result: - Optional result string to return upon stopping.

        :remarks:

        This method generates a tool call payload with execution result and uses ``AGENT_FINISH_TOOL_ID``
        to notify the controller via both ``addMessages`` and ``runTool``.
        It uses ``ToolCallType.XPANDER`` to mark the tool call type for xpander.ai execution tracking.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d66a4c63458dd56f0d1fe482150d16c1346e9182e052917067713ac99d2be1d6)
            check_type(argname="argument is_success", value=is_success, expected_type=type_hints["is_success"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
        return typing.cast(None, jsii.invoke(self, "stopExecution", [is_success, result]))

    @jsii.member(jsii_name="sync")
    def sync(self) -> "Agent":
        '''
        :return: The deployed agent's details.

        :description: Syncs and deploys the agent along with its related assets.
        :function: sync
        :memberof: xpanderAI
        :throws: {Error} If the sync process fails.
        '''
        return typing.cast("Agent", jsii.invoke(self, "sync", []))

    @jsii.member(jsii_name="update")
    def update(self) -> "Agent":
        '''
        :return: The updated agent's details.

        :description: Updates the agent with the current instance's properties.
        :function: update
        :memberof: xpanderAI
        :throws: {Error} If the update process fails.
        '''
        return typing.cast("Agent", jsii.invoke(self, "update", []))

    @jsii.member(jsii_name="updateUserDetails")
    def update_user_details(self, user_details: UserDetails) -> None:
        '''Updates the user details for the agent.

        :param user_details: - The user details to update.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83adb98120d61cd6e5328f2ce8718542d01899c0e61b507458cf4b016b21ae58)
            check_type(argname="argument user_details", value=user_details, expected_type=type_hints["user_details"])
        return typing.cast(None, jsii.invoke(self, "updateUserDetails", [user_details]))

    @builtins.property
    @jsii.member(jsii_name="endToolEnabled")
    def end_tool_enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "endToolEnabled"))

    @builtins.property
    @jsii.member(jsii_name="hasLocalTools")
    def has_local_tools(self) -> builtins.bool:
        '''Checks if the agent has local tools loaded.'''
        return typing.cast(builtins.bool, jsii.get(self, "hasLocalTools"))

    @builtins.property
    @jsii.member(jsii_name="hasMCPServers")
    def has_mcp_servers(self) -> builtins.bool:
        '''Checks if the agent has mcp servers attached.'''
        return typing.cast(builtins.bool, jsii.get(self, "hasMCPServers"))

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(self) -> Memory:
        '''Retrieves the memory instance for the agent.'''
        return typing.cast(Memory, jsii.get(self, "memory"))

    @builtins.property
    @jsii.member(jsii_name="messages")
    def messages(self) -> typing.List[typing.Any]:
        '''Retrieves list of messages.

        :return: A list of messages according to the agent's llm provider.
        '''
        return typing.cast(typing.List[typing.Any], jsii.get(self, "messages"))

    @builtins.property
    @jsii.member(jsii_name="sourceNodeType")
    def source_node_type(self) -> SourceNodeType:
        '''Retrieves the type of source node for the agent.'''
        return typing.cast(SourceNodeType, jsii.get(self, "sourceNodeType"))

    @builtins.property
    @jsii.member(jsii_name="toolChoice")
    def tool_choice(self) -> builtins.str:
        '''Gets the tool choice mode.

        :return: Returns 'required' if ``withAgentEndTool`` is true, otherwise 'auto'.
        '''
        return typing.cast(builtins.str, jsii.get(self, "toolChoice"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''Constructs the API URL for this agent.'''
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="vanillaKnowledgeBases")
    def vanilla_knowledge_bases(self) -> typing.List[KnowledgeBase]:
        '''Retrieves the vanilla knowledge bases of the agent.'''
        return typing.cast(typing.List[KnowledgeBase], jsii.get(self, "vanillaKnowledgeBases"))

    @builtins.property
    @jsii.member(jsii_name="accessScope")
    def access_scope(self) -> AgentAccessScope:
        '''- Scope of the agent's access permissions.'''
        return typing.cast(AgentAccessScope, jsii.get(self, "accessScope"))

    @access_scope.setter
    def access_scope(self, value: AgentAccessScope) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb6c11034237fb99d4afc18d0b8280c1e1f09ddaefe3eb074cf796e3b725e93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessScope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> Configuration:
        '''- Configuration settings for the agent.'''
        return typing.cast(Configuration, jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: Configuration) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2acddc917b6b415bc14dfb9a7094cbd1b0319e93c3c4b3298f8cb5d9ec8206a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegationEndStrategy")
    def delegation_end_strategy(self) -> AgentDelegationEndStrategy:
        return typing.cast(AgentDelegationEndStrategy, jsii.get(self, "delegationEndStrategy"))

    @delegation_end_strategy.setter
    def delegation_end_strategy(self, value: AgentDelegationEndStrategy) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3661730e0df834b6194aee6c2237f76d066a302c1a032e7243ebd65edb9ce0e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegationEndStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegationType")
    def delegation_type(self) -> AgentDelegationType:
        '''- The agent's delegation type (Router/Sequence).'''
        return typing.cast(AgentDelegationType, jsii.get(self, "delegationType"))

    @delegation_type.setter
    def delegation_type(self, value: AgentDelegationType) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__595deaa3cabe2c927e992ffe08afc2aa88721124c5e9b438db838667096751f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="graph")
    def graph(self) -> Graph:
        return typing.cast(Graph, jsii.get(self, "graph"))

    @graph.setter
    def graph(self, value: Graph) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__455c760f94e4fc5ed8c239f2c501ce6bf2eb3da9a89e20e6afdd569a617b8ab0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "graph", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''- Unique identifier for the agent.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0b9d8c488cea43db21adbef0723558d2e632d07b3f9134efdeb872de791fa1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instructions")
    def instructions(self) -> "AgentInstructions":
        '''- Instructions for the agent's operation.'''
        return typing.cast("AgentInstructions", jsii.get(self, "instructions"))

    @instructions.setter
    def instructions(self, value: "AgentInstructions") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__729aa75df9167864d69d977ed37c2a63fa4c55e59a6a6595769ebe73e9503771)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instructions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="knowledgeBases")
    def knowledge_bases(self) -> typing.List[KnowledgeBase]:
        '''- Knowledge bases associated with the agent.'''
        return typing.cast(typing.List[KnowledgeBase], jsii.get(self, "knowledgeBases"))

    @knowledge_bases.setter
    def knowledge_bases(self, value: typing.List[KnowledgeBase]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d560d33d3a8d9ab2d5d84adacd04b2b8a4d5a0db676c32684e81f32478d93eaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knowledgeBases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="llmProvider")
    def llm_provider(self) -> LLMProvider:
        return typing.cast(LLMProvider, jsii.get(self, "llmProvider"))

    @llm_provider.setter
    def llm_provider(self, value: LLMProvider) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__461357f98d7832be631c7539e2a04a98e371030637fbb3e8aea3024cef4960a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "llmProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localTools")
    def local_tools(self) -> typing.List[ILocalTool]:
        '''Collection of local tools specific to this agent.'''
        return typing.cast(typing.List[ILocalTool], jsii.get(self, "localTools"))

    @local_tools.setter
    def local_tools(self, value: typing.List[ILocalTool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdc78718c4e88ad0687034fec3393a9b0dd4518c626fe4c60d2244cefaadbe37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localTools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryStrategy")
    def memory_strategy(self) -> MemoryStrategy:
        '''- Strategy for memory management.'''
        return typing.cast(MemoryStrategy, jsii.get(self, "memoryStrategy"))

    @memory_strategy.setter
    def memory_strategy(self, value: MemoryStrategy) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f78a447686d7a170f7713415428aefc1544249c3da73e354d5f28a8917f689ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryStrategy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryType")
    def memory_type(self) -> MemoryType:
        '''- Type of memory the agent utilizes.'''
        return typing.cast(MemoryType, jsii.get(self, "memoryType"))

    @memory_type.setter
    def memory_type(self, value: MemoryType) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__805f0dbb3034522e5cd382a8d7f7c31a544db0bd26e45b0915f5b060aec59bed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''- Human-readable name of the agent.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22da1a47b30804817cea4f52e46761946f71d0d3436d3236d8ab8bbd3f9a2364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oas")
    def oas(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "oas"))

    @oas.setter
    def oas(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed0174f671a90a524f265b28d5f9b948ecc8db890cd973390f9a408091d5cd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''- Organization ID to which the agent belongs.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b78331aeaf11efbf7d44a1bd4ce9783ac8b3be074090b3f146520a09bb2ff99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="originalToolNamesReMapping")
    def _original_tool_names_re_mapping(
        self,
    ) -> typing.Mapping[builtins.str, builtins.str]:
        '''Maps original tool names to renamed versions for consistency.'''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "originalToolNamesReMapping"))

    @_original_tool_names_re_mapping.setter
    def _original_tool_names_re_mapping(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6762bda91838241a6ee34d79cd8660a8ecf1de3ef553cabb0bd5130090bc15a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originalToolNamesReMapping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prompts")
    def prompts(self) -> typing.List[builtins.str]:
        '''- Prompts used by the agent.'''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "prompts"))

    @prompts.setter
    def prompts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da71d0425a1a175452f028e91eec348b008ccd07d2c4ee25c3bc20232edadfb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prompts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ready")
    def ready(self) -> builtins.bool:
        '''Indicates if the agent is ready and tools are loaded.'''
        return typing.cast(builtins.bool, jsii.get(self, "ready"))

    @ready.setter
    def ready(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89bc6384ff613546183aa4186ddfac11deaaf2c2b3c4f43fd64f205dee4ad649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ready", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceNodes")
    def source_nodes(self) -> typing.List[ISourceNode]:
        '''- Source nodes associated with the agent.'''
        return typing.cast(typing.List[ISourceNode], jsii.get(self, "sourceNodes"))

    @source_nodes.setter
    def source_nodes(self, value: typing.List[ISourceNode]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1dff1fd2031b8c10437260cbaae7a1861611afa24cb0ca6b7126c825461d0aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> AgentStatus:
        '''- Current status of the agent.'''
        return typing.cast(AgentStatus, jsii.get(self, "status"))

    @status.setter
    def status(self, value: AgentStatus) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f657c5abb4af14138072346cc87aee77138c4171cd0fc2bf21f903fd6c6299ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tools")
    def tools(self) -> typing.List[IAgentTool]:
        '''- Tools available to the agent.'''
        return typing.cast(typing.List[IAgentTool], jsii.get(self, "tools"))

    @tools.setter
    def tools(self, value: typing.List[IAgentTool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d712115a2ab298e5d50d49c632fab67794a7409f1db441e663ee069fabba3ef8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tools", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "version"))

    @version.setter
    def version(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddb249e972d9df7a7192823a54a5a782d4cb6f68f0a20fccf97eed51464257b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="execution")
    def execution(self) -> typing.Optional[Execution]:
        return typing.cast(typing.Optional[Execution], jsii.get(self, "execution"))

    @execution.setter
    def execution(self, value: typing.Optional[Execution]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b67abdb1cba5becc669e94a301b7f98b7c0c0b097b682d08a910595e09541afb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "execution", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="executionMemory")
    def execution_memory(self) -> typing.Optional[Memory]:
        return typing.cast(typing.Optional[Memory], jsii.get(self, "executionMemory"))

    @execution_memory.setter
    def execution_memory(self, value: typing.Optional[Memory]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89fe0c3654814305defb5190865bb0e7e7946de0fcd8a1902cc070067eebac5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionMemory", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userDetails")
    def user_details(self) -> typing.Optional[UserDetails]:
        return typing.cast(typing.Optional[UserDetails], jsii.get(self, "userDetails"))

    @user_details.setter
    def user_details(self, value: typing.Optional[UserDetails]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fabc29b53bc06a2b34ccc6428c40b29c90e1d5ec2e10f24d38c01e08691e82d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userDetails", value) # pyright: ignore[reportArgumentType]


class AgentInstructions(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.AgentInstructions",
):
    '''Represents the instructions provided to an agent within the xpander.ai framework.

    :class: AgentInstructions
    :extends: Base

    Example::

        const instructions = new AgentInstructions(
          ['data-analyzer'],
          ['extract insights from customer data'],
          'Perform general analysis and summary of given inputs.'
        );
    '''

    def __init__(
        self,
        role: typing.Optional[typing.Sequence[builtins.str]] = None,
        goal: typing.Optional[typing.Sequence[builtins.str]] = None,
        general: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param role: -
        :param goal: -
        :param general: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4da74b53547f0d8183511f5718499b6511ce5b76ea838b6bfb5d57375add4bc2)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument goal", value=goal, expected_type=type_hints["goal"])
            check_type(argname="argument general", value=general, expected_type=type_hints["general"])
        jsii.create(self.__class__, self, [role, goal, general])

    @builtins.property
    @jsii.member(jsii_name="general")
    def general(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "general"))

    @general.setter
    def general(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5d84d42689623385325eea71e52af47a908566ba3ada2cd4717f6db79a5e87e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "general", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="goal")
    def goal(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "goal"))

    @goal.setter
    def goal(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f558d9b2c5b0e6e2b7040a982539f1e66ac8e30e733878d0543b8c798c7c55bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "goal", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "role"))

    @role.setter
    def role(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c2d5459e4c3b9d304799f5aba566152b118f3bcb59d6669a2b6aa78e1ffdc35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]


class AgenticInterface(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.AgenticInterface",
):
    '''Represents an agentic interface with identifying and descriptive properties.

    :class: AgenticInterface
    :extends: Base *
    :memberof: xpander.ai
    '''

    def __init__(
        self,
        id: builtins.str,
        name: builtins.str,
        summary: builtins.str,
        description: builtins.str,
    ) -> None:
        '''
        :param id: -
        :param name: -
        :param summary: -
        :param description: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0421198e44ee66874d3a9ac56a6a99b6dc0f7eaeda89671242d6bf39f995ebb)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument summary", value=summary, expected_type=type_hints["summary"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        jsii.create(self.__class__, self, [id, name, summary, description])

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56a0933f379e823c8bd5a098d8cd0823f5da788f81e2cf82493bf3af19aa8278)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08bd8a9295a3f6bca09f1c529729d2e5992f248ccf768c476242ab5d1de6783b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31c02741e670a81628ccc3d3192b3361264d004315b890e135943817d1d096be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="summary")
    def summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "summary"))

    @summary.setter
    def summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c3a97c5c727d70421a58b11a3058835df0a23f2a16d59f8cdba4de75a695978)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "summary", value) # pyright: ignore[reportArgumentType]


class AgenticOperation(
    Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.AgenticOperation",
):
    '''Represents an agentic operation with metadata and execution details.

    :class: AgenticOperation
    :extends: Base *
    :memberof: xpander.ai
    '''

    def __init__(
        self,
        id: builtins.str,
        name: builtins.str,
        summary: builtins.str,
        description: builtins.str,
        id_to_use_on_graph: builtins.str,
        interface_id: builtins.str,
        is_function: builtins.bool,
        method: builtins.str,
        path: builtins.str,
    ) -> None:
        '''
        :param id: -
        :param name: -
        :param summary: -
        :param description: -
        :param id_to_use_on_graph: -
        :param interface_id: -
        :param is_function: -
        :param method: -
        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d00f579f8b6ee8853d6931c865ecc5f5725966e5904e8b93d829aa1ee31f452c)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument summary", value=summary, expected_type=type_hints["summary"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id_to_use_on_graph", value=id_to_use_on_graph, expected_type=type_hints["id_to_use_on_graph"])
            check_type(argname="argument interface_id", value=interface_id, expected_type=type_hints["interface_id"])
            check_type(argname="argument is_function", value=is_function, expected_type=type_hints["is_function"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        jsii.create(self.__class__, self, [id, name, summary, description, id_to_use_on_graph, interface_id, is_function, method, path])

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16136fd2cfb48534b715b821da91ba0ebd50f4bc91c89635be6fd883c37e98c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a0c69767cc9b4f79e6e93e447d7eefbd6f542b65f5bf0159dc4a2903ae01ac8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idToUseOnGraph")
    def id_to_use_on_graph(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idToUseOnGraph"))

    @id_to_use_on_graph.setter
    def id_to_use_on_graph(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__927a7c017e4de23bc0d60ebf1c164f160dab69aa503297714add886d9d80c55d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idToUseOnGraph", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interfaceId")
    def interface_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceId"))

    @interface_id.setter
    def interface_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a6e530ff5690677acfbd9200f9c7d8708df4352809ed9f249e11bff282c541a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interfaceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isFunction")
    def is_function(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isFunction"))

    @is_function.setter
    def is_function(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b51d5413b6076bc739a43c541f056c33398474a75b28756209fe0c1f6a177cd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isFunction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bea3b9c44e7fc9bb175da70e7039e2646073c61c4a79c867792dc37e52e95eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__307dd21d55d2a3ba195730e39e0dc6189176bbd4eb3c27a4189933af67a0550e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__346d4f6c174a3dd581dd1a41074b805bf9d98571e4c31a3bee2fa180205bc608)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="summary")
    def summary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "summary"))

    @summary.setter
    def summary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdd36b5fcfcdcd966eb42737d1b07a3aacc359e8a701825f48df5eddef35e432)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "summary", value) # pyright: ignore[reportArgumentType]


class ExecutionMetrics(
    MetricsBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.ExecutionMetrics",
):
    def __init__(
        self,
        source: builtins.str,
        execution_id: builtins.str,
        sub_executions: typing.Optional[typing.Sequence[builtins.str]] = None,
        memory_thread_id: typing.Optional[builtins.str] = None,
        task: typing.Optional[builtins.str] = None,
        triggered_by: typing.Optional[builtins.str] = None,
        skills: typing.Optional[typing.Sequence[builtins.str]] = None,
        status: typing.Optional[builtins.str] = None,
        duration: typing.Optional[jsii.Number] = None,
        ai_model: typing.Optional[builtins.str] = None,
        worker: typing.Optional[builtins.str] = None,
        ai_employee_id: typing.Optional[builtins.str] = None,
        api_calls_made: typing.Optional[typing.Sequence[typing.Any]] = None,
        result: typing.Optional[builtins.str] = None,
        llm_tokens: typing.Optional[Tokens] = None,
    ) -> None:
        '''
        :param source: -
        :param execution_id: -
        :param sub_executions: -
        :param memory_thread_id: -
        :param task: -
        :param triggered_by: -
        :param skills: -
        :param status: -
        :param duration: -
        :param ai_model: -
        :param worker: -
        :param ai_employee_id: -
        :param api_calls_made: -
        :param result: -
        :param llm_tokens: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0a23d2576a400dab8819022af0df7b0396c4f396b10977354c94cf8b3f91f68)
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument execution_id", value=execution_id, expected_type=type_hints["execution_id"])
            check_type(argname="argument sub_executions", value=sub_executions, expected_type=type_hints["sub_executions"])
            check_type(argname="argument memory_thread_id", value=memory_thread_id, expected_type=type_hints["memory_thread_id"])
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
            check_type(argname="argument triggered_by", value=triggered_by, expected_type=type_hints["triggered_by"])
            check_type(argname="argument skills", value=skills, expected_type=type_hints["skills"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
            check_type(argname="argument ai_model", value=ai_model, expected_type=type_hints["ai_model"])
            check_type(argname="argument worker", value=worker, expected_type=type_hints["worker"])
            check_type(argname="argument ai_employee_id", value=ai_employee_id, expected_type=type_hints["ai_employee_id"])
            check_type(argname="argument api_calls_made", value=api_calls_made, expected_type=type_hints["api_calls_made"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
            check_type(argname="argument llm_tokens", value=llm_tokens, expected_type=type_hints["llm_tokens"])
        jsii.create(self.__class__, self, [source, execution_id, sub_executions, memory_thread_id, task, triggered_by, skills, status, duration, ai_model, worker, ai_employee_id, api_calls_made, result, llm_tokens])

    @builtins.property
    @jsii.member(jsii_name="aiEmployeeId")
    def ai_employee_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aiEmployeeId"))

    @ai_employee_id.setter
    def ai_employee_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d95f5139406915b7629e6ee233b89c646474c8a5ea1e849fee06932ef134cba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aiEmployeeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aiModel")
    def ai_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aiModel"))

    @ai_model.setter
    def ai_model(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a8dcbeff1fb21fa64959e475f6a99ad147dc8d5183d962848f888c8f2a75f4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aiModel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiCallsMade")
    def api_calls_made(self) -> typing.List[typing.Any]:
        return typing.cast(typing.List[typing.Any], jsii.get(self, "apiCallsMade"))

    @api_calls_made.setter
    def api_calls_made(self, value: typing.List[typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a332b8a7051546f589d0e1717fb96df2864e0e8fabda5d46747cda079c9d78ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiCallsMade", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c9bcfdd0bd94e084cdf3403b76f3a3457eccb58cc0646f90a34e3c95adc2ed9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="executionId")
    def execution_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionId"))

    @execution_id.setter
    def execution_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef4bb1f3fb78bef421d677fc5bd2a6f9e2ccf1de4a9f7e4b827516baadfeeacd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="llmTokens")
    def llm_tokens(self) -> Tokens:
        return typing.cast(Tokens, jsii.get(self, "llmTokens"))

    @llm_tokens.setter
    def llm_tokens(self, value: Tokens) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d17923eae7d86c986a64e9e20660611129063467c27b2052d9e78fbd797f53c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "llmTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="memoryThreadId")
    def memory_thread_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "memoryThreadId"))

    @memory_thread_id.setter
    def memory_thread_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7fcb9bb5c3e9f690c8f00f402f591d7ecfd6748464b65f0bc7d6852f695b157)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "memoryThreadId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="result")
    def result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "result"))

    @result.setter
    def result(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eb676f604f7a7cf535bdd88a1f0b69d2c3781ba8e971c5c05bf500023f3c452)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "result", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skills")
    def skills(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "skills"))

    @skills.setter
    def skills(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c34e1c35e1f7ac9512e4c3be386781893cc2bf24a48789961595854c7c4af5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skills", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04fde28064408d412417c483de95f3248a4af0c224b83e5f1c0d36c206da3898)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bc49a2aa9df8e476dffc5653b4b81f6d971462a831e8294eca730c2f1f2f095)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subExecutions")
    def sub_executions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subExecutions"))

    @sub_executions.setter
    def sub_executions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f2399a878cc9ea4c6c6b29530779d5ccbad71412b8a3b1d6ddbc0a087df240)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subExecutions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "task"))

    @task.setter
    def task(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fafdf1312e9e78054c2e3e08be239b78dfe8357a2b387ebe2148831d6e885c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "task", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="triggeredBy")
    def triggered_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "triggeredBy"))

    @triggered_by.setter
    def triggered_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4300e7ab3fef290648958095fdb7c6fb08e539776f8727ae23edd9718a6af893)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggeredBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="worker")
    def worker(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "worker"))

    @worker.setter
    def worker(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dce5845684332dad7cfa7cba737c0ea3e23af2a75ab31f91eb7b37698517d060)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "worker", value) # pyright: ignore[reportArgumentType]


class LLMMetrics(
    MetricsBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="xpander-sdk.LLMMetrics",
):
    def __init__(
        self,
        source_node_type: builtins.str,
        finish_reason: typing.Optional[builtins.str] = None,
        provider: typing.Optional[LLMProvider] = None,
        model: typing.Optional[builtins.str] = None,
        duration: typing.Optional[jsii.Number] = None,
        prompt_tokens: typing.Optional[jsii.Number] = None,
        completion_tokens: typing.Optional[jsii.Number] = None,
        total_tokens: typing.Optional[jsii.Number] = None,
        function_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param source_node_type: -
        :param finish_reason: -
        :param provider: -
        :param model: -
        :param duration: -
        :param prompt_tokens: -
        :param completion_tokens: -
        :param total_tokens: -
        :param function_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95e6bc9fe2f387a7934d2bf3ca35a2874ee3a7d6187eb51f4212020bf9ffcaf1)
            check_type(argname="argument source_node_type", value=source_node_type, expected_type=type_hints["source_node_type"])
            check_type(argname="argument finish_reason", value=finish_reason, expected_type=type_hints["finish_reason"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
            check_type(argname="argument prompt_tokens", value=prompt_tokens, expected_type=type_hints["prompt_tokens"])
            check_type(argname="argument completion_tokens", value=completion_tokens, expected_type=type_hints["completion_tokens"])
            check_type(argname="argument total_tokens", value=total_tokens, expected_type=type_hints["total_tokens"])
            check_type(argname="argument function_name", value=function_name, expected_type=type_hints["function_name"])
        jsii.create(self.__class__, self, [source_node_type, finish_reason, provider, model, duration, prompt_tokens, completion_tokens, total_tokens, function_name])

    @builtins.property
    @jsii.member(jsii_name="completionTokens")
    def completion_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "completionTokens"))

    @completion_tokens.setter
    def completion_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2b5bbd91446490960da2d273a10a10ec832d31eb07042199f29cc19fb03fe10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completionTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="duration")
    def duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "duration"))

    @duration.setter
    def duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bee74b44a45f2cdc6dc717ac2c9e0963d46b80931fb6ae5c3c17263be8f14b20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "duration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="finishReason")
    def finish_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finishReason"))

    @finish_reason.setter
    def finish_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db12302f49a6391aeb5bd9d619a5f6b4618ba61b26b1520bc4ebc2dc6019c1df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "finishReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "functionName"))

    @function_name.setter
    def function_name(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e02a2996428bfdf63c01fb22bfd803a5983254bc5a0d521a785dae3fbabeec5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "model"))

    @model.setter
    def model(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47b3f67277a37dc2e6dfea898a83aadaffb6c3ed15b3768ec7e931567f0d4b55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "model", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="promptTokens")
    def prompt_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "promptTokens"))

    @prompt_tokens.setter
    def prompt_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d68dd5305cc0e20650929ac52607eef81d44f5d872bbf721cdd5b31709cee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "promptTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> LLMProvider:
        return typing.cast(LLMProvider, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: LLMProvider) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60a70fae0cf0e4068388f776612812f1b94283597c2387d40f5ccf20f9bf961a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceNodeType")
    def source_node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceNodeType"))

    @source_node_type.setter
    def source_node_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cfc835d388478f4971cb8fca3b6a5073ecd664dfcfddd466717b98a08bdd455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceNodeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalTokens")
    def total_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalTokens"))

    @total_tokens.setter
    def total_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f49c427ae78f6c816dbca40629bada77b3292d61e47efe333f5e77c41633abc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalTokens", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Agent",
    "AgentAccessScope",
    "AgentDelegationEndStrategy",
    "AgentDelegationType",
    "AgentGraphItemSubType",
    "AgentGraphItemType",
    "AgentInstructions",
    "AgentStatus",
    "AgentType",
    "AgenticInterface",
    "AgenticOperation",
    "Agents",
    "Base",
    "Configuration",
    "Execution",
    "ExecutionMetrics",
    "ExecutionStatus",
    "Graph",
    "GraphItem",
    "IAgentGraphItemAdvancedFilteringOption",
    "IAgentGraphItemMCPSettings",
    "IAgentGraphItemSchema",
    "IAgentGraphItemSettings",
    "IAgentTool",
    "IBedrockTool",
    "IBedrockToolOutput",
    "IBedrockToolSpec",
    "IBedrockToolSpecInputSchema",
    "IConfiguration",
    "IExecutionInput",
    "ILocalTool",
    "ILocalToolFunction",
    "IMemoryMessage",
    "INodeDescription",
    "INodeSchema",
    "IOpenAIToolFunctionOutput",
    "IOpenAIToolOutput",
    "IPGSchema",
    "ISourceNode",
    "ITool",
    "IToolCall",
    "IToolCallPayload",
    "IToolExecutionResult",
    "IToolInstructions",
    "IToolParameter",
    "KnowledgeBase",
    "KnowledgeBaseDocument",
    "KnowledgeBaseItem",
    "KnowledgeBaseStrategy",
    "KnowledgeBaseType",
    "KnowledgeBases",
    "LLMMetrics",
    "LLMProvider",
    "LLMTokens",
    "Memory",
    "MemoryStrategy",
    "MemoryThread",
    "MemoryType",
    "MetricsBase",
    "SourceNodeType",
    "Tokens",
    "ToolCall",
    "ToolCallResult",
    "ToolCallType",
    "UnloadedAgent",
    "UserDetails",
    "XpanderClient",
]

publication.publish()

def _typecheckingstub__56c927c42c835c774c6f5f1f6f97fed3b3214baccc5c46df58f7f5cf97262992(
    configuration: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76702171336bf6b0ea472737a1f7d3c35de102f261244c52f4175ac7a6799b14(
    name: builtins.str,
    type: typing.Optional[AgentType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb382a0499d6ff9252ba35bb8f4c90a05697129cfe9cad98a7f8a1a14da8e1d4(
    agent_id: builtins.str,
    version: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f37932ab42616ef0215f3190c6c4bfa79237ec478d6c77803ea5cc9260af1f3(
    value: typing.List[UnloadedAgent],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec4b41eaf57993f4b49ed6bc9995e9ed9fa2685fb355f0d948717f7ea7e34c2f(
    value: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dab3da5f8c0475ccab1873969e148ad9dcbdb0ddf88c9ecc6b02b751238b6e5(
    data: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d4d603584cc9880629c407e84565dc862d0614d798748f7556e51d6023943cb(
    data: typing.Mapping[typing.Any, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dafae5b4445df1b4c673783f144d770b151e831e63bc8be999b4708f966d5caa(
    __0: IConfiguration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135b56998170832cdd7296e91cdddd9c57d7b17d36e505bee4468b800785e5a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6025924c03e9981cc1b85f95320de6d369f9970a79f6ee17298111769cddfa5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20369269e83a8faf9b0e5c03d8b299c924f1479bf7cf5b8c1b3b9f8bb93c406f(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3511e5562e6adcbc92f800855d3a0afb25a625d0c55d5485a4a1dce9c4d0f5(
    id: builtins.str,
    agent_id: builtins.str,
    organization_id: builtins.str,
    input: IExecutionInput,
    status: ExecutionStatus,
    last_executed_node_id: typing.Optional[builtins.str] = None,
    memory_thread_id: typing.Optional[builtins.str] = None,
    parent_execution: typing.Optional[builtins.str] = None,
    worker_id: typing.Optional[builtins.str] = None,
    result: typing.Optional[builtins.str] = None,
    llm_tokens: typing.Optional[Tokens] = None,
    agent_version: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28ac71fcc66c47d57a2431d7b9d1ededfeebe4d25d4d76be0af7aea52433b43e(
    agent: Agent,
    input: builtins.str,
    files: typing.Sequence[builtins.str],
    worker_id: typing.Optional[builtins.str] = None,
    thread_id: typing.Optional[builtins.str] = None,
    parent_execution_id: typing.Optional[builtins.str] = None,
    tool_call_name: typing.Optional[builtins.str] = None,
    agent_version: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5826ee4343bbc6d6fa82b8318fb69ba8915209dc65ef5871fcded50883e01a3b(
    agent: Agent,
    execution_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a16dd673599a3466cd88daa634558ce551e5bf88775633c2a1b347c8d331cc4(
    created_execution: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77c3a6862ed0afbaef96d1fb83314e009abc247417477fc19054c75929da550d(
    agent: Agent,
    worker_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cee0f42d8d8dd5f66e986850120e23b19cc68cac936f98a8dd25fb36353d17a(
    agent: Agent,
    execution_id: builtins.str,
    delta: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b03ca08f9b2b069041973b39cf02c9a0068d90548e5ddee63b20fe94c7012609(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b8ae0a9930209f40a66e2e42b95dd021cdd8ddba299929a31caa19ae08d4cf1(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d868b6b5ce250193ce443b9016b04756769b83eeba535e78241ec0ff3f83d51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdf2cbec0d7a7f57322611349ee6da80c76ffc15d17073f0a02db00de934ea18(
    value: IExecutionInput,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f14ab38fd58bcb6df93f21afda177a617f7ba0d607127377b3613011486dd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b8ec1c80577669cd65855b4bfcc994db091cf6f987b85815778246c461c834f(
    value: Tokens,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71b5fe859564b314681ecc8ec189116efd662d6e84e6ac8185c34215670ec574(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cdb7bc0e59f92fdd53d0635a8fca37266c786acca82dac2cbfc332ac269981(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98eb70fdda04bc040f99a78963bf4c39b92357daed49526791876d5d160ac033(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cba55b034120440ccd908317158f72c44d2b7322aebe344934e7495df875f5bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ea35b2f322e75bd9b6c5f06edfbe93b6c622ef9bc2c373933a362ffe4af250(
    value: ExecutionStatus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b54b957eb2ffee3bc5db4dc5843d7381ada868fa8b19457c6ae7bb85e5235834(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05c62bde7fdbe61c5e8a021bd34dd2caa05004f9b05f08679285c1916bbac5c0(
    agent: Agent,
    items: typing.Sequence[GraphItem],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa425681e3f5e5317e5e11364c4e8fd5e072b73205f40342eb460fdc7c769fa5(
    node: typing.Union[Agent, GraphItem],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b1d141f90de09eccb807109ef6536ff2c9788996c910b07bd8d1e73db2d04a6(
    item_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3507c211c7595e5c0f4712af30156e3ff1d0137bf46f41ae16951f52221f66a9(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e5c908c03ffa1a741480d3abd5a079bcf0c1ac187699aed7deb5ab56fce6529(
    node_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15160dba22952263e9151beef520c9612beb9cb07eed594d7bb4d56d5119adb4(
    agent: Agent,
    id: typing.Optional[builtins.str] = None,
    item_id: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[AgentGraphItemType] = None,
    is_local_tool: typing.Optional[builtins.bool] = None,
    targets: typing.Optional[typing.Sequence[builtins.str]] = None,
    settings: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f56ab7aacb7878e1d39e5898ac1427926bfc05426f15db694d3fc0ff734dedad(
    targets: typing.Sequence[GraphItem],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74968991c9a0c8c387a3fd1115e9e2ee1dcfc781eafd41ea456f2215d517ff05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4d6791c897c3b4cba72154de942bf44559197ad1162bd5610ffe8e1672b11f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebba065518cc99903325a7584e1d0747cc5bcfea4a9cd32a741ae37d3f91b2f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3a4981d71edb62a9f18e2559a8e1c3ce4c8234ae77ce043029575f4d94187c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac535ec8b6e6592e8b1da2efcbcc433463a94dc3f8b822fc0ffbae7245e36820(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fefc2e34cc9c85d0ecc86ca114ee5d300ccf9e14fe00bb70821a4796b530eb6(
    value: AgentGraphItemType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66d78e4b33ae25244cb7b81ee8ec05b2cc6797c8ff01f37b427240985f25f7c3(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c37442176fd38f417112ebe47d309cfbcd7730390b5e828c327831187383b0b9(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a22b984d43570db7290f1372800735e3ac718279f0b81723ed1d35d12bc3e7f(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fb360ef1fd0dcf7f3a19dca1e9bfda4864bf9b2135ee0b3e2c58cdbdd93c5a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b925c95748b3345b4bb550bf691c8bf2ed25b265328e9941c7ea089164779ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06b0f2790ca7d605344b619d76ee541c60899dc5da95e03d5fb1f909b4d3142f(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d01f08d3c62996d9ee3cb22120fdd61c8bb47a41dd73e73eddaed059f977795c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d83a27065ff688296f54a2b4a7b7bd9e2cf50799491f1783c29eecaa4fb598e3(
    value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10c09b4778194db94a8d00c666b7a1871afdce4091cd3cac67e6f78ea507904a(
    value: typing.Optional[typing.Mapping[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ddafee8c7509fd377d08cd4dcb4bd75f290d6cfee8836b9158c69a50a8d205(
    value: typing.Optional[typing.List[IAgentGraphItemAdvancedFilteringOption]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48133c207df167a1e2ac7d22c1e6b7159bb3845cf34a55f28a9c340e4b17b5a0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5abe35889371107b0a28dc1777a7eed9117daefb0245778d0a219398b8b30de(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa56cad7247d597ff8e8db1d3e9b3ea9e18e1b3943bb31502832624d61e9b55a(
    value: typing.Optional[IAgentGraphItemMCPSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c048394bfb4cd680c4e606cd9f9da38990e641593522bda31ffc5307812b9f(
    value: typing.Optional[IAgentGraphItemSchema],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__013ed94cf5075f5bf0c5bc74a0e8036501c284d35e4392ea6f15080eddc2a7ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1b25237ddc5e6038acd2ee375459e97263388f5a79c9b19df1509b8ad33817e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ba86af1a111c4132196288035231114364f7fd5846ba31b895e28cf0263f6b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdd4d28b7b8f38ee90640906c0dfa66779e13f1537479bfac62236199af53599(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfb31aa04b21eb4806b8482aa225a11b478a08f9a3d8fe6ed1ff02f818c62244(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7629b10507753cd17f8a141e1f5acf42aa3ad6279b11466521e8e879158f1c0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c1639f3cf0ce4876316784b66d4eb55d50082b87dcaa56347a0ebcb4c5be615(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76420473c4800542a5c924d1375223fda76771d1a194354c646c87a134351b2d(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94d18303f76ca1cea7f0333afa6e171a5ff4c99c53601d4772e5d916b00ae6de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__686bee2f9cc4cb8e5e46bd20309c912c48752fa01feec49d211288fe414d9879(
    value: IBedrockToolSpec,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50442d45bad8e7fa927b6be3feac263e79712091c62056e831a391b5a17c13bc(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bab15f7ad29e9cbdf37869d4d12b1eca4937a0130eb1409bb74f1149d0dfc26b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39dfbf6fa195f65cf55b428cbf9c7e700af738bcd9c47ebdda318cfedf78e70a(
    value: IBedrockToolSpecInputSchema,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0534d2b1daae9caffc87b99f4b6cc09e1a9eac3888374c04e9c619375c2f1b35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1454322c6f1b39bdf36a5d88226526fce2d55d1e13ada58cf00d44f12fd64366(
    value: typing.Mapping[builtins.str, IToolParameter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3e8b15e3c3381cc6704c1ee29aa4c16d1b4a86e2ac011b6e441b3e0b431f930(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07a526e81165d7b0acee70572029a007577d042379f52fcd7844f14a292ff14e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df183128da8ce312ade8f62d98d9db3bba128d9acf1d9f56955baae69e409c37(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da3a818f4694a99ea585b769eb098754a7fe2d1868cc0704ace9d8e92ba7f3f1(
    value: UserDetails,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ded72ddaf5f71f91ade05bb19c950ea501c6e1e1233100d5f19c597947e7d3aa(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eb39d06928f51e090591017e234f9560633786e66b238d3b42531c3252f0eea(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12e375f6294f1a5448700c974b2c29d93eaac36a1dea798ca8ded9b92594d10b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c40dff0d9263c5102becbce5d5ea18378e769c964c924a052f6c023b15b889e(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2af096115236a1c0df0e3b558acc615c594ec3a2f016074ae50c4c83fcb2600(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__221c82f5a357c0f118efe86c29a8a97b2a8f51d955265c9972dc156543547bb0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d263d1c0fb18bd7e903fe0d0af692e3808ac21c99197a495a3f6c62acba8a50b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25eaf42500bdb62a0efcb583df3587ae560b4f99f9d9214b8ebebc6131aec02e(
    value: typing.Optional[typing.List[IToolCall]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6782cb166f668691a7b4be7b743380ed50722ee1549291808eee66d6a811fed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf5d7d569b37ac0c974cabb49c4e85f99273856f9fc2bdac40d66bc3412561d(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b0db8ab6f32bead8676f5d65edb0c8465aea43ef940f7b1d7b2ba9d2d577c39(
    value: SourceNodeType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f56ea2b548b4cdfe22f0f80bf2c3f88697c04aedd2bf7fe61755b4eb9cee55b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5396ff1ffb06161e7b92840a35a663b1f418ffdcc7dde0e2593addf6ca31936a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__682720a04a90eb0d29239c0baf8e36b53b239f76f1079edf9cd418a69ddb97ac(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bf23d7676e5d1c7e307b10d99651d3e323b4741175a001eec3d04daa9f6a063(
    value: typing.Optional[typing.Mapping[builtins.str, IToolParameter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5219f06879c23f3e080fc36ccd3ecf3404dfc6994def97d5e4ec94ce59d72bb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039a35d67dfcf0e4fcf0d24c95fae7adcb68a33fbc193c12840c321781f41670(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c4f34dbc98830433192bba8d2c699a1cb8148d1491b27977e6d346e261fb913(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9832f75123fcf9d9b942f4c173edc15dd68204b28ad5d4260488d6c5c649f9e(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a367c116b987fb49136a9814177e4d056c61593dd022f63355bb894da7fc9988(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e21845a97036e31f029489182b71f645274dafcc99c56e102732ed75019f377(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__893f015e220df05bf7b08ec5d24e2064db840604744494f599f33b596f114ee0(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a45442afc737189c680b610029e36c0388f812ca6addfc20d90f2255236a7a1d(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f74a57170964ac6f2225d4a42e688907f1b3fc6d5dcc4cefae60ba4c69e6a205(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f354465848d57d08212584493a7b8ebb70e6a4185a12514d09d39089267cc34(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd332b88cb4f7bb75ce8e88200df9b702232ca7807d466896031bba1bac55a15(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbdc5a25cd119bc40de0970a3da5a996792b481e3623e5692f2220f66858eaff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__116d46c0c30294630e565344bb001679a311f6d4bdf7fde9def35de5f5e69bff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09181db93f9b9267ab92d06c025f7bac4699c1fdac9ca798c651a63559aa913f(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187dae4a63a6fee1ee6e1cb395b2f91742bd245c20c13ab04570590726c5ef61(
    value: typing.Mapping[builtins.str, IToolParameter],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16039ce6185f742cd5865e412fc0342905a7a6d458331abeea0c8aea52fd0eb5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b13164b7161ac045d14f7c4212e2fc304cf9b4c0234c2221c11807a860fee0(
    value: typing.Optional[typing.List[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51e3a6f2086f6f694ae00811d3c8cfbc7998d5e84bc5e953097d209d2b1d9e8e(
    id: builtins.str,
    name: builtins.str,
    description: builtins.str,
    strategy: KnowledgeBaseStrategy,
    documents: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd9e1109152304880a099fddab37e97bb8a4b8eac7d4eaeb9ba5b64b7d20f6c(
    agent: Agent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5346ca86b97d9beb023662f6917773322c22dd333b4088d0a3e1aa3f9b863f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f91030cf0630f559d66490e3f6115e32fa737afa26a254c624598a4473424178(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b1a6bd536d05cb8f737d34d1a5470e5cbffbae2b7b39eabd405ec3a83750f39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec5f1b09e3bf37c8db0a7e8a770f79ae3a608fbcf53ae579ab368ca80ea281b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c985cb1467f7bafe537bc1fe177d04bb3967730f168ac32ce862f8c3d39dbe95(
    value: KnowledgeBaseStrategy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fd6fc1bc899c30f952acad91b807e3c07f73510da89adfa97a770eb79ad5064(
    configuration: Configuration,
    id: builtins.str,
    kb_id: builtins.str,
    document_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__494bbd93c6a5e9ca1966bbc40e8be3d234451861d89fcd53b23cb0e2ab4dcb02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f8f7ae67842812194c8b5491d2274fd0b073b0f89f63dcdfb61542b7ca735fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a423960f6ac18af623ce08adfef52d521928c2ae5142dc93ac90cfdaed08e932(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a16c0152501f00605cd56315921ddaa33d77f9545dc90ec0750945db59f8e57f(
    configuration: Configuration,
    id: builtins.str,
    name: builtins.str,
    description: builtins.str,
    type: KnowledgeBaseType,
    organization_id: builtins.str,
    total_documents: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3e0c23fe2c94485ca3f32b3957337ab50312aee88a1d61e71032a2e5e55034(
    urls: typing.Sequence[builtins.str],
    sync: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__145b0ae5ea807889d0359e8b982d1eda720a42f19f365eb9d7f4c99c1779536b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f85c313f85cc78ccb4fe6b4e1f8233e113b17260168de6d9f869d554cc3a662(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5103538f7d91ad0c411c0d92613beba1e18a1ea49de878d886873d975664c0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20428b0e41f89ed6975763d5d75f7a678fbd8256f48c74972d3a5bf85af161f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a81285873a8d10bdc1952072273f2ed5ddfbac0610f731bdcce75452a4014a2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bfc8a098157fa3cf0f23a3b0f6b364ceb07639375ef856b2763787b63f87d0b(
    value: KnowledgeBaseType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c6e2dab357d715d7f0d00dc77fe0087fe20869271615fc96a075d0c48596c79(
    configuration: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eeed02486950f43c36c0410e8a502b926d979648d745c558aa0aaad4202b149(
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22e41d43ad93e4b06027bd610f379a1454b2ed9f72ede507ae3ed2a9271d39db(
    knowledge_base_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b22ff5d2628f8ec12d17053d91f6bab123c69072d3226b5a5b47a3f47993ffe2(
    value: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e1b070d38acba21af9e85835b7f9505be50edca1af2b7ad290db29d26ba43e1(
    completion_tokens: typing.Optional[jsii.Number] = None,
    prompt_tokens: typing.Optional[jsii.Number] = None,
    total_tokens: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbb7f6dd98655a57ace2277474663dd657f6cee9c3240d690e3ac8f55ac13697(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__840ce298a0bc1fb999a434f981e1e65d101bd12087b3f2612a39bad3edc90613(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c70699746506dd558549f075a6264324f040037434e4d0e45e629d7206702463(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81920271697ae42e098719be39b49bcd21415f983a883772a893c601ddaee6dd(
    agent: Agent,
    id: builtins.str,
    messages: typing.Sequence[IMemoryMessage],
    user_details: builtins.str,
    memory_type: MemoryType,
    metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aac0cdf9d3941968c7d1fb460252d03479b6f845bc6ba305a0180fce4bcdb71b(
    agent: Agent,
    user_details: typing.Optional[UserDetails] = None,
    thread_metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e7a3cc44823e0bd1074b9528f2bb8474d492df6b5ba552251aee89336e1ef0b(
    agent: typing.Any,
    thread_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e2e59e4d3fb03b2220fd16d51c1c03d26c81217aecbc900c19d672d4777df78(
    agent: typing.Any,
    thread_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__071fa16b048875d36af2a392e9eff4fa516175617a7f3aae94775da15db152fe(
    agent: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ba863dd52fe282ca9d0689fe6f56343e5b24266d122c7bc67f845d1680d79f4(
    agent: typing.Any,
    thread_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b9699df3510508554ad78d3dbc8cdcdf487a52850c8d30148c0a56992f7092(
    agent: Agent,
    thread_id: builtins.str,
    delta: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a51857d33f65b0aeb1e47a32821416678e02e9977e28bcf191def00e1de1385(
    _messages: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__371bbac48ab4303b8878745ba398512a7e9b2282fcdf6e8b9dd183b48b03488e(
    tool_call_results: typing.Sequence[ToolCallResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce51eb3bc0f66424dc100907e6b8645a78f014da089334b5683929638780555(
    instructions: AgentInstructions,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3820bd4aa216fc45c11762598045b405bfcb54d55efafa184a988ea86af9191c(
    input: IMemoryMessage,
    instructions: AgentInstructions,
    llm_provider: typing.Optional[LLMProvider] = None,
    files: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43486da039b91b09744e42b7b31901476e80049c84ef6f5a1e8c12946e5fca9a(
    _messages: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbe18b88e2660e8696c14f8f8e6d7a160be4e10f351309c88ad1ef59993830d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__480c9de0d56a727b6080606ffa19389e9a950f96e37f7f9a97200fd43981ce7f(
    value: LLMProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b4f084a61d1e17795026fdf0d8050b34b2f09eea03d6dfbb5809384ca99e18c(
    value: MemoryType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__061b6a073f962d6437ad5fafa99b961231c85f17625aa93e208f2ab144777953(
    value: typing.List[IMemoryMessage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c32eb529c2827d1d2d5e8eafc00e7e04a06df1f90b3e6d59b9a6ca51e3c2f77(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e929e79b7b59a892685c04ee233be1c732bd06c519447292cd87e096540451a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02fc4d33a917e0e6da8b5cedc5b5080dd3e329d0f585c0df82a28bed9dffacb4(
    id: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    metadata: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__351136a3c6205f7a6ca7271ab89aad37aacb8db2760c9193ab183f176568cf3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d98421cc7fa1aaa0659076e6f9368e1832f4c5e26a01072da4049125970ce3eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc2b13099f398ab092fae2f0168bb07bb9f7d8bec9f1d7da95a4675d1a787bef(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c7828f395f2671c9dc6587ce6ced2e48ec9fd11f89af3abbaa88d27472962b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f94fa5a937bc0bc1bcaa5ec59fd11112a5478a8d1b1dd6aef138b9d0d30a30f7(
    agent: Agent,
    report_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd35ef6de1c9651bc7d151f4efc8c1f0db15088148591bc019d5cea3dd7a8bc2(
    inner: typing.Optional[LLMTokens] = None,
    worker: typing.Optional[LLMTokens] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b3c2c0548517a31cc05aa0d6e475ade9f2a9dec96fd9a34d4bc3edbdabbd7d8(
    value: LLMTokens,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__298b6757d19c9f36a1df243177e78409e0c8bed0b905c0ebcaadf9a658276b48(
    value: LLMTokens,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5b1512c48e4c0a4b618d417e46f7c83b02989356f2412aa0eae9d63b626ce0e(
    name: typing.Optional[builtins.str] = None,
    type: typing.Optional[ToolCallType] = None,
    payload: typing.Any = None,
    tool_call_id: typing.Optional[builtins.str] = None,
    graph_approved: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fa618f493b9f124cef109e56d0f709f1b78016dbeb7ed55a9eb8cdc733dba99(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7cce041752b4e95ae25466ea39d32f51ec0301e64015b66ccf20bb9b23db25e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1940e09fdc14592acfce7003f99bcc770eb4b17ea62e53e30d6cbfd4d3d3707(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d9b994824033489cb2b3b806044405bcb06c1d72048f017c89bb422b16b35e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2059ec549c7384dd73be7be379faf6256c60a8ec7b55fdb9082692bbdc4bac54(
    value: ToolCallType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2debc725768136a46976eacab873877fdcc3efbb47c357e0973193213896e283(
    function_name: typing.Optional[builtins.str] = None,
    tool_call_id: typing.Optional[builtins.str] = None,
    payload: typing.Any = None,
    status_code: typing.Optional[jsii.Number] = None,
    result: typing.Any = None,
    is_success: typing.Optional[builtins.bool] = None,
    is_error: typing.Optional[builtins.bool] = None,
    is_local: typing.Optional[builtins.bool] = None,
    graph_approved: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fffc9823e52bc6b5b2f4aa72f7ed94614aad7d55b77f29de8574547aa73f28f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d03c735e160319bb8f7ff2043b62a07dc4ac091a1eb43c315b5be4128fcf92a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e12e85757c6557cdf77248e76a660df04102b8873b38236827fb882d1fa6439a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6923af36e794b8a5e685b7b5409aa9d63e048e0dde8cd5691e95250ecc939bf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e0ae8339ae925874f36d96caaf593a776e69a5def415e6cd597660d7e9c011e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2de087a3432f7b811bf4e98dd110380b61cb2d0cdcd014af55ea9c493c5e516(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b512e8cc2e3d13362bf29e552b8dff26b147cd4cf7b3fc2ac09efd5bd6e5bd8(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d7de4c43b1bcc39cb1dbd154a581a3c2a35f429555b50d12f81d0c6662c787a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e548be6ee41a966ad4e21e38458b2dc18fde679b9017e65e4f088b5b0d8c3580(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ad0f4ee2a8ddc83f945f89e3e6d713c8feaf7a7396b6b0435b3d8b01dbcd30d(
    configuration: Configuration,
    id: builtins.str,
    name: builtins.str,
    status: AgentStatus,
    organization_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be6af203e065a2e78c58c607874e4f2b9549d01bf66e0c563b5608336cef17cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a97a3b5f071d297b2aac0ac9cd726e2808c590639e3d4ef730ebb20756c9ec7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6027724ba7ab5ddecadd02d711569a0a4806fb8d2f046ecc2c2c7de68ce56b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9d4d1b15e40e35739183c3453f29a7c40b620d1efc759a89e3b8c4de7de7541(
    value: AgentStatus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7329314fccee5b9ac6ae21377aed20b3b58b8e4362fdaaf73481b787b7e9ccb1(
    id: builtins.str,
    first_name: typing.Optional[builtins.str] = None,
    last_name: typing.Optional[builtins.str] = None,
    email: typing.Optional[builtins.str] = None,
    additional_attributes: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f6ada61e6a476091ed3b896af2bb30412b2b21546fc1ec5dc82eced56299576(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ef5a82a2d4441cfe90fc0bba0711ecdcc126060fa2f12156f85a20ffb451f40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cc2c69cac56a0d499cc6b3fe05b85180c760de9596f0d95fa23899dacc67bc3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63911c605dfb76017dd111da3d0eb2759d4281365e645a3f6be942b03ef98003(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5446210d9c39a301ae2ac61861be554ae17304401c3de63f874241cda248e456(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ada04f0df01e9b462e0b973aee5f69eda17ab0f22e7345f33423f0acca9ad36(
    api_key: builtins.str,
    base_url: typing.Any = None,
    organization_id: typing.Optional[builtins.str] = None,
    should_reset_cache: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d89a5c88d1a2ed62ab765c38358d4adda81980f27657e34b4fe23fc61eca9217(
    llm_response: typing.Any,
    llm_provider: typing.Optional[LLMProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f435d83beaf0c0d7ba5fac4b14d448f0cd185e5af1d9aff81d5cfc4147374b61(
    tool_calls: typing.Sequence[ToolCall],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50de96ce44613a7f9044134d55c384c9cbc69918873535eed55a2d9c1f2cafbd(
    value: Agents,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f24bf46a0a96d6e069bcfdce151aa22264da15a80125c376dbad457bf91d1c0(
    value: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b3090998ec2c8bf3ca3548a14caaf6de4971b4c774603a66cee58c84379ce22(
    value: KnowledgeBases,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed3ca6ba27cec860aa869deb2eaf5d80822747214c50652c074c1fd995c12295(
    configuration: Configuration,
    id: builtins.str,
    name: builtins.str,
    organization_id: builtins.str,
    status: AgentStatus,
    delegation_type: AgentDelegationType,
    delegation_end_strategy: AgentDelegationEndStrategy,
    memory_type: MemoryType,
    memory_strategy: MemoryStrategy,
    instructions: AgentInstructions,
    access_scope: AgentAccessScope,
    source_nodes: typing.Sequence[ISourceNode],
    prompts: typing.Sequence[builtins.str],
    tools: typing.Optional[typing.Sequence[IAgentTool]] = None,
    _graph: typing.Optional[typing.Sequence[typing.Any]] = None,
    knowledge_bases: typing.Optional[typing.Sequence[KnowledgeBase]] = None,
    oas: typing.Any = None,
    version: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76b6cdc7eb3f36024a9c7754118375ea2bc37265acbea46b1152c2be8dc1072d(
    configuration: Configuration,
    agent_id: builtins.str,
    version: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1a4e9d238bcd6575542fe126282fe717dabbed97bd4b5d5f0906439f6debd49(
    tools: typing.Union[typing.Sequence[typing.Any], typing.Sequence[ILocalTool]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c763e76e4ecb7f7a77fe6c2dba333b644ea0abddac2e6c51dcad464709b85e(
    messages: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d16546c5c195ddef4391e46da78707938e8cd6d85040e33d40bc00a7120446e(
    input: typing.Optional[builtins.str] = None,
    thread_id: typing.Optional[builtins.str] = None,
    files: typing.Optional[typing.Sequence[builtins.str]] = None,
    use_worker: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b6b5a079da787d90c8d00f39c55c743d24f5ed3b67480566451861a7cd9ec9(
    tool_call_results: typing.Sequence[ToolCallResult],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__714c96a4dcb9157921296811cd8edcf9f84bf337706dac7c155320ff730bcbf2(
    operations: typing.Sequence[AgenticOperation],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3052afdc5d1b5b60445cf51a8879fbae2c027aae54558102a8ddab28b0963d8a(
    llm_response: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__773e3afa26f8b79fe00973c69c9983fbf523bfd2f52c02c0a473df8878934452(
    llm_provider: typing.Optional[LLMProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16872029ef2ca9a4aea1671c278ba6987a5be977e7311f29693d64313ecee69b(
    execution: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__083e27f1b35697c0dc5dd7bec052ea93d4a2fd3d2ee05d66ed6dfd7754537ddb(
    agent_id: typing.Optional[builtins.str] = None,
    ignore_cache: typing.Optional[builtins.bool] = None,
    raw_agent_data: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4315e33d477848f207013139088ddfe589c01ac5fe3ac40fe3887eda68a8c81(
    llm_tokens: Tokens,
    ai_model: typing.Optional[builtins.str] = None,
    source_node_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a96e0f5f5b59da335f12b0146213acc128807a6c3137a890fed7ed76a04562(
    llm_response: typing.Any,
    llm_inference_duration: typing.Optional[jsii.Number] = None,
    llm_provider: typing.Optional[LLMProvider] = None,
    source_node_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0958d9b6b5bfc800ebaa305539fc9dcd3ddf83cfd3fd110883c1698d297f6349(
    ignore_cache: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b9086ebd87942a70c9515c8974e8d9cab5772e11bb9fcb24a227d204d9923f9(
    agentic_interface: AgenticInterface,
    ignore_cache: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b76974a0e120e8cf7b77d0deb9b609235bfbb31f7bb65ad41e928422ab50a6b3(
    item_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c8bd19cf7540125e9b8a693e01fca0f177512d77ee3bab418456eeeef90162f(
    tool_calls: typing.Sequence[ToolCall],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e1ca0e533f7a6dc6cf8465ad7809ba4a450abee064ca45429a80a258a5e2e65(
    tool: ToolCall,
    payload_extension: typing.Any = None,
    is_multiple: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307c287f13e8189f59310f2e5a43f33ebb271c35e1502a531966c06bbe13ef32(
    tool_calls: typing.Sequence[ToolCall],
    payload_extension: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9740847c802111e1e7ecb2c787f36456764d241fc1e2b504620eb68c38f2beab(
    llm_provider: LLMProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d66a4c63458dd56f0d1fe482150d16c1346e9182e052917067713ac99d2be1d6(
    is_success: builtins.bool,
    result: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83adb98120d61cd6e5328f2ce8718542d01899c0e61b507458cf4b016b21ae58(
    user_details: UserDetails,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb6c11034237fb99d4afc18d0b8280c1e1f09ddaefe3eb074cf796e3b725e93(
    value: AgentAccessScope,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2acddc917b6b415bc14dfb9a7094cbd1b0319e93c3c4b3298f8cb5d9ec8206a7(
    value: Configuration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3661730e0df834b6194aee6c2237f76d066a302c1a032e7243ebd65edb9ce0e8(
    value: AgentDelegationEndStrategy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__595deaa3cabe2c927e992ffe08afc2aa88721124c5e9b438db838667096751f1(
    value: AgentDelegationType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__455c760f94e4fc5ed8c239f2c501ce6bf2eb3da9a89e20e6afdd569a617b8ab0(
    value: Graph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0b9d8c488cea43db21adbef0723558d2e632d07b3f9134efdeb872de791fa1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__729aa75df9167864d69d977ed37c2a63fa4c55e59a6a6595769ebe73e9503771(
    value: AgentInstructions,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d560d33d3a8d9ab2d5d84adacd04b2b8a4d5a0db676c32684e81f32478d93eaa(
    value: typing.List[KnowledgeBase],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__461357f98d7832be631c7539e2a04a98e371030637fbb3e8aea3024cef4960a9(
    value: LLMProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdc78718c4e88ad0687034fec3393a9b0dd4518c626fe4c60d2244cefaadbe37(
    value: typing.List[ILocalTool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f78a447686d7a170f7713415428aefc1544249c3da73e354d5f28a8917f689ae(
    value: MemoryStrategy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__805f0dbb3034522e5cd382a8d7f7c31a544db0bd26e45b0915f5b060aec59bed(
    value: MemoryType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22da1a47b30804817cea4f52e46761946f71d0d3436d3236d8ab8bbd3f9a2364(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed0174f671a90a524f265b28d5f9b948ecc8db890cd973390f9a408091d5cd2(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b78331aeaf11efbf7d44a1bd4ce9783ac8b3be074090b3f146520a09bb2ff99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6762bda91838241a6ee34d79cd8660a8ecf1de3ef553cabb0bd5130090bc15a3(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da71d0425a1a175452f028e91eec348b008ccd07d2c4ee25c3bc20232edadfb3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89bc6384ff613546183aa4186ddfac11deaaf2c2b3c4f43fd64f205dee4ad649(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1dff1fd2031b8c10437260cbaae7a1861611afa24cb0ca6b7126c825461d0aa(
    value: typing.List[ISourceNode],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f657c5abb4af14138072346cc87aee77138c4171cd0fc2bf21f903fd6c6299ce(
    value: AgentStatus,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d712115a2ab298e5d50d49c632fab67794a7409f1db441e663ee069fabba3ef8(
    value: typing.List[IAgentTool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddb249e972d9df7a7192823a54a5a782d4cb6f68f0a20fccf97eed51464257b7(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b67abdb1cba5becc669e94a301b7f98b7c0c0b097b682d08a910595e09541afb(
    value: typing.Optional[Execution],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89fe0c3654814305defb5190865bb0e7e7946de0fcd8a1902cc070067eebac5a(
    value: typing.Optional[Memory],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fabc29b53bc06a2b34ccc6428c40b29c90e1d5ec2e10f24d38c01e08691e82d(
    value: typing.Optional[UserDetails],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4da74b53547f0d8183511f5718499b6511ce5b76ea838b6bfb5d57375add4bc2(
    role: typing.Optional[typing.Sequence[builtins.str]] = None,
    goal: typing.Optional[typing.Sequence[builtins.str]] = None,
    general: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5d84d42689623385325eea71e52af47a908566ba3ada2cd4717f6db79a5e87e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f558d9b2c5b0e6e2b7040a982539f1e66ac8e30e733878d0543b8c798c7c55bb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c2d5459e4c3b9d304799f5aba566152b118f3bcb59d6669a2b6aa78e1ffdc35(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0421198e44ee66874d3a9ac56a6a99b6dc0f7eaeda89671242d6bf39f995ebb(
    id: builtins.str,
    name: builtins.str,
    summary: builtins.str,
    description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56a0933f379e823c8bd5a098d8cd0823f5da788f81e2cf82493bf3af19aa8278(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08bd8a9295a3f6bca09f1c529729d2e5992f248ccf768c476242ab5d1de6783b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31c02741e670a81628ccc3d3192b3361264d004315b890e135943817d1d096be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c3a97c5c727d70421a58b11a3058835df0a23f2a16d59f8cdba4de75a695978(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d00f579f8b6ee8853d6931c865ecc5f5725966e5904e8b93d829aa1ee31f452c(
    id: builtins.str,
    name: builtins.str,
    summary: builtins.str,
    description: builtins.str,
    id_to_use_on_graph: builtins.str,
    interface_id: builtins.str,
    is_function: builtins.bool,
    method: builtins.str,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16136fd2cfb48534b715b821da91ba0ebd50f4bc91c89635be6fd883c37e98c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a0c69767cc9b4f79e6e93e447d7eefbd6f542b65f5bf0159dc4a2903ae01ac8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__927a7c017e4de23bc0d60ebf1c164f160dab69aa503297714add886d9d80c55d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a6e530ff5690677acfbd9200f9c7d8708df4352809ed9f249e11bff282c541a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b51d5413b6076bc739a43c541f056c33398474a75b28756209fe0c1f6a177cd6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bea3b9c44e7fc9bb175da70e7039e2646073c61c4a79c867792dc37e52e95eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307dd21d55d2a3ba195730e39e0dc6189176bbd4eb3c27a4189933af67a0550e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__346d4f6c174a3dd581dd1a41074b805bf9d98571e4c31a3bee2fa180205bc608(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdd36b5fcfcdcd966eb42737d1b07a3aacc359e8a701825f48df5eddef35e432(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a23d2576a400dab8819022af0df7b0396c4f396b10977354c94cf8b3f91f68(
    source: builtins.str,
    execution_id: builtins.str,
    sub_executions: typing.Optional[typing.Sequence[builtins.str]] = None,
    memory_thread_id: typing.Optional[builtins.str] = None,
    task: typing.Optional[builtins.str] = None,
    triggered_by: typing.Optional[builtins.str] = None,
    skills: typing.Optional[typing.Sequence[builtins.str]] = None,
    status: typing.Optional[builtins.str] = None,
    duration: typing.Optional[jsii.Number] = None,
    ai_model: typing.Optional[builtins.str] = None,
    worker: typing.Optional[builtins.str] = None,
    ai_employee_id: typing.Optional[builtins.str] = None,
    api_calls_made: typing.Optional[typing.Sequence[typing.Any]] = None,
    result: typing.Optional[builtins.str] = None,
    llm_tokens: typing.Optional[Tokens] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d95f5139406915b7629e6ee233b89c646474c8a5ea1e849fee06932ef134cba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a8dcbeff1fb21fa64959e475f6a99ad147dc8d5183d962848f888c8f2a75f4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a332b8a7051546f589d0e1717fb96df2864e0e8fabda5d46747cda079c9d78ff(
    value: typing.List[typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c9bcfdd0bd94e084cdf3403b76f3a3457eccb58cc0646f90a34e3c95adc2ed9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef4bb1f3fb78bef421d677fc5bd2a6f9e2ccf1de4a9f7e4b827516baadfeeacd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d17923eae7d86c986a64e9e20660611129063467c27b2052d9e78fbd797f53c(
    value: Tokens,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7fcb9bb5c3e9f690c8f00f402f591d7ecfd6748464b65f0bc7d6852f695b157(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eb676f604f7a7cf535bdd88a1f0b69d2c3781ba8e971c5c05bf500023f3c452(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c34e1c35e1f7ac9512e4c3be386781893cc2bf24a48789961595854c7c4af5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04fde28064408d412417c483de95f3248a4af0c224b83e5f1c0d36c206da3898(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bc49a2aa9df8e476dffc5653b4b81f6d971462a831e8294eca730c2f1f2f095(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f2399a878cc9ea4c6c6b29530779d5ccbad71412b8a3b1d6ddbc0a087df240(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fafdf1312e9e78054c2e3e08be239b78dfe8357a2b387ebe2148831d6e885c72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4300e7ab3fef290648958095fdb7c6fb08e539776f8727ae23edd9718a6af893(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dce5845684332dad7cfa7cba737c0ea3e23af2a75ab31f91eb7b37698517d060(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95e6bc9fe2f387a7934d2bf3ca35a2874ee3a7d6187eb51f4212020bf9ffcaf1(
    source_node_type: builtins.str,
    finish_reason: typing.Optional[builtins.str] = None,
    provider: typing.Optional[LLMProvider] = None,
    model: typing.Optional[builtins.str] = None,
    duration: typing.Optional[jsii.Number] = None,
    prompt_tokens: typing.Optional[jsii.Number] = None,
    completion_tokens: typing.Optional[jsii.Number] = None,
    total_tokens: typing.Optional[jsii.Number] = None,
    function_name: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2b5bbd91446490960da2d273a10a10ec832d31eb07042199f29cc19fb03fe10(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee74b44a45f2cdc6dc717ac2c9e0963d46b80931fb6ae5c3c17263be8f14b20(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db12302f49a6391aeb5bd9d619a5f6b4618ba61b26b1520bc4ebc2dc6019c1df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e02a2996428bfdf63c01fb22bfd803a5983254bc5a0d521a785dae3fbabeec5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47b3f67277a37dc2e6dfea898a83aadaffb6c3ed15b3768ec7e931567f0d4b55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d68dd5305cc0e20650929ac52607eef81d44f5d872bbf721cdd5b31709cee9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60a70fae0cf0e4068388f776612812f1b94283597c2387d40f5ccf20f9bf961a(
    value: LLMProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cfc835d388478f4971cb8fca3b6a5073ecd664dfcfddd466717b98a08bdd455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f49c427ae78f6c816dbca40629bada77b3292d61e47efe333f5e77c41633abc1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass
