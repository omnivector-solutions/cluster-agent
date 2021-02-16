# armada-agent

## Secrets

## Setup parameters

1. Setup env
  ```bash
  virtualenv -p python3 env
  source env/bin/activate
  pip3 install -e .
  ```

2. Setup parameters on AWS SSM
  ```bash
  armada-agent-config <stage> # e.g. armada-agent-config dev
  ```

## Local usage example

```python
from armada_agent.agent import ScraperAgent

stage = "dev" # define stage name here. Default is "dev"

agent = ScraperAgent(stage)

agent.update_partition()
agent.update_node()
```

## Deploy
