# Rancher AI Assistant backend

This chart bootstraps the backend required for the Rancher AI Assistant to run.  

- Ollama
- MCPO
- ToolBox
- LLMProxy

## How to configure

A single parameters is required `rancherUrl` which is the public IP of your Rancher.

```yaml
rancherUrl: "https://rancher.rd.localhost"
```

Other parameters can be customised in the `values`

```yaml
ollama:
  gpu:
    # -- Enable GPU integration
    enabled: false
    
    # -- GPU type: 'nvidia' or 'amd'
    type: 'nvidia'
    
    # -- Specify the number of GPU to 1
    number: 1
   
  # -- List of models to pull at container startup
  models:
    run: 
      - qwen3:1.7b
    pull:
      - qwen3:1.7b
      - qwen3:4b
```
