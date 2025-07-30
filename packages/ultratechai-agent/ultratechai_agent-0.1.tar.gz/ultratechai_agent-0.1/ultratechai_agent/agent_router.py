
def route(prompt):
    if "sənəd" in prompt or "doc" in prompt:
        return "DocWriter"
    elif "test" in prompt or "sınaq" in prompt:
        return "TesterAI"
    elif "terminal" in prompt:
        return "TerminalExec"
    else:
        return "CodeMaster"
