#!/usr/bin/env python3
# -*- coding:utf8 -*-
import os
import jinja2
import logging

logger = logging.getLogger(__name__)


def render_template(template_str=None, context=None, dry_run=False, output_file=None):
    """渲染 Jinja2 模板并输出到文件或打印到控制台"""
    try:
        # 创建 Jinja2 环境
        template_env = jinja2.Environment(
            loader=jinja2.DictLoader({'template': template_str}),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        template = template_env.get_template('template')

        # 渲染模板
        rendered_content = template.render(context or {})

        # 如果是 dry run，打印渲染内容但不保存
        if dry_run:
            logger.debug("Dry-run 模式，输出渲染内容：")
            print(rendered_content)
            return

        # 输出到文件
        if output_file:
            with open(output_file, 'w') as f:
                f.write(rendered_content)
            logger.debug("渲染结果已保存到 {}".format(output_file))
        else:
            # 否则打印到控制台
            print(rendered_content)

    except jinja2.TemplateError as e:
        logger.error(f"模板错误: {e}")
    except Exception as e:
        logger.error(f"模板渲染过程中发生错误: {e}")
