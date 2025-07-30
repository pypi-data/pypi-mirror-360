"""
FastCommit 核心功能实现
"""

import subprocess
import os
import sys
from typing import List, Dict, Optional, Tuple
import json
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("请先安装 OpenAI SDK: pip install openai")


@dataclass
class GitChange:
    """Git 修改信息"""

    file_path: str
    change_type: str  # A=添加, M=修改, D=删除, R=重命名
    diff_content: str


class GitOperator:
    """Git 操作类"""

    def __init__(self):
        self.repo_root = self._get_repo_root()

    def _get_repo_root(self) -> Optional[str]:
        """获取 Git 仓库根目录"""
        try:
            result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def is_git_repo(self) -> bool:
        """检查当前目录是否为 Git 仓库"""
        return self.repo_root is not None

    def get_staged_changes(self) -> List[GitChange]:
        """获取暂存区的所有修改"""
        if not self.is_git_repo():
            raise RuntimeError("当前目录不是一个 Git 仓库")

        changes = []

        # 获取暂存区文件状态
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"], capture_output=True, text=True, check=True
            )

            if not result.stdout.strip():
                return changes

            # 解析文件状态
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) >= 2:
                    change_type = parts[0]
                    file_path = parts[1]

                    # 获取具体的 diff 内容
                    diff_content = self._get_file_diff(file_path)

                    changes.append(GitChange(file_path=file_path, change_type=change_type, diff_content=diff_content))

            return changes

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取暂存区修改失败: {e}")

    def _get_file_diff(self, file_path: str) -> str:
        """获取文件的具体 diff 内容"""
        try:
            result = subprocess.run(["git", "diff", "--cached", file_path], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def get_commit_changes(self, commit_ref: str) -> List[GitChange]:
        """获取指定commit的所有修改"""
        if not self.is_git_repo():
            raise RuntimeError("当前目录不是一个 Git 仓库")

        changes = []

        try:
            # 获取commit的文件变更状态
            result = subprocess.run(
                ["git", "diff", "--name-status", f"{commit_ref}^", commit_ref],
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                return changes

            # 解析文件状态
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) >= 2:
                    change_type = parts[0]
                    file_path = parts[1]

                    # 获取具体的 diff 内容
                    diff_content = self._get_commit_file_diff(commit_ref, file_path)

                    changes.append(GitChange(file_path=file_path, change_type=change_type, diff_content=diff_content))

            return changes

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取commit修改失败: {e}")

    def _get_commit_file_diff(self, commit_ref: str, file_path: str) -> str:
        """获取commit中指定文件的diff内容"""
        try:
            result = subprocess.run(
                ["git", "diff", f"{commit_ref}^", commit_ref, "--", file_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def get_commit_info(self, commit_ref: str) -> Dict:
        """获取commit基本信息"""
        if not self.is_git_repo():
            return {"error": "当前目录不是一个 Git 仓库"}

        try:
            # 获取commit hash
            hash_result = subprocess.run(["git", "rev-parse", commit_ref], capture_output=True, text=True, check=True)
            commit_hash = hash_result.stdout.strip()

            # 获取commit作者
            author_result = subprocess.run(
                ["git", "show", "--format=%an", "--no-patch", commit_ref], capture_output=True, text=True, check=True
            )
            author = author_result.stdout.strip()

            # 获取commit日期
            date_result = subprocess.run(
                ["git", "show", "--format=%ad", "--no-patch", commit_ref], capture_output=True, text=True, check=True
            )
            date = date_result.stdout.strip()

            # 获取完整的commit消息
            message_result = subprocess.run(
                ["git", "show", "--format=%B", "--no-patch", commit_ref], capture_output=True, text=True, check=True
            )
            message = message_result.stdout.strip()

            return {"hash": commit_hash, "author": author, "date": date, "message": message}

        except subprocess.CalledProcessError as e:
            return {"error": f"获取commit信息失败: {e}"}

    def get_recent_commits(self, count: int = 3) -> List[str]:
        """获取最近的commit message历史"""
        if not self.is_git_repo():
            return []

        try:
            # 获取最近的commit message标题
            result = subprocess.run(
                ["git", "log", f"--max-count={count}", "--format=%B", "--no-merges"],
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                return []

            # 直接按行分割,每行就是一个commit message
            commit_messages = result.stdout.strip().split("\n")

            return commit_messages

        except subprocess.CalledProcessError:
            # 如果获取失败(比如没有commit历史),返回空列表
            return []


class AIProvider:
    """AI 服务提供者基类"""

    def generate_commit_message(
        self, changes: List[GitChange], language: str = "en", history: List[str] = None
    ) -> str:
        """生成 commit message"""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI API 提供者"""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        # 创建 OpenAI 客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_commit_message(
        self, changes: List[GitChange], language: str = "en", history: List[str] = None
    ) -> str:
        """使用 OpenAI SDK 生成 commit message"""

        # 构建提示词
        prompt = self._build_prompt(changes, language, history)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=1.0,
                max_tokens=8192,
                stream=True,  # 使用流式响应
            )

            # 处理流式响应并实时显示
            commit_message = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end="")  # 实时显示生成内容
                    commit_message += content

            print()  # 换行,结束流式显示
            return commit_message.strip()

        except Exception as e:
            raise RuntimeError(f"调用 AI API 失败: {e}")

    def _get_system_prompt(self, language: str = "en") -> str:
        """根据语言获取系统提示词"""

        # 确定prompt文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        if language == "zh" or language == "zh-cn":
            prompt_file = os.path.join(current_dir, "system_prompt_zh.txt")
        else:
            prompt_file = os.path.join(current_dir, "system_prompt_en.txt")

        # 读取文件内容
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _build_prompt(
        self, changes: List[GitChange], language: str = "en", history: List[str] = None
    ) -> str:
        """构建发送给 AI 的提示词"""

        if not changes:
            if language == "zh" or language == "zh-cn":
                return "没有检测到暂存区的修改."
            else:
                return "No staged changes detected."

        prompt_lines = []

        # 添加历史记录
        if history:
            if language == "zh" or language == "zh-cn":
                prompt_lines.extend(
                    [
                        "最近的提交记录(作为风格参考):",
                    ]
                )
                for i, commit_msg in enumerate(history, 1):
                    prompt_lines.append(f"{i}. {commit_msg}")
                prompt_lines.append("")
            else:
                prompt_lines.extend(
                    [
                        "Recent commit messages (for style reference):",
                    ]
                )
                for i, commit_msg in enumerate(history, 1):
                    prompt_lines.append(f"{i}. {commit_msg}")
                prompt_lines.append("")

        # 添加当前修改信息
        if language == "zh" or language == "zh-cn":
            prompt_lines.append("当前暂存区修改:")
            change_type_map = {"A": "新增", "M": "修改", "D": "删除", "R": "重命名"}
        else:
            prompt_lines.append("Current staged changes:")
            change_type_map = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed"}

        for i, change in enumerate(changes, 1):
            change_desc = change_type_map.get(change.change_type, change.change_type)
            prompt_lines.append(f"{i}. {change_desc}: {change.file_path}")

            # 添加diff内容
            if change.diff_content:
                if language == "zh" or language == "zh-cn":
                    prompt_lines.append("   修改内容:")
                else:
                    prompt_lines.append("   Changes:")
                # 添加diff内容
                for line in change.diff_content.split("\n"):
                    if line.strip():
                        prompt_lines.append(f"   {line}")

            prompt_lines.append("")

        return "\n".join(prompt_lines)


class FastCommit:
    """FastCommit 主类"""

    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.git_operator = GitOperator()
        self.ai_provider = ai_provider

    def set_ai_provider(self, provider: AIProvider):
        """设置 AI 提供者"""
        self.ai_provider = provider

    def check_prerequisites(self) -> Tuple[bool, str]:
        """检查运行前提条件"""

        # 检查是否在 Git 仓库中
        if not self.git_operator.is_git_repo():
            return False, "当前目录不是一个 Git 仓库"

        # 检查是否配置了 AI 提供者
        if not self.ai_provider:
            return False, "未配置 AI 提供者,请先配置 API"

        return True, "检查通过"

    def generate_commit_message(self, language: str = "en") -> str:
        """生成 commit message"""

        # 检查前提条件
        is_valid, message = self.check_prerequisites()
        if not is_valid:
            raise RuntimeError(message)

        # 获取暂存区修改
        changes = self.git_operator.get_staged_changes()

        if not changes:
            raise RuntimeError("暂存区没有修改,请先使用 'git add' 添加要提交的文件")

        # 获取最近的commit历史作为参考
        history = self.git_operator.get_recent_commits(3)

        # 生成 commit message
        commit_msg = self.ai_provider.generate_commit_message(changes, language, history)

        return commit_msg

    def get_staged_files_summary(self) -> Dict:
        """获取暂存区文件摘要信息"""

        if not self.git_operator.is_git_repo():
            return {"error": "当前目录不是一个 Git 仓库"}

        changes = self.git_operator.get_staged_changes()

        if not changes:
            return {"message": "暂存区没有修改"}

        summary = {"total_files": len(changes), "changes": []}

        for change in changes:
            change_type_map = {"A": "新增", "M": "修改", "D": "删除", "R": "重命名"}

            summary["changes"].append(
                {
                    "file": change.file_path,
                    "type": change_type_map.get(change.change_type, change.change_type),
                    "raw_type": change.change_type,
                }
            )

        return summary

    def get_commit_info(self, commit_ref: str) -> Dict:
        """获取commit信息并包含变更内容"""
        # 获取基本commit信息
        commit_info = self.git_operator.get_commit_info(commit_ref)

        if "error" in commit_info:
            return commit_info

        # 获取变更内容
        try:
            changes = self.git_operator.get_commit_changes(commit_ref)

            # 转换为显示格式
            change_type_map = {"A": "新增", "M": "修改", "D": "删除", "R": "重命名"}
            change_list = []
            for change in changes:
                change_list.append(
                    {
                        "file": change.file_path,
                        "type": change_type_map.get(change.change_type, change.change_type),
                        "raw_type": change.change_type,
                    }
                )

            commit_info["changes"] = change_list
            commit_info["change_objects"] = changes  # 保留原始对象用于AI分析

            return commit_info

        except Exception as e:
            return {"error": f"获取commit变更失败: {e}"}
