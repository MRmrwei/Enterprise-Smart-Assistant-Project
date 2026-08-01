from graphs.state import AgentState


def init_node(state: AgentState):
    
    
    print("-------------init_node-----------------")
    print(f"文档的路径：{state.get('intentions', None).file_path}")
    
    return state