# armada-agent

## Secrets

## Setup parameters

1. Setup env
  ```bash
  virtualenv -p python3 env
  source env/bin/activate
  pip3 install -e .
  ```

2. Setup `.env` parameters
  ```bash
  agentconfig
  ```

## Local usage example

1. Run app
  ```bash
  agentrun
  ```

Outputs:
  ```bash
  INFO:     Started server process [8798]
  INFO:     Waiting for application startup.
  INFO:     Run collecting
  INFO:     Depends(get_agent)
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
  ```

2. Make local request
  ```bash
  curl http://localhost:8080/health
  ```

Outputs:
  ```json
  {"status":"ok","message":""}
  ```

## Deploy
