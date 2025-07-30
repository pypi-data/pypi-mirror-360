
def get_model(agent_name):
    mapping = {
        "CodeMaster": "gpt-4",
        "DocWriter": "claude-3-opus",
        "TesterAI": "mistral-medium",
        "SelfHealingAgent": "gpt-4-turbo",
        "MemoryAgent": "gpt-3.5-turbo"
    }
    return mapping.get(agent_name, "gpt-4")
