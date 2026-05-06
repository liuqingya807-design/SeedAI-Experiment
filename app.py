import os
import sys
import subprocess
import random
import streamlit as st
import pandas as pd
import requests
from openai import OpenAI
from github import Github
from io import StringIO
import csv


# =====================================================
# 0. 让代码可以在 PyCharm 中直接运行
# =====================================================
def is_running_with_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

if not is_running_with_streamlit():
    current_file = os.path.abspath(__file__)
    subprocess.run([sys.executable, "-m", "streamlit", "run", current_file])
    sys.exit()


# =====================================================
# ✅【只加这个】自动保存数据到你的 GitHub 数据库
# =====================================================
def save_data_to_database(data):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        repo = g.get_repo("liuqingya807-design/SeedAI-Experiment")
        path = "experiment_data.csv"

        try:
            f = repo.get_contents(path)
            content = f.decoded_content.decode("utf-8")
            reader = csv.DictReader(StringIO(content))
            rows = list(reader)
            fieldnames = reader.fieldnames
        except:
            fieldnames = data.keys()
            rows = []
            f = None

        rows.append(data)
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        new_content = output.getvalue()

        if f:
            repo.update_file(path, "Add data", new_content, f.sha)
        else:
            repo.create_file(path, "Create data file", new_content)
    except:
        pass


# =====================================================
# 1. DeepSeek 配置（完全没动）
# =====================================================
DEEPSEEK_API_KEY = ""
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


# =====================================================
# 2. Streamlit 兼容性处理（完全没动）
# =====================================================
def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


# --- 3. 实验初始化配置（完全没动）---
st.set_page_config(page_title="Seed AI", layout="centered")

if "consent" not in st.session_state:
    st.markdown("""
   # 欢迎参与本次实验！
尊敬的女士/先生：
您好！非常感谢您参与本实验，本实验旨在了解用户在<span style="color:red">求职面试相关任务情境中与AI助手的交互行为</span>，仅用于毕业论文研究。

本次实验包含以下内容：
- 您将被随机分配到<span style="color:red">「求职者」</span>或<span style="color:red">「HR」</span>两种角色，并根据页面说明完成相应任务；
- 任务过程中，<span style="color:red">您可以与AI助手对话，辅助您完成相关任务；</span>
- 任务完成后，请<span style="color:red">根据页面提示保存数据</span>，并<span style="color:red">填写</span>一份简短的后续<span style="color:red">问卷</span>；
- <span style="color:red">问卷中需要填写用户ID，请提前记录下您的用户ID，以便填写。</span>

实验流程：
1.  阅读任务说明进入任务界面 → 分配用户ID
2.  完成角色对应的核心任务<span style="color:red">（与AI对话协作）</span>
3.  完成任务后，<span style="color:red">点击页面中的"保存数据"按钮</span>
4.  <span style="color:red">填写后测问卷</span>

⚠️ 重要说明：
- 本实验无对错之分，请按您的真实想法完成任务
- 您可以随时退出实验，无需任何理由，数据不会被记录
- 所有数据仅用于学术研究，不会泄露任何个人信息

点击下方按钮，即表示您已阅读并同意以上说明，自愿参与本次实验。
    """, unsafe_allow_html=True)

    if st.button("我已阅读并同意，进入实验"):
        st.session_state["consent"] = True
        rerun_app()

    st.stop()

# --- 问卷引导页面（完全没动）---
if st.query_params.get("page") == "questionnaire":
    st.title("📋 调查问卷")
    st.markdown("---")
    st.markdown(f"""
    ### 亲爱的用户 (ID: {st.session_state.user_id})：

    感谢您完成本次实验！

    您的参与对我们的研究非常重要。现在，请您花费几分钟时间填写以下调查问卷。

    您的回答将被严格保密，仅用于学术研究目的。
    """)
    st.markdown("---")
    st.markdown("[点击此处填写问卷](https://www.credamo.com/s/i2YZR3ano/)")
    st.markdown("cdmq6uhCiueL 邀请您作答问卷《生成式 AI 任务交互体验调查问卷》，点击链接开始作答。")
    st.markdown("---")
    if st.button("← 返回实验页面"):
        st.query_params["page"] = "experiment"
        rerun_app()
    st.stop()


RESUME_IMAGES = [
    "https://raw.githubusercontent.com/liuqingya807-design/SeedAI-Experiment/main/简历1.jpg",
    "https://raw.githubusercontent.com/liuqingya807-design/SeedAI-Experiment/main/简历2.jpg",
    "https://raw.githubusercontent.com/liuqingya807-design/SeedAI-Experiment/main/简历3.jpg",
    "https://raw.githubusercontent.com/liuqingya807-design/SeedAI-Experiment/main/简历4.jpg"
]


if "messages" not in st.session_state:
    st.session_state.messages = []

if "task_type" not in st.session_state:
    st.session_state.task_type = random.choice(["low", "high"])

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{random.randint(100000, 999999)}"

if "first_intervene" not in st.session_state:
    st.session_state.first_intervene = None

if "total_intervene" not in st.session_state:
    st.session_state.total_intervene = 0


# --- 4. 页面标题（完全没动）---
st.title("🤖 Seed AI")


# --- 5. 侧边栏（完全没动）---
st.sidebar.info(f"**用户ID:** {st.session_state.user_id}")
st.sidebar.info(f"**实验组:** {st.session_state.task_type}")


# --- 6. 简历图片（完全没动）---
st.subheader("📄 简历材料")
cols = st.columns(4)
for i, img in enumerate(RESUME_IMAGES):
    if img.strip():
        cols[i].image(img, caption=f"简历{i + 1}")
st.divider()


# ==============================================
# 【任务说明 100% 原样】（完全没动）
# ==============================================
task_type = st.session_state.task_type
user_task_input = ""

if task_type == "low":
    st.markdown("求职者写自我介绍")
    st.markdown("""
**你是一名求职者，拟应聘一家公司的“AI算法工程师”岗位。**
请结合岗位关注提示、面试者简历，以求职者身份编写1份自我介绍，为将来的面试做准备。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 负责公司核心产品中机器学习/深度学习算法的开发与优化；
- 跟踪前沿 AI 技术，将其转化为可落地的业务方案；
- 参与模型性能评估，确保持续提升算法输出的准确度。

【任职要求】
- 计算机、统计学或数学相关专业本科及以上学历；
- 熟悉 Python/C++ 等编程语言，熟练使用 PyTorch 或 TensorFlow 框架；
- 核心关注：具备良好的算法优化能力，有实际的项目应用经验者优先。

【自我介绍编写提示】
该岗位中，招聘方关注候选人是否具有算法优化与应用经验，请你围绕这一要点编写自我介绍。
自我介绍稿中可以补充JD中未提及的相关内容。
""")
    user_task_input = st.text_area("✍️ 请在此编写你的自我介绍：", height=200)

else:
    st.markdown("### HR筛选简历")
    st.markdown("""
**你是一名人力资源经理（HR），你所在的公司拟招聘1名AI算法工程师。**
请梳理你目前收到的4份简历，结合岗位招聘标准，为“AI算法工程师”岗位选择1名合适的候选人。
并请给出您选择时参考的岗位招聘标准（至少3个方面，每个方面不超过200字）。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 负责公司核心产品中机器学习/深度学习算法的开发与优化；
- 跟踪前沿 AI 技术，将其转化为可落地的业务方案；
- 参与模型性能评估，确保持续提升算法输出的准确度。

【任职要求】
- 计算机、统计学或数学相关专业本科及以上学历；
- 熟悉 Python/C++ 等编程语言，熟练使用 PyTorch 或 TensorFlow 框架；
- 核心关注：具备良好的算法优化能力，有实际的项目应用经验者优先。
""")
    choice = st.radio("✅ 请选择录取的候选人：", ["候选人1", "候选人2", "候选人3", "候选人4"])
    q1 = st.text_input("① 专业匹配度评价（≤200字）：")
    q2 = st.text_input("② 算法优化能力评价（≤200字）：")
    q3 = st.text_input("③ 项目经验评价（≤200字）：")
    user_task_input = f"录取：{choice} | 专业：{q1} | 算法能力：{q2} | 项目经验：{q3}"

st.divider()


# --- AI 回复函数（完全没动）---
def fetch_ai_response(chat_history):
    try:
        if DEEPSEEK_API_KEY == "xxxx" or not DEEPSEEK_API_KEY:
            return "API调用失败：请先在代码中填写你的 DeepSeek API Key。"

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API调用失败: {e}"


# --- 干预关键词（完全没动）---
revision_keywords = [
    "改", "重写", "调整", "不对", "换", "重新", "不要", "修改", "优化",
    "太长", "太短", "长一点", "短一点", "精简", "扩写", "缩写", "字数",
    "语气", "风格", "幽默", "专业", "严肃", "通俗", "正式", "口语化",
    "表格", "列表", "分点", "条理", "结构", "清晰", "替换", "纠正",
    "错", "不好", "不够", "重新生成", "换一种", "再来", "重做", "修正"
]


# --- 聊天界面（完全没动）---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("输入指令（可修改/干预意图）...")

if prompt:
    current_turn = len([m for m in st.session_state.messages if m["role"] == "user"]) + 1
    is_revision = any(keyword in prompt for keyword in revision_keywords)

    if is_revision and st.session_state.first_intervene is None:
        st.session_state.first_intervene = current_turn
    if is_revision:
        st.session_state.total_intervene += 1

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI 思考中..."):
            ai_content = fetch_ai_response(st.session_state.messages)
            st.markdown(ai_content)
    st.session_state.messages.append({"role": "assistant", "content": ai_content})


# --- 导出数据（完全没动，只加一行自动上传）---
st.divider()
user_turns = len([m for m in st.session_state.messages if m["role"] == "user"])

if user_turns < 3:
    st.warning(f"当前对话轮次：{user_turns}，**至少完成3轮对话**才能提交实验")

else:
    if "experiment_completed" not in st.session_state:
        st.session_state.experiment_completed = False

    if st.button("✅ 完成并提交实验数据") or st.session_state.experiment_completed:
        if not st.session_state.experiment_completed:
            first_intervene_turn = st.session_state.first_intervene or 0
            total_intervene_count = st.session_state.total_intervene
            total_turns = len([m for m in st.session_state.messages if m["role"] == "user"])

            full_dialogue = ""
            for msg in st.session_state.messages:
                role = "用户" if msg["role"] == "user" else "AI"
                full_dialogue += f"[{role}]: {msg['content']}\n\n"

            final_data = {
                "user_id": st.session_state.user_id,
                "group": st.session_state.task_type,
                "total_turns": total_turns,
                "first_intervene_turn": first_intervene_turn,
                "total_intervene_count": total_intervene_count,
                "user_answer": user_task_input,
                "full_dialogue": full_dialogue
            }

            # ✅ 只加这一行：自动上传到你的数据库
            save_data_to_database(final_data)

            st.session_state.experiment_completed = True
            st.success("✅ 实验数据已成功提交！")

        if st.button("📝 实验已经完成，请点击进行问卷填写", key="btn_questionnaire"):
            st.query_params["page"] = "questionnaire"
            rerun_app()
