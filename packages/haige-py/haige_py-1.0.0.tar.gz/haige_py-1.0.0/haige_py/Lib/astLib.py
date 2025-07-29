import ast
import astunparse  # 需要安装：pip install astunparse


def replace_var_ast(file_path, var_name, new_value):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 解析为 AST
    tree = ast.parse(code)

    # 遍历 AST，找到目标变量并修改
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    # 修改赋值语句的值为新值（需是合法的 Python 表达式）
                    node.value = ast.parse(repr(new_value)).body[0].value

    # 将 AST 转换回代码
    new_code = astunparse.unparse(tree)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_code)
