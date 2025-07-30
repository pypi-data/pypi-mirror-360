# j2_template

## Introduction
This is a template for creating a new Jinja2 template.

实现了一个类似 Ansible 的 template 模块工具，具备以下功能：

- 渲染 Jinja2 模板。
- 支持命令行界面（CLI），可以通过传递模板文件、上下文、输出文件等参数来进行模板渲染。
- 支持 `dry-run` 模式，避免实际输出文件，仅打印渲染结果。
- 支持通过 API 调用，能够将功能集成到其他 Python 项目中。
- 使用 `argparse` 和 `logging` 模块来实现命令行参数解析和日志记录，确保工具的易用性和可调试性。

## Usage

模版文件：`template.j2`

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ greeting }}</h1>
    <p>{{ description }}</p>
</body>
</html>
```

CLI 模式：

```shell
#从文件读取模板和上下文数据：
j2_template --template-file template.j2 --context-file context.json
j2_template --template-file template.j2 --context-file context.json --log-level info

# 从标准输入读取模板内容：
cat template.j2 | j2_template --context '{"title": "Test", "greeting": "Hello!", "description": "This is a description."}' --output result.txt --log-level debug

# 使用环境变量提供上下文数据：
export J2_TEMPLATE_CONTEXT='{"title": "Test", "greeting": "Hello!", "description": "This is a description."}'
j2_template --template-file template.j2 --output result.txt
```


API 模式：
```
from j2_template import render_template

# 示例上下文
context = {
    'title': 'Test Page',
    'greeting': 'Hello, World!',
    'description': 'This is a Jinja2 template rendered in Python.'
}

# 渲染模板并输出到控制台
render_template(template_file='test/test_template.html', context=context)
```


## wiki

https://www.yuque.com/fcant/python/tb7rutgf9ac5lhk1#