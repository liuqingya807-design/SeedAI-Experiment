import os
import sys
import subprocess
import random
import streamlit as st
import pandas as pd
from openai import OpenAI

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
# ✅ 【已修改】本地保存数据（无API、无Seatable、不报错、不404）
# =====================================================
def save_data_to_database(data):
    try:
        filename = "experiment_data.xlsx"
        # 如果文件存在就追加，不存在就新建
        if os.path.exists(filename):
            df = pd.read_excel(filename)
            new_df = pd.DataFrame([data])
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = pd.DataFrame([data])
        df.to_excel(filename, index=False)
        print("✅ 数据已保存到本地：experiment_data.xlsx")
    except Exception as e:
        print("⚠️ 保存失败：", e)

# =====================================================
# 1. DeepSeek 配置
# =====================================================
DEEPSEEK_API_KEY = ""
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# =====================================================
# 2. Streamlit 兼容性处理
# =====================================================
def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# --- 3. 实验初始化配置 ---
st.set_page_config(page_title="Seed AI", layout="centered")

if "consent" not in st.session_state:
    st.markdown("""
# 欢迎参与本次实验！
尊敬的女士/先生：
您好！非常感谢您参与本实验，本实验旨在了解用户在求职面试相关任务中与AI助手的交互行为，仅用于毕业论文研究。

本次实验包含以下内容：
- 您将被随机分配到「求职者」或「HR」两种角色
- 任务过程中，您可以与AI助手对话
- 系统会自动记录您的对话数据（仅用于学术研究、全程匿名）

⚠️ 重要说明：
- 本实验无对错之分
- 您可以随时退出实验
- 所有数据严格保密
""")
    if st.button("我已阅读并同意，进入实验"):
        st.session_state["consent"] = True
        rerun_app()
    st.stop()

# --- 问卷引导页面 ---
if st.query_params.get("page") == "questionnaire":
    st.title("📋 调查问卷")
    st.markdown("---")
    st.markdown("感谢您完成本次实验！请填写以下问卷。")
    st.markdown("---")
    st.markdown("[点击此处填写问卷](https://www.credamo.com/s/umEBviano/)")
    st.markdown("cdmq6uhCiueL 邀请您作答问卷《生成式 AI 任务交互体验调查问卷》")
    st.markdown("---")
    if st.button("← 返回实验页面"):
        st.query_params["page"] = "experiment"
        rerun_app()
    st.stop()

RESUME_IMAGES = [
    "https://i.imgur.com/hfRjQTI.jpeg",
    "https://i.imgur.com/dDM6Mt2.jpeg",
    "https://i.imgur.com/O5cvFL9.jpeg",
    "https://i.imgur.com/cyRqMzM.jpeg"
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

# --- 4. 页面标题 ---
st.title("🤖 Seed AI")

# --- 5. 侧边栏 ---
st.sidebar.info(f"**用户ID:** {st.session_state.user_id}")
st.sidebar.info(f"**实验组:** {st.session_state.task_type}")

# --- 6. 简历图片 ---
st.subheader("📄 简历材料")
cols = st.columns(4)
for i, img in enumerate(RESUME_IMAGES):
    if img.strip():
        cols[i].image(img, caption=f"简历{i + 1}")
st.divider()

# ==============================================
# 任务说明
# ==============================================
task_type = st.session_state.task_type
user_task_input = ""

if task_type == "low":
    st.markdown("## 求职者写自我介绍")
    st.markdown("""
**你是一名求职者，应聘“AI算法工程师”岗位。**
请结合岗位要求和简历，编写1份自我介绍。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 负责机器学习/深度学习算法开发与优化
- 跟踪前沿 AI 技术并落地
- 评估模型性能，提升准确度

【任职要求】
- 计算机/统计/数学相关专业
- 熟悉 Python/C++，PyTorch/TensorFlow
- 优先考虑：算法优化能力、项目经验
""")
    user_task_input = st.text_area("✍️ 请在此编写你的自我介绍：", height=200)

else:
    st.markdown("## HR筛选简历")
    st.markdown("""
**你是人力资源经理，筛选4份简历，录取1名候选人。**
并给出3个评价维度。

### 招聘岗位：AI 算法工程师
【岗位职责】
- 算法开发、优化、落地
- 模型性能提升

【任职要求】
- 相关专业
- 编程与框架能力
- 算法优化与项目经验
""")
    choice = st.radio("✅ 请选择录取的候选人：", ["候选人1", "候选人2", "候选人3", "候选人4"])
    q1 = st.text_input("① 专业匹配度评价（≤200字）：")
    q2 = st.text_input("② 算法优化能力评价（≤200字）：")
    q3 = st.text_input("③ 项目经验评价（≤200字）：")
    user_task_input = f"录取：{choice} | 专业：{q1} | 算法能力：{q2} | 项目经验：{q3}"

st.divider()

# --- AI 回复 ---
def fetch_ai_response(chat_history):
    try:
        if not DEEPSEEK_API_KEY:
            return "请先填写 DeepSeek API Key"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API错误：{str(e)}"

# 干预关键词
revision_keywords = ["改", "重写", "调整", "不对", "换", "重新", "不要", "修改", "优化", "太长", "太短", "精简", "扩写", "语气", "风格", "表格", "分点", "纠正", "错", "不好", "重新生成"]

# 聊天界面
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

# ==============================================
# ✅ 提交数据（已改成本地保存）
# ==============================================
st.divider()
user_turns = len([m for m in st.session_state.messages if m["role"] == "user"])

if user_turns < 3:
    st.warning(f"当前对话轮次：{user_turns}，至少完成3轮对话才能提交")
else:
    if "experiment_completed" not in st.session_state:
        st.session_state.experiment_completed = False

    if st.button("✅ 完成并提交实验数据") or st.session_state.experiment_completed:
        if not st.session_state.experiment_completed:
            first = st.session_state.first_intervene or 0
            total = st.session_state.total_intervene
            total_turns = user_turns

            full_dialogue = ""
            for msg in st.session_state.messages:
                role = "用户" if msg["role"] == "user" else "AI"
                full_dialogue += f"[{role}]: {msg['content']}\n\n"

            final_data = {
                "user_id": st.session_state.user_id,
                "group": st.session_state.task_type,
                "total_turns": total_turns,
                "first_intervene_turn": first,
                "total_intervene_count": total,
                "user_answer": user_task_input,
                "full_dialogue": full_dialogue
            }

            # ✅ 保存到本地
            save_data_to_database(final_data)
            st.session_state.experiment_completed = True
            st.success("✅ 实验数据已成功保存！")

        if st.button("📝 实验完成，请点击填写问卷"):
            st.query_params["page"] = "questionnaire"
            rerun_app()
