import ast

def extract_graph_from_code(code):
    tree = ast.parse(code)
    graph = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            graph.append({
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node),
            })
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            graph.append({
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node),
            })
            self.generic_visit(node)

    Visitor().visit(tree)
    return graph
