#!/usr/bin/env python3
# -*- coding:utf8 -*-
from j2_template import render_template

# 示例上下文
context = {
    'title': 'Test Page',
    'greeting': 'Hello, World!',
    'description': 'This is a Jinja2 template rendered in Python.'
}

# 渲染模板并输出到控制台
render_template(template_file='test/test_template.html', context=context)
