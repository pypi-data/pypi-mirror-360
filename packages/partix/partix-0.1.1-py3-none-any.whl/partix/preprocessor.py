import json
import re
from jsonpath_ng import parse


def alias_preprocess(text):
    alias_map = {}
    lines = text.splitlines()
    processed_lines = []
    for line in lines:
        m = re.match(r'@(\w+)\s+as\s+@(\w+)', line)
        if m:
            original, alias = m.group(1), m.group(2)
            alias_map[alias] = original
            continue

        for alias, original in alias_map.items():
            line = re.sub(r'@' + re.escape(alias) + r'\b', '@' + original, line)

        processed_lines.append(line)

    return '\n'.join(processed_lines)

def body_preprocess(body, dlt="---"):
    return body.split(dlt)

def ns_preprocess(block, import_stmt):
    # 解析 import ns 语句
    pattern = r'import\s+ns\s+([\w\.]+)'
    m = re.match(pattern, import_stmt)
    if not m:
        return block

    ns_path = m.group(1).strip()
    ns_json_file = f'{ns_path.split(".")[0]}.json'
    with open(ns_json_file, "r", encoding="utf-8") as f:
        ns_json = json.load(f)

    sub_ns_list = ns_path.split(".")
    sub_ns_path = ""
    alias = []

    for sub_ns in sub_ns_list:
        sub_ns_path += f"{sub_ns}."
        jsonpath_expr = parse(f'{sub_ns_path}.*')
        matches = jsonpath_expr.find(ns_json)
        for match in matches:
            key = match.path.fields[0] if hasattr(match.path, 'fields') else None
            value = match.value
            if isinstance(value, str):
                new_ns_stmt = f"@{key} as @{value}"
                if new_ns_stmt not in alias:
                    alias.append(new_ns_stmt)

    alias_block = "\n".join(alias)
    if alias_block:
        # 以换行分隔开，方便阅读
        return alias_block + "\n" + block
    else:
        return block

def ctx_preprocess(block: str, ctx_stmt: str) -> str:
    pattern = r'import\s+ctx\s+(\w+)'
    m = re.match(pattern, ctx_stmt)
    if not m:
        return block

    ctx_file = m.group(1).strip() + ".ctx"
    with open(ctx_file, "r", encoding="utf-8") as f:
        ctx_content = f.read()

    if ctx_content:
        return ctx_content + "\n" + block
    else:
        return block


def scope_preprocess(text):
    pattern = re.compile(r'\{(.*?)}', re.DOTALL)
    output = []
    last_end = 0

    for m in pattern.finditer(text):
        start, end = m.span()
        block_content = m.group(1).strip()

        parts = [p.strip() for p in block_content.split('---')]
        if len(parts) < 2:
            combined_block = block_content
        else:
            prefix = parts[0]
            body_parts = parts[1:]
            combined_parts = []
            for part in body_parts:
                combined_parts.append(prefix + "\n" + part)
            combined_block = "\n---\n".join(combined_parts)

        output.append(text[last_end:start])  # 大括号之前的文本
        output.append("\n---\n")              # 先插入分隔符
        output.append(combined_block)         # 再添加块内容

        last_end = end

    output.append(text[last_end:])
    return "".join(output)



def program_preprocess(program):
    ns_import_stmts = []
    ctx_import_stmts = []
    body_stmts = []

    ns_pattern = re.compile(r'^import\s+ns\s+([\w.]+)$')
    ctx_pattern = re.compile(r'^import\s+ctx\s+(\w+)$')
    lines = program.splitlines()
    for line in lines:
        line = line.strip()
        ns_match = ns_pattern.match(line)
        if ns_match:
            ns_import_stmts.append(line)
            continue
        ctx_match = ctx_pattern.match(line)
        if ctx_match:
            ctx_import_stmts.append(line)
            continue
        body_stmts.append(line)

    return ns_import_stmts, ctx_import_stmts, '\n'.join(body_stmts)

def preprocess(program):
    processed_blocks = []
    ns, ctx, body = program_preprocess(program)
    body = scope_preprocess(body)
    blocks = body_preprocess(body)

    for block in blocks:
        if ctx:
            block = ctx_preprocess(block, ctx[0])
        if ns:
            block = ns_preprocess(block, ns[0])
        block = alias_preprocess(block)
        if block:
            processed_blocks.append(block)

    return processed_blocks

def test():
    program = """
@test0 test0
{
@Scope "1"
---
@Test1_1 "1_1"
@Test1_2 "1_2"
}
{
@Scope "2"
---
@Test2 "2"
}
---
@f "test()"
"""

    result = scope_preprocess(program)
    print("After scope_preprocess:")
    print(result)


if __name__ == "__main__":
    test()