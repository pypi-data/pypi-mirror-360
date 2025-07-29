from langgraph.graph.state import CompiledStateGraph


def get_graph_draw_mermaid_png(
    graph: CompiledStateGraph, output_path: str = "graph.png"
):
    """
    获取 LangGraph 状态图的 Mermaid PNG 可视化并保存到文件。

    Args:
        graph (CompiledStateGraph): 要可视化的已编译 LangGraph 状态图实例。
        output_path (str): 保存 PNG 图像的文件路径。
    """
    png_data = graph.get_graph(xray=True).draw_mermaid_png()
    with open(output_path, "wb") as f:
        f.write(png_data)
