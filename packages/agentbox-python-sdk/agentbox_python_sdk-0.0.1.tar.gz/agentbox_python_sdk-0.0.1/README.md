## What is AgentBox?
[AgentBox](https://agentbox.cloud/) is an infrastructure that allows you to run AI-generated code in secure isolated android sandboxes in the cloud.

## Run your first Sandbox

### 1. Install SDK

```
pip install agentbox-python-sdk
```

### 2. Get your AgentBox API key
1. Sign up to AgentBox [here](https://agentbox.cloud).
2. Get your API key [here](https://agentbox.cloud/dashboard?tab=keys).
3. Set environment variable with your API key 

### 3. Execute code with code interpreter inside Sandbox

```py
from agentbox import Sandbox

with Sandbox() as sandbox:
    sandbox.run_code("x = 1")
    execution = sandbox.run_code("x+=1; x")
    print(execution.text)  # outputs 2
```

### 4. Check docs
Visit [AgentBox documentation](https://agentbox.cloud/docs).
