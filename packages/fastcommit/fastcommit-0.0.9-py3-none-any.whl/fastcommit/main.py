"""
FastCommit 命令行入口
"""

import argparse
import sys
import json
import signal
from .core import FastCommit, OpenAIProvider
from .config import ConfigManager, APIConfig


def show_config_help():
    """显示配置帮助信息"""
    print(
        """
配置 FastCommit API:

支持的服务提供商:
- 通义千问: https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen (推荐)
- DeepSeek: https://api-docs.deepseek.com/zh-cn/
- 自定义: 支持任何 OpenAI 兼容的 API 服务

方法1: 交互式配置 (推荐)
fsc config

方法2: 使用配置命令
# 通义千问配置示例 (推荐)
fsc config --api-key your_qwen_api_key
fsc config --api-base https://dashscope.aliyuncs.com/compatible-mode/v1/
fsc config --model qwen-plus

# DeepSeek 配置示例
fsc config --api-key your_deepseek_api_key
fsc config --api-base https://api.deepseek.com/
fsc config --model deepseek-reasoner

# 自定义配置示例
fsc config --api-key your_custom_api_key
fsc config --api-base https://your-custom-api.com/v1/
fsc config --model your-custom-model

# 通用配置
fsc config --language en

查看当前配置:
fsc config --show
"""
    )


def configure_api(args):
    """配置 API"""
    try:
        config_manager = ConfigManager()

        # 显示当前配置
        if args.show:
            config_info = config_manager.get_config_info()
            print("当前配置:")
            for key, value in config_info.items():
                print(f"  {key}: {value}")
            return

        # 加载现有配置
        config = config_manager.load_config()

        # 更新配置
        if args.api_key:
            config.api_key = args.api_key
            print("API Key 已更新")

        if args.api_base:
            config.api_base = args.api_base
            print(f"API Base URL 已更新为: {args.api_base}")

        if args.model:
            config.model = args.model
            print(f"模型已更新为: {args.model}")

        if args.language:
            config.language = args.language
            print(f"语言已更新为: {args.language}")

        # 如果没有提供任何参数,进入交互式配置
        if not any([args.api_key, args.api_base, args.model, args.language, args.show]):
            config = config_manager.update_config_interactive()

        # 保存配置
        if any([args.api_key, args.api_base, args.model, args.language]) or not args.show:
            config_manager.save_config(config)
            print(f"配置已保存到: {config_manager.config_file}")

    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
        return
    except Exception as e:
        print(f"配置错误: {e}")


def show_staged_files():
    """显示暂存区文件"""
    try:
        fc = FastCommit()
        summary = fc.get_staged_files_summary()

        if "error" in summary:
            print(f"错误: {summary['error']}")
            return

        if "message" in summary:
            print(summary["message"])
            return

        print(f"暂存区文件 ({summary['total_files']} 个):")
        for change in summary["changes"]:
            print(f"  {change['type']}: {change['file']}")

    except Exception as e:
        print(f"错误: {e}")


def manage_prompt(args):
    """管理 prompt 文件"""
    try:
        import os

        # 获取当前模块目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 确定语言
        language = getattr(args, "language", "en")

        if language == "zh" or language == "zh-cn":
            prompt_file = os.path.join(current_dir, "system_prompt_zh.txt")
            lang_name = "中文"
        else:
            prompt_file = os.path.join(current_dir, "system_prompt_en.txt")
            lang_name = "English"

        # 显示当前 prompt
        if args.show:
            print(f"当前 {lang_name} 系统提示词:")
            print("=" * 50)
            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)
            except FileNotFoundError:
                print("文件不存在")
            except Exception as e:
                print(f"读取文件失败: {e}")
            print("=" * 50)
            return

        # 编辑 prompt
        if args.edit:
            try:
                # 使用系统默认编辑器打开文件
                import subprocess

                # 尝试使用不同的编辑器
                editors = [
                    "vim",  # 默认使用 vim
                    os.environ.get("EDITOR", ""),
                    "nano",
                    "vi",
                    "code",  # VS Code
                    "subl",  # Sublime Text
                ]

                editor_found = False
                for editor in editors:
                    if editor:
                        try:
                            print(f"正在使用 {editor} 编辑 {lang_name} 提示词...")
                            subprocess.run([editor, prompt_file], check=True)
                            editor_found = True
                            print(f"✅ {lang_name} 提示词已更新")
                            break
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue

                if not editor_found:
                    print("未找到合适的编辑器,请手动编辑文件:")
                    print(f"文件路径: {prompt_file}")

            except Exception as e:
                print(f"编辑文件失败: {e}")
            return

        # 如果没有指定操作,显示帮助
        print(f"Prompt 管理工具")
        print(f"")
        print(f"查看当前 {lang_name} 提示词:")
        print(f"  fsc prompt --show --language {language}")
        print(f"")
        print(f"编辑 {lang_name} 提示词:")
        print(f"  fsc prompt --edit --language {language}")
        print(f"")
        print(f"支持的语言: en (英文), zh (中文)")
        print(f"")
        print(f"文件位置:")
        print(f"  中文: {os.path.join(current_dir, 'system_prompt_zh.txt')}")
        print(f"  英文: {os.path.join(current_dir, 'system_prompt_en.txt')}")

    except Exception as e:
        print(f"错误: {e}")


def generate_commit_message():
    """生成 commit message"""
    try:
        # 加载配置
        config_manager = ConfigManager()

        # 检查是否首次运行
        if not config_manager.is_configured():
            print("检测到首次运行,需要配置 API 信息...")
            config = config_manager.setup_first_time()
        else:
            config = config_manager.load_config()

        # 验证配置
        if not config.api_key:
            print("错误: API Key 未配置")
            print("\n请先配置 API:")
            show_config_help()
            return

        # 创建 AI 提供者 (这里需要根据实际的AI提供者类进行调整)
        # 假设使用 OpenAI 兼容的接口
        ai_provider = OpenAIProvider(api_key=config.api_key, base_url=config.api_base, model=config.model)

        # 创建 FastCommit 实例
        fc = FastCommit(ai_provider)

        # 显示暂存区修改文件
        print("正在分析暂存区修改...")

        # 显示使用的模型
        print(f"使用模型: {config.model}")

        # 获取并显示修改的文件
        summary = fc.get_staged_files_summary()
        if "error" in summary:
            print(f"错误: {summary['error']}")
            return
        if "message" in summary:
            print(summary["message"])
            return

        # 用绿色显示修改的文件
        print(f"\n修改的文件 ({summary['total_files']} 个):")
        for change in summary["changes"]:
            # ANSI 绿色代码: \033[32m, 重置代码: \033[0m
            print(f"  \033[32m{change['type']}: {change['file']}\033[0m")

        # 生成 commit message
        print("\n生成的 Commit Message:")
        print("=" * 50)

        # 流式生成并显示
        commit_msg = fc.generate_commit_message(language=config.language)

        print("=" * 50)

        # 询问是否直接提交
        while True:
            try:
                choice = input("\n是否使用此消息进行提交? (Y/n/e): ").lower().strip()

                # 默认选择 yes
                if not choice:
                    choice = "y"

                if choice == "y":
                    import subprocess

                    try:
                        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                        print("✅ 提交成功!")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ 提交失败: {e}")
                    break
                elif choice == "n":
                    print("已取消提交")
                    break
                elif choice == "e":
                    import subprocess

                    try:
                        # 先使用当前消息进行提交
                        print(f"\n正在提交当前消息...")
                        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                        print("✅ 提交成功!")

                        # 然后调用 git commit --amend 进入编辑模式
                        print("正在打开编辑器修改提交信息...")
                        subprocess.run(["git", "commit", "--amend"], check=True)
                        print("✅ 提交信息已更新!")

                    except subprocess.CalledProcessError as e:
                        print(f"❌ 操作失败: {e}")
                    break
                else:
                    print("请输入 Y (提交)、n (取消) 或 e (编辑),默认为 Y")
            except KeyboardInterrupt:
                print("\n\n👋 操作已取消")
                return

    except KeyboardInterrupt:
        print("\n\n👋 FastCommit 已退出")
        return
    except Exception as e:
        print(f"错误: {e}")


def show_commit_summary(commit_ref):
    """重新生成指定commit的commit message"""
    try:
        # 加载配置
        config_manager = ConfigManager()

        if not config_manager.is_configured():
            print("错误: 未配置 API Key")
            print("\n请先配置 API:")
            show_config_help()
            return

        config = config_manager.load_config()

        # 验证配置
        if not config.api_key:
            print("错误: API Key 未配置")
            print("\n请先配置 API:")
            show_config_help()
            return

        # 创建 AI 提供者
        ai_provider = OpenAIProvider(api_key=config.api_key, base_url=config.api_base, model=config.model)

        # 创建 FastCommit 实例
        fc = FastCommit(ai_provider)

        print(f"正在分析 commit {commit_ref} 的修改内容...")

        # 获取commit信息和修改内容
        commit_info = fc.get_commit_info(commit_ref)
        if "error" in commit_info:
            print(f"错误: {commit_info['error']}")
            return

        # 显示commit基本信息
        print(f"\nCommit: {commit_info['hash']}")
        print(f"作者: {commit_info['author']}")
        print(f"日期: {commit_info['date']}")
        print(f"原始消息: {commit_info['message']}")

        # 显示修改的文件
        print(f"\n修改的文件 ({len(commit_info['changes'])} 个):")
        for change in commit_info["changes"]:
            # ANSI 绿色代码: \033[32m, 重置代码: \033[0m
            print(f"  \033[32m{change['type']}: {change['file']}\033[0m")

        # 重新生成commit message
        print("\nAI 重新生成的 Commit Message:")
        print("=" * 50)

        # 获取历史记录作为参考
        history = fc.git_operator.get_recent_commits(3)

        # 流式生成并显示commit message
        commit_msg = fc.ai_provider.generate_commit_message(commit_info["change_objects"], config.language, history, "")

        print("=" * 50)

    except KeyboardInterrupt:
        print("\n\n👋 FastCommit 已退出")
        return
    except Exception as e:
        print(f"错误: {e}")


def main():
    """主函数"""

    def signal_handler(sig, frame):
        """处理Ctrl+C信号"""
        print("\n\n👋 FastCommit 已退出")
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    try:
        parser = argparse.ArgumentParser(
            description="FastCommit - AI 生成 Git Commit Message",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  fsc                    # 生成 commit message
  fsc status            # 查看暂存区状态
  fsc see HEAD~1        # 重新生成上一个commit的message
  fsc see -1            # 重新生成上一个commit的message
  fsc see abc123        # 重新生成指定commit的message
  fsc config            # 配置 API
  fsc config --show     # 查看当前配置
  fsc prompt --show     # 查看当前 prompt (默认英文)
  fsc prompt --show --language zh    # 查看中文 prompt
  fsc prompt --edit     # 编辑 prompt (默认英文)
  fsc prompt --edit --language zh    # 编辑中文 prompt

支持的 AI 服务:
  通义千问:     https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen (推荐)
  DeepSeek:    https://api-docs.deepseek.com/zh-cn/
  自定义:       支持任何 OpenAI 兼容的 API 服务
        """,
        )

        parser.add_argument("--version", "-v", action="store_true", help="显示版本信息")

        # 配置子命令
        subparsers = parser.add_subparsers(dest="command", help="可用命令")

        # status 子命令
        status_parser = subparsers.add_parser("status", help="显示暂存区文件状态")

        # see 子命令
        see_parser = subparsers.add_parser("see", help="重新生成指定commit的commit message")
        see_parser.add_argument("commit", help="commit号或相对位置 (如: HEAD~1, -1, abc123)")

        # config 子命令
        config_parser = subparsers.add_parser("config", help="配置 API 设置")
        config_parser.add_argument("--api-key", help="设置 API Key")
        config_parser.add_argument("--api-base", help="设置 API Base URL")
        config_parser.add_argument("--model", help="设置使用的模型")
        config_parser.add_argument("--language", help="设置语言")
        config_parser.add_argument("--show", action="store_true", help="显示当前配置")

        # prompt 子命令
        prompt_parser = subparsers.add_parser("prompt", help="管理 prompt 文件")
        prompt_parser.add_argument("--show", action="store_true", help="显示当前 prompt")
        prompt_parser.add_argument("--edit", action="store_true", help="编辑 prompt")
        prompt_parser.add_argument("--language", help="设置语言")

        args = parser.parse_args()

        # 处理版本信息
        if args.version:
            from . import __version__

            print(f"FastCommit v{__version__}")
            return

        # 处理子命令
        if args.command == "config":
            configure_api(args)
            return

        # 处理状态查看
        if args.command == "status":
            show_staged_files()
            return

        # 处理commit message重新生成
        if args.command == "see":
            # 处理相对位置参数
            commit_ref = args.commit
            if commit_ref.startswith("-") and commit_ref[1:].isdigit():
                # 将 -1, -2, -3 转换为 HEAD, HEAD~1, HEAD~2
                num = int(commit_ref[1:])
                if num == 1:
                    commit_ref = "HEAD"
                else:
                    commit_ref = f"HEAD~{num-1}"
            show_commit_summary(commit_ref)
            return

        # 处理prompt管理
        if args.command == "prompt":
            manage_prompt(args)
            return

        # 默认行为:生成 commit message
        generate_commit_message()

    except KeyboardInterrupt:
        print("\n\n👋 FastCommit 已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
