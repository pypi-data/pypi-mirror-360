import re
import os

class Node:
    pass

class Element(Node):
    def __init__(self, tag, attrs, children):
        self.tag = tag
        self.attrs = attrs
        self.children = children

class Text(Node):
    def __init__(self, text):
        self.text = text

class Expression(Node):
    def __init__(self, code):
        self.code = code.strip()

def parse_jsx(code):
    code = code.strip()

    def parse_element(s, pos=0):
        tag_match = re.compile(r"<((?:\w+\.)?\w+)([^>]*)>").match(s, pos)
        if not tag_match:
            return None, pos

        tag = tag_match.group(1)
        raw_attrs = tag_match.group(2).strip()
        attrs = dict(re.findall(r'(\w+)="(.*?)"', raw_attrs))
        pos = tag_match.end()

        children = []
        while True:
            close_tag = f"</{tag}>"
            close_pos = s.find(close_tag, pos)
            if close_pos == -1:
                raise ValueError(f"No closing tag found for {tag}")

            next_open = s.find("<", pos)
            if next_open == -1 or next_open >= close_pos:
                text = s[pos:close_pos]
                if text.strip():
                    parts = re.split(r"(\{.*?\})", text)
                    for part in parts:
                        if not part.strip():
                            continue
                        if part.startswith("{") and part.endswith("}"):
                            children.append(Expression(part[1:-1]))
                        else:
                            children.append(Text(part))
                pos = close_pos + len(close_tag)
                break
            else:
                if next_open > pos:
                    text = s[pos:next_open]
                    if text.strip():
                        parts = re.split(r"(\{.*?\})", text)
                        for part in parts:
                            if not part.strip():
                                continue
                            if part.startswith("{") and part.endswith("}"):
                                children.append(Expression(part[1:-1]))
                            else:
                                children.append(Text(part))
                    pos = next_open

                child, new_pos = parse_element(s, pos)
                if child is None:
                    break
                children.append(child)
                pos = new_pos

        return Element(tag, attrs, children), pos

    root, endpos = parse_element(code)
    return root

def render_node(node, indent=0):
    pad = "    " * indent
    if isinstance(node, Text):
        text = node.text.strip()
        if not text:
            return ""
        return repr(text)
    elif isinstance(node, Expression):
        return node.code
    elif isinstance(node, Element):
        tag = node.tag
        if '.' not in tag:
            tag = "html." + tag

        attr_lines = []
        for k, v in node.attrs.items():
            attr_lines.append(f'{"    "*(indent+1)}"{k}": "{v}",')
        attr_str = "{\n" + "\n".join(attr_lines) + f"\n{'    '*indent}}}" if attr_lines else "{}"

        children_rendered = [render_node(c, indent+1) for c in node.children]
        children_rendered = [c for c in children_rendered if c]

        if len(children_rendered) == 0:
            return f"{tag}(\n{attr_str},\n{'    '*(indent+1)}\"\"\n{pad})"
        elif len(children_rendered) == 1:
            return f"{tag}(\n{attr_str},\n{'    '*(indent+1)}{children_rendered[0]}\n{pad})"
        else:
            children_tuple = ",\n".join(f"{'    '*(indent+2)}{c}" for c in children_rendered)
            return f"{tag}(\n{attr_str},\n{'    '*(indent+1)}(\n{children_tuple},\n{'    '*(indent+1)})\n{pad})"
    else:
        raise TypeError("Unknown node type")

def transform_jsx_to_function_call(code: str) -> str:
    root = parse_jsx(code)
    return render_node(root, indent=1)

def Lilliepy_Tags(src_folder: str, dist_folder: str):
    if not os.path.exists(dist_folder):
        os.makedirs(dist_folder)

    for filename in os.listdir(src_folder):
        if filename.endswith(".x.py"):
            process_file_in_folder(filename, src_folder, dist_folder)

def process_file_in_folder(filename: str, src_folder: str, dist_folder: str):
    src_path = os.path.join(src_folder, filename)
    dist_path = os.path.join(dist_folder, filename)

    with open(src_path, "r", encoding="utf-8") as f:
        code = f.read()

    component_funcs = re.findall(r"@component\s*\ndef (\w+)\(", code)
    if not component_funcs:
        print(f"❌ No @component functions found in {filename}")
        return

    for func_name in component_funcs:
        pattern = re.compile(rf"(def {func_name}\(.*?\):)(.*?)(?=^def |\Z)", re.DOTALL | re.MULTILINE)
        func_match = pattern.search(code)
        if not func_match:
            continue

        func_body = func_match.group(2)
        body_start = func_match.start(2)

        return_pattern = re.compile(r"(return\s*\(\s*)(<.*?>.*?</.*?>)(\s*\))", re.DOTALL)
        new_func_body = func_body

        for ret_match in return_pattern.finditer(func_body):
            jsx_code = ret_match.group(2).strip()
            try:
                transpiled = transform_jsx_to_function_call(jsx_code)
                new_func_body = new_func_body.replace(jsx_code, "\n" + transpiled + "\n")
            except Exception as e:
                print(f"⚠️ Error transpiling JSX in {func_name}: {e}")

        code = code[:body_start] + new_func_body + code[func_match.end(2):]

    with open(dist_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Transformed {filename} → {dist_path}")