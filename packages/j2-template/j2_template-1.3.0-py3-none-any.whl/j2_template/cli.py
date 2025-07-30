#!/usr/bin/env python3
# -*- coding:utf8 -*-
import argparse
import logging
import json
import os
import sys
import yaml

from .core import render_template
from .__version__ import __version__


def setup_logging(log_level='info'):
    """设置日志记录"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        logging.error("无效的日志级别: %s" % log_level)
        return
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Jinja2 模板渲染工具")

    parser.add_argument('--template-file', type=str, help="Jinja2 模板文件路径")
    parser.add_argument('--template-content', type=str, help="Jinja2 模板内容")
    parser.add_argument('--output', type=str, help="输出渲染结果的文件路径")
    parser.add_argument('--dry-run', action='store_true', help="只进行渲染预览，不保存到文件")
    parser.add_argument('--context', type=str, help="上下文数据，JSON 格式的字符串")
    parser.add_argument('--context-file', type=str, help="上下文数据文件路径，支持 JSON 或 YAML 格式")
    parser.add_argument('--log-level', type=str, default='info',
                        choices=['debug', 'info', 'warning', 'error', 'critical'], help="设置日志级别")
    parser.add_argument('--version', action='version', version='%s' % __version__, help="显示版本信息")
    args = parser.parse_args()

    # 参数验证
    if args.template_file and not os.path.isfile(args.template_file):
        raise FileNotFoundError(args.template_file)
    if args.output and os.path.exists(args.output) and not os.access(args.output, os.W_OK):
        raise PermissionError(args.output)
    if args.context_file and not os.path.isfile(args.context_file):
        raise FileNotFoundError(args.context_file)

    return parser, args


def load_context_from_file(file_path):
    """从文件中加载上下文数据，支持 JSON 或 YAML 格式"""
    _, ext = os.path.splitext(file_path)
    if ext.lower() in ['.json', '.js']:
        with open(file_path, 'r') as f:
            return json.load(f)
    elif ext.lower() in ['.yaml', '.yml']:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        logging.error("不支持的文件格式: %s" % file_path)
        return {}


def load_context_from_env():
    """从环境变量中加载上下文数据"""
    context_env_var = os.getenv('J2_TEMPLATE_CONTEXT')
    if context_env_var:
        try:
            return json.loads(context_env_var)
        except json.JSONDecodeError as e:
            logging.error(f"无法解析环境变量中的上下文数据: {e}")
    return {}


def main():
    """命令行主函数"""
    parser, args = parse_arguments()
    setup_logging(args.log_level)  # 传入日志级别参数

    context = {}
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            logging.error(f"无法解析上下文数据: {e}")
            return

    if args.context_file:
        context_from_file = load_context_from_file(args.context_file)
        context.update(context_from_file)

    context_from_env = load_context_from_env()
    context.update(context_from_env)

    template_str = None
    if args.template_content:
        template_str = args.template_content
    elif args.template_file:
        with open(args.template_file, 'r') as f:
            template_str = f.read()
    elif not sys.stdin.isatty():
        template_str = sys.stdin.read()
    else:
        parser.print_help()
        return

    render_template(
        template_str=template_str,
        context=context,
        dry_run=args.dry_run,
        output_file=args.output
    )
