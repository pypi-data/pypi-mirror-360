"""
会话管理器 - 负责会话的存储和加载
"""

import json
import sys
from pathlib import Path
from typing import Any

from .models import PKSession


class SessionManager:
    """简化版会话管理器 - 专注于会话存储和管理"""

    def __init__(self, data_dir: str | None = None, expert_manager: Any = None) -> None:
        if data_dir is None:
            # 使用环境变量或默认到用户家目录
            import os

            data_dir = os.environ.get("DATA_DIR", os.path.expanduser("~/.guru-pk-data"))

        self.data_dir = Path(data_dir)
        self.expert_manager = expert_manager
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # 如果无法创建目录，回退到临时目录
            import tempfile

            self.data_dir = Path(tempfile.mkdtemp(prefix="guru-pk-"))
            print(
                f"Warning: Could not create data directory {data_dir}, using temporary directory {self.data_dir}",
                file=sys.stderr,
            )

    def save_session(self, session: PKSession) -> bool:
        """保存会话到JSON文件"""
        try:
            file_path = self.data_dir / f"{session.session_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存会话失败: {e}")
            return False

    def load_session(self, session_id: str) -> PKSession | None:
        """从文件加载会话"""
        try:
            file_path = self.data_dir / f"{session_id}.json"
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    return PKSession.from_dict(data)
        except Exception as e:
            print(f"加载会话失败: {e}")
        return None

    def list_sessions(self) -> list[dict[str, Any]]:
        """列出所有会话的基本信息"""
        sessions = []
        try:
            for file_path in self.data_dir.glob("*.json"):
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append(
                        {
                            "session_id": data["session_id"],
                            "question": (
                                data["user_question"][:100] + "..."
                                if len(data["user_question"]) > 100
                                else data["user_question"]
                            ),
                            "personas": data["selected_personas"],
                            "created_at": data["created_at"],
                            "is_completed": data.get("final_synthesis") is not None,
                        }
                    )
        except Exception as e:
            print(f"列出会话失败: {e}")

        # 按创建时间倒序排列
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        try:
            file_path = self.data_dir / f"{session_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"删除会话失败: {e}")
        return False

    def get_latest_session(self) -> PKSession | None:
        """获取最新的会话"""
        sessions = self.list_sessions()
        if sessions:
            return self.load_session(sessions[0]["session_id"])
        return None

    def create_session(
        self,
        question: str,
        personas: list[str],
        expert_profiles: dict[str, Any] | None = None,
        is_recommended_by_host: bool = False,
    ) -> PKSession:
        """创建新的会话"""
        session = PKSession.create_new(
            user_question=question,
            selected_personas=personas,
            is_recommended_by_host=is_recommended_by_host,
        )

        # 如果提供了专家详细信息，保存到会话中
        if expert_profiles:
            session.expert_profiles = expert_profiles

        # 保存会话
        self.save_session(session)
        return session

    async def export_session_as_infographic(self, session: PKSession) -> str:
        """导出会话为塔夫特风格的单页动态信息图"""

        # 生成Markdown内容（复用现有逻辑）
        md_content = self._generate_session_markdown(session)

        # 保存Markdown文件
        md_file = self.data_dir / f"export_{session.session_id}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 读取信息图prompt模板
        # 统一使用包内的模板文件
        try:
            from importlib import resources

            prompt_template = resources.read_text(
                "guru_pk_mcp.templates", "infographic_spa_prompt.md"
            )
        except (ImportError, FileNotFoundError) as e:
            raise FileNotFoundError(f"信息图prompt模板未找到: {e}") from e

        # 生成HTML信息图文件路径
        html_file = self.data_dir / f"infographic_{session.session_id}.html"

        # 构造完整的指令内容，直接返回给MCP Host端LLM处理
        full_prompt = f"""{prompt_template}

{md_content}

---

**重要指令**: 请根据上述塔夫特风格信息图生成指令和专家辩论内容，生成一个完整的HTML文件。HTML文件要求：

1. **单文件形式**: 所有CSS、JavaScript都内联到HTML中
2. **文件保存**: 将生成的HTML内容保存到文件: `{html_file}`
3. **自动打开**: 保存完成后使用以下Python代码打开浏览器:
   ```python
   import webbrowser
   webbrowser.open("file://{html_file.absolute()}")
   ```
4. **遵循塔夫特原则**: 严格按照上述设计原则实现数据可视化
5. **响应式设计**: 确保在不同屏幕尺寸下都能正常显示

请立即开始生成HTML信息图文件。"""

        return full_prompt

    def _generate_session_markdown(self, session: PKSession) -> str:
        """生成会话的Markdown内容（从export_session方法提取）"""
        md_content = f"""# 专家PK讨论记录

**会话ID**: {session.session_id}
**问题**: {session.user_question}
**创建时间**: {session.created_at}
**参与专家**: {", ".join(session.selected_personas)}

---

"""

        round_names = {
            1: "🤔 第1轮：独立思考",
            2: "💬 第2轮：交叉辩论",
            3: "🎯 第3轮：最终立场",
            4: "🧠 第4轮：智慧综合",
        }

        for round_num in sorted(session.responses.keys()):
            md_content += f"## {round_names.get(round_num, f'第{round_num}轮')}\n\n"

            for persona, response in session.responses[round_num].items():
                md_content += f"### {persona}\n\n"
                md_content += f"{response}\n\n---\n\n"

        # Only add final_synthesis if it's different from round 4 content
        if session.final_synthesis:
            # Check if final_synthesis is identical to any round 4 response
            round_4_responses = session.responses.get(4, {})
            is_duplicate = any(
                session.final_synthesis == response
                for response in round_4_responses.values()
            )

            if not is_duplicate:
                md_content += f"## 🌟 最终综合方案\n\n{session.final_synthesis}\n\n"

        md_content += f"""## 📊 统计信息

- **总发言数**: {len([r for round_responses in session.responses.values() for r in round_responses.values()])}
- **字数统计**: {sum(len(r) for round_responses in session.responses.values() for r in round_responses.values()):,} 字符
- **最后更新**: {session.updated_at}

---
*由 Guru-PK MCP 系统生成*"""

        return md_content
