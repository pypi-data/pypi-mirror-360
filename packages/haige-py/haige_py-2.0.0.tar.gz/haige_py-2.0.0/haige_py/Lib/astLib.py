import ast
import astunparse  # 需要安装：pip install astunparse

import ast
import astunparse


def replace_var_ast(file_path, var_name, new_value):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 解析为 AST
    tree = ast.parse(code)

    # 标志变量是否找到
    var_found = False

    # 遍历 AST，找到目标变量并修改
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    # 修改变量的值
                    node.value = ast.parse(repr(new_value)).body[0].value
                    var_found = True

    # 如果变量不存在，则在文件末尾添加新的赋值语句
    if not var_found:
        # 创建新的赋值节点
        new_assign = ast.Assign(
            targets=[ast.Name(id=var_name, ctx=ast.Store())],
            value=ast.parse(repr(new_value)).body[0].value
        )

        # 将新节点添加到模块体的末尾
        if isinstance(tree, ast.Module):
            tree.body.append(new_assign)
        else:
            # 如果不是模块，创建一个新模块包含原始代码和新赋值
            new_tree = ast.Module(body=[tree, new_assign])
            tree = new_tree

    # 将 AST 转换回代码
    new_code = astunparse.unparse(tree)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_code)
