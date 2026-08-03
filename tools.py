"""SIA tool-use layer: registry + agent loop that lets the model call tools.
Format: the model emits [[tool:name(args)]]; the loop executes and appends the result.
"""
import ast
import datetime as _dt
import os
import re
from pathlib import Path

import torch

TOOL_RE = re.compile(r"\[\[tool:(\w+)\((.*?)\)\]\]", re.S)


def safe_eval(expr: str):
    tree = ast.parse(expr, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"unsupported expression node: {type(node).__name__}")
    ns = {"__builtins__": {}}
    return eval(compile(tree, "<tool>", "eval"), ns)


def calc(expr: str) -> str:
    return str(safe_eval(expr))


def now() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def file_read(path: str) -> str:
    p = Path(path).resolve()
    if not str(p).startswith(os.getcwd()):
        return "ERR: path outside workdir"
    return p.read_text(encoding="utf-8", errors="ignore")[:4000]


def file_write(path: str, content: str) -> str:
    p = Path(path).resolve()
    if not str(p).startswith(os.getcwd()):
        return "ERR: path outside workdir"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} chars to {path}"


def list_files(path: str = ".") -> str:
    return "\n".join(sorted(os.listdir(path)))[:2000]


DEFAULT_TOOLS = {
    "calc": calc,
    "now": now,
    "file_read": file_read,
    "file_write": file_write,
    "list_files": list_files,
}


def run_agent(model, tokenizer, prompt: str, tools=None, max_rounds: int = 3, max_new: int = 64):
    """Model-driven tool loop: generate -> parse [[tool:name(args)]] -> execute -> continue."""
    tools = tools or DEFAULT_TOOLS
    log = []
    current = prompt
    for r in range(max_rounds):
        ids = tokenizer.encode(current)
        input_ids = torch.tensor([ids], dtype=torch.long)
        out = model.generate_text(input_ids, max_new=max_new, temp=0.6, top_k=40)
        text = tokenizer.decode(out[0].tolist())
        calls = TOOL_RE.findall(text)
        if not calls:
            log.append(("answer", text))
            return {"rounds": r + 1, "answer": text, "log": log}
        for name, argstr in calls:
            fn = tools.get(name)
            if fn is None:
                result = f"ERR: unknown tool {name}"
            else:
                try:
                    result = fn(argstr)
                except Exception as e:  # noqa
                    result = f"ERR: {e}"
            log.append(("tool", f"{name}({argstr}) -> {result}"))
            current = f"{current}\n[tool_result] {name} returned: {result}"
    return {"rounds": max_rounds, "answer": "max rounds", "log": log}
