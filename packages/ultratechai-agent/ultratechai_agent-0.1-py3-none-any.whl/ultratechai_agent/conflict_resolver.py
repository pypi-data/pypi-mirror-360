
def resolve_conflict(agent_opinions):
    priority = {'security': 3, 'correctness': 2, 'performance': 1, 'style': 0}
    ranked = sorted(agent_opinions, key=lambda x: priority.get(x.get('focus'), 0), reverse=True)
    return ranked[0]
