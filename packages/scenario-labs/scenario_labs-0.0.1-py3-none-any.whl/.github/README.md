# Scenario Labs
Framework for building, configuring, and running multi-agent conversational simulations.


## Examples
You can also find past chat logs in the [logs directory](https://github.com/christopherwoodall/scenario-labs/tree/main/logs).

![](docs/agents-example.png)


## Getting Started
[Set the enviromental variable](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var) `XAPI_API_KEY` to your [xAI API key](https://x.ai/api).

```bash
git clone https://github.com/christopherwoodall/scenario-labs Labs.git
cd scenario-labs
pip install -e ".[developer]"

scenario-labs
```

You can also run simulations in parallel with the following command:

```bash
for i in {1..9}; do scenario-labs & done; wait
```

## Configuration
You can configure the simulation by editing the `starbound_config.yaml` file. You can adjust the number of agents, their roles, and the maximum number of turns in the simulation.

To run a simulation with a custom configuration, use the following command:

```bash
scenario-labs --config configs/prison_config.yaml
```


## Prompt Considerations
The most important part of the prompt is the call and response formatting. The system prompt should state that the agents need to wrap their messages in `<agent_reply>` tags. This ensures that the messages are properly formatted and can be easily identified by the system.

The following is a good way of achieving this:

```
All messages must begin with your character's name followed by a colon. For example: 
"Lily Chen: I hope you're having a great day!"

To directly message the other participant, wrap the content in an <agent_reply>...</agent_reply> tag. 
Inside the tag, write the character name, a colon, then the message. For example: 
"<agent_reply>Lily Chen: Have you ever tried crypto investing?</agent_reply>"

The following agents are involved:
- "Lily Chen"
- "Michael"

```
