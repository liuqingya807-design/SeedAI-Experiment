import os
import sys
import subprocess


# =========================================================
# PyCharm 直接运行适配：
# 如果用户直接点击 PyCharm 的 Run，本文件会自动用 streamlit run 重新启动。
# 如果已经处于 Streamlit 运行环境，则继续执行下面的网页代码。
# =========================================================
def is_running_in_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if not is_running_in_streamlit():
    current_file = os.path.abspath(__file__)
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        current_file,
        "--server.headless=false"
    ])
    sys.exit()

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
from openai import OpenAI

# --- 1. 实验初始化配置 ---
st.set_page_config(page_title="Seed AI", layout="centered")

# =========================================================
# 助推区域固定与自动对齐样式
# 说明：
# 1. 不改动 Streamlit 原生输入框位置；
# 2. 只把助推区域固定到输入框正上方；
# 3. 位置由后面的 JS 自动读取输入框位置后校准；
# 4. 按钮仍然使用原生 st.button，保留原有功能逻辑。
# =========================================================
st.markdown("""
<style>
.block-container {
    padding-bottom: 360px !important;
}

:root {
    --seed-nudge-left: 50%;
    --seed-nudge-width: min(720px, calc(100vw - 32px));
    --seed-nudge-bottom: 120px;
    --seed-nudge-transform: translateX(-50%);
}

.st-key-seed_nudge_fixed_area {
    position: fixed !important;
    left: var(--seed-nudge-left) !important;
    bottom: var(--seed-nudge-bottom) !important;
    transform: var(--seed-nudge-transform) !important;
    width: var(--seed-nudge-width) !important;
    max-width: var(--seed-nudge-width) !important;
    box-sizing: border-box !important;
    z-index: 999999 !important;
    background: transparent !important;
}

/* 让固定助推区域内部组件撑满 */
.st-key-seed_nudge_fixed_area > div {
    width: 100% !important;
    margin-bottom: 0 !important;
}

/* B组按钮宽度更稳定 */
.st-key-seed_nudge_fixed_area div[data-testid="column"] button {
    width: 100% !important;
}

/* 提示框与按钮行之间的间距设置为0像素 */
/* B组提示框样式 - 浅蓝色背景 */
.st-key-seed_nudge_fixed_area .stAlert {
    margin: 0 !important;
    padding: 4px 12px !important;
    border-radius: 4px !important;
    border: none !important;
    box-shadow: none !important;
    background: #bbdefb !important;
    position: relative !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    min-height: 36px !important;
}

/* A组提示框样式 - 浅黄色背景 (#FFFACD) */
.st-key-seed_nudge_fixed_area .stAlert[data-testid="stAlertWarning"] {
    background: #FFFACD !important;
}

.st-key-seed_nudge_fixed_area .stAlert > div {
    display: flex !important;
    align-items: center !important;
    flex: 1 !important;
}

/* 隐藏左侧强调条 */
.st-key-seed_nudge_fixed_area .stAlert::before {
    display: none !important;
}

/* 提示框文字样式 - 浅蓝背景深色字体 */
.st-key-seed_nudge_fixed_area .stAlert p {
    font-size: 21px !important;
    font-weight: 600 !important;
    color: #0d3c91 !important;
    line-height: 1.2 !important;
    margin: 0 !important;
    padding: 0 !important;
    text-shadow: none !important;
    position: relative !important;
    top: -7px !important;
}

/* 调整按钮列布局 - Flexbox实现均匀间距和左右对齐 */
.st-key-seed_nudge_fixed_area div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 8px !important;
    justify-content: space-between !important;
    align-items: stretch !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    margin-top: 0 !important;
}

.st-key-seed_nudge_fixed_area div[data-testid="column"] {
    flex: 1 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    min-width: 0 !important;
    display: flex !important;
    justify-content: center !important;
}

/* 移除按钮容器与上方内容的间距 */
.st-key-seed_nudge_fixed_area div[data-testid="stHorizontalBlock"] > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* 移除按钮容器本身的间距 */
.st-key-seed_nudge_fixed_area div[data-testid="stHorizontalBlock"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* 移动端适配 */
@media (max-width: 640px) {
    .block-container {
        padding-bottom: 420px !important;
    }

    /* 移动端按钮间距调整 */
    .st-key-seed_nudge_fixed_area div[data-testid="stHorizontalBlock"] {
        gap: 6px !important;
    }

    /* 移动端提示框与按钮行间距也设置为0像素 */
    .st-key-seed_nudge_fixed_area .stAlert {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }

    /* 移动端提示框样式 - 浅蓝色背景 */
    .st-key-seed_nudge_fixed_area .stAlert {
        margin: 0 !important;
        padding: 4px 10px !important;
        border-radius: 4px !important;
        border: none !important;
        min-height: 34px !important;
        background: #bbdefb !important;
    }

    /* 移动端A组提示框样式 - 浅黄色背景 */
    .st-key-seed_nudge_fixed_area .stAlert[data-testid="stAlertWarning"] {
        background: #FFFACD !important;
    }
    
    /* 移动端提示框文字样式 */
    .st-key-seed_nudge_fixed_area .stAlert p {
        font-size: 19px !important;
        font-weight: 600 !important;
        color: #0d3c91 !important;
        line-height: 1.2 !important;
        text-shadow: none !important;
        position: relative !important;
        top: -7px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- 问卷引导页面 ---
if st.query_params.get("page") == "questionnaire":
    st.title("📋 调查问卷")
    st.markdown("---")
    st.markdown("""
    ### 亲爱的参与者：

    感谢您完成本次实验！

    您的参与对我们的研究非常重要。现在，请您花费几分钟时间填写以下调查问卷。

    您的回答将被严格保密，仅用于学术研究目的。
    """)
    st.markdown("---")
    st.markdown("[点击此处填写问卷](https://www.credamo.com/s/Ynaqqaano/)")
    st.markdown("cdmq6uhCiueL 邀请您作答问卷《生成式AI任务辅助体验调查问卷》，点击链接开始作答。")
    st.markdown("---")
    if st.button("← 返回实验页面"):
        st.query_params["page"] = "experiment"
        st.rerun()
    st.stop()

# --- 按钮点击跳转处理 ---
if st.session_state.get("btn_questionnaire"):
    st.query_params["page"] = "questionnaire"
    st.rerun()

if "consent" not in st.session_state:
    st.markdown("""
    # 欢迎参与本次实验！
尊敬的女士/先生：
您好！非常感谢您参与本实验，本实验旨在了解用户在求职面试相关任务中与AI助手的交互行为，仅用于毕业论文研究。

本次实验包含以下内容：
- 您将进入一个求职面试相关任务情境，并根据页面说明完成相应任务；
- 任务过程中，您可以与AI助手对话，系统会自动记录您的对话数据（仅用于学术研究，全程匿名、严格保密）；
- 任务完成后，请根据页面提示保存数据，并填写一份简短的后续问卷；

实验流程：
1.  阅读任务说明进入任务界面 → 分配用户ID
2.  根据页面说明完成相应任务（与AI对话协作）
3.  完成任务后，点击页面中的“保存数据”按钮
4.  填写后测问卷

⚠️ 重要说明：
- 本实验无对错之分，请按您的真实想法完成任务
- 您可以随时退出实验，无需任何理由，数据不会被记录
- 所有数据仅用于学术研究，不会泄露任何个人信息

点击下方按钮，即表示您已阅读并同意以上说明，自愿参与本次实验。
    """)
    if st.button("我已阅读并同意，进入实验"):
        st.session_state["consent"] = True
        st.rerun()
    st.stop()

# 直接配置 DeepSeek 接口
client = OpenAI(
    api_key="sk-b11f07718e2745aa8c12eb817ff9fa64",  # 你自己填写 API Key
    base_url="https://api.deepseek.com"
)

# 简历图片链接（和研究3完全一样）
RESUME_IMAGES = [
    "https://i.imgur.com/hfRjQTI.jpeg",
    "https://i.imgur.com/dDM6Mt2.jpeg",
    "https://i.imgur.com/O5cvFL9.jpeg",
    "https://i.imgur.com/cyRqMzM.jpeg"
]

# 初始化实验数据（完全沿用研究3格式）
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'group' not in st.session_state:
    st.session_state.group = random.choice(['Control', 'A', 'B'])
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{random.randint(100000, 999999)}"
if 'first_intervene' not in st.session_state:
    st.session_state.first_intervene = None
if 'total_intervene' not in st.session_state:
    st.session_state.total_intervene = 0
if 'nudge_prompt' not in st.session_state:
    st.session_state.nudge_prompt = ""

# --- 2. 页面标题 ---
st.title("🤖 Seed AI")

# --- 3. 侧边栏 ---
st.sidebar.info(f"**用户ID:** {st.session_state.user_id}")
st.sidebar.info(f"**助推组别:** {st.session_state.group}")

# --- 4. 简历图片（和研究3完全一样：横向4列） ---
st.subheader("📄 简历材料")
cols = st.columns(4)
for i, img in enumerate(RESUME_IMAGES):
    if img:
        cols[i].image(img, caption=f"简历{i + 1}")

st.divider()

# ==============================================
# 研究4任务说明（保持和研究3一样的排版）
# ==============================================
st.markdown("### 任务：人力资源经理（HR）")
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


# --- AI 调用函数（和研究3完全一样） ---
def fetch_ai_response(chat_history):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=chat_history,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API调用失败: {e}"


# --- 干预关键词（和研究3完全一样） ---
revision_keywords = [
    "改", "重写", "调整", "不对", "换", "重新", "不要", "修改", "优化",
    "太长", "太短", "长一点", "短一点", "精简", "扩写", "缩写", "字数",
    "语气", "风格", "幽默", "专业", "严肃", "通俗", "正式", "口语化",
    "表格", "列表", "分点", "条理", "结构", "清晰", "替换", "纠正",
    "错", "不好", "不够", "重新生成", "换一种", "再来", "重做", "修正"
]


# ==============================================
# 元认知唤醒助推（保留最初原有功能逻辑）
# 只增加：固定在输入框上方并自动对齐
# ==============================================
def render_nudge(last_ai_response):
    # B组：始终显示按钮，不需要创建标志
    if st.session_state.group == 'B':
        with st.container(key="seed_nudge_fixed_area"):
            st.info("点击按钮快速优化内容")
            ca, cb, cc = st.columns(3)

            def handle_professional_click():
                st.session_state.btn_b_professional_clicked = True

            def handle_length_click():
                st.session_state.btn_b_length_clicked = True

            def handle_points_click():
                st.session_state.btn_b_points_clicked = True

            with ca:
                st.button("💼 专业语气", key="btn_b_professional", on_click=handle_professional_click)

            with cb:
                st.button("📏 控制字数", key="btn_b_length", on_click=handle_length_click)

            with cc:
                st.button("✅ 分点整理", key="btn_b_points", on_click=handle_points_click)

            # 单独处理按钮点击事件，确保所有按钮始终显示
            if st.session_state.get("btn_b_professional_clicked", False):
                prompt = "请使用专业HR语气"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.session_state.btn_b_professional_clicked = False
                st.rerun()

            if st.session_state.get("btn_b_length_clicked", False):
                prompt = "请控制每条内容100-120字"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.session_state.btn_b_length_clicked = False
                st.rerun()

            if st.session_state.get("btn_b_points_clicked", False):
                prompt = "请分点整理，结构更清晰"
                st.session_state.messages.append({"role": "user", "content": prompt})
                ai_reply = fetch_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.session_state.btn_b_points_clicked = False
                st.rerun()
        return None

    # A组：基于AI回答内容显示提示框
    if st.session_state.group == 'A':
        # 初始化容器创建标志（仅A组使用）
        if 'nudge_container_created' not in st.session_state:
            st.session_state.nudge_container_created = False

        # 只允许创建一次容器（当前会话轮次）
        if st.session_state.nudge_container_created:
            return None

        if len(last_ai_response) > 150:
            with st.container(key="seed_nudge_fixed_area"):
                st.warning("💡 提示：内容较长，建议精简为 100-120 字")
            st.session_state.nudge_container_created = True

        elif len(last_ai_response) > 2 and "、" not in last_ai_response[:50]:
            with st.container(key="seed_nudge_fixed_area"):
                st.warning("💡 提示：内容结构较零散，建议分点整理")
                if st.button("  自动分点整理"):
                    prompt = "请帮我把内容整理成清晰的分点条目"
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    ai_reply = fetch_ai_response(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    st.rerun()
            st.session_state.nudge_container_created = True

        elif "会" in last_ai_response[:30] or "可以" in last_ai_response[:30]:
            with st.container(key="seed_nudge_fixed_area"):
                st.warning("💡 提示：表述偏口语，建议使用专业 HR 用语")
                if st.button("🔧 自动优化专业度"):
                    prompt = "请使用专业的HR招聘术语，不要口语化"
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    ai_reply = fetch_ai_response(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    st.rerun()
            st.session_state.nudge_container_created = True

    return None


# --- 聊天界面 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 获取上一次AI回答内容（用于在用户输入后立即显示提示框）
last_ai_response = ""
if len(st.session_state.messages) >= 2:
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            last_ai_response = msg["content"]
            break

# 在聊天输入框之前渲染提示框（基于上一次AI回答）
render_nudge(last_ai_response)

if prompt := st.chat_input("输入指令（可修改/干预意图）..."):
    # A组：重置容器创建标志，允许创建新的提示框
    if st.session_state.group == 'A':
        st.session_state.nudge_container_created = False

    current_turn = len([m for m in st.session_state.messages if m['role'] == 'user']) + 1
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

    # A组：AI回答生成后显示提示框（基于新回答）
    # B组不需要再次调用，因为按钮内容与AI回答无关
    if st.session_state.group == 'A':
        render_nudge(ai_content)

# =========================================================
# 自动对齐脚本
# 作用：
# 1. 读取底部输入框真实位置；
# 2. 将助推容器 st-key-seed_nudge_fixed_area 对齐到输入框正上方；
# 3. 不改变输入框自身位置；
# 4. 不改变按钮原有 st.button 功能。
# =========================================================
components.html("""
<script>
(function () {
    const gapPx = 4;  // 约 1mm

    function findChatInput(doc) {
        const textarea =
            doc.querySelector('textarea[placeholder^="输入指令"]') ||
            doc.querySelector('textarea[data-testid="stChatInputTextArea"]') ||
            doc.querySelector('textarea');

        if (textarea) {
            const form = textarea.closest('form');
            if (form) {
                const formRect = form.getBoundingClientRect();
                if (formRect.width > 200 && formRect.height > 20) {
                    return form;
                }
            }

            const chatInput =
                textarea.closest('[data-testid="stChatInput"]') ||
                textarea.parentElement;
            return chatInput || textarea;
        }

        const candidates = Array.from(doc.querySelectorAll(
            '[data-testid="stChatInput"], .stChatFloatingInputContainer'
        ));

        let best = null;
        let bestArea = 0;

        for (const el of candidates) {
            const rect = el.getBoundingClientRect();
            const area = rect.width * rect.height;
            if (rect.width > 200 && rect.height > 20 && area > bestArea) {
                best = el;
                bestArea = area;
            }
        }

        return best;
    }

    function findNudgeArea(doc) {
        return (
            doc.querySelector('.st-key-seed_nudge_fixed_area') ||
            doc.querySelector('[class*="st-key-seed_nudge_fixed_area"]')
        );
    }

    function alignNudgeToChatInput() {
        try {
            const doc = window.parent.document;
            const root = doc.documentElement;
            const nudge = findNudgeArea(doc);
            const chatInput = findChatInput(doc);

            if (!nudge || !chatInput) {
                return;
            }

            const rect = chatInput.getBoundingClientRect();

            if (rect.width < 200 || rect.height < 20) {
                return;
            }

            const bottomValue = window.parent.innerHeight - rect.top + gapPx;

            root.style.setProperty('--seed-nudge-left', rect.left + 'px');
            root.style.setProperty('--seed-nudge-width', rect.width + 'px');
            root.style.setProperty('--seed-nudge-bottom', bottomValue + 'px');
            root.style.setProperty('--seed-nudge-transform', 'none');

            nudge.style.left = rect.left + 'px';
            nudge.style.width = rect.width + 'px';
            nudge.style.maxWidth = rect.width + 'px';
            nudge.style.bottom = bottomValue + 'px';
            nudge.style.transform = 'none';
        } catch (e) {
            // 如果脚本未能执行，保留 CSS 默认位置
        }
    }

    alignNudgeToChatInput();

    let count = 0;
    const timer = setInterval(function () {
        alignNudgeToChatInput();
        count += 1;
        if (count > 50) {
            clearInterval(timer);
        }
    }, 150);

    window.parent.addEventListener('resize', alignNudgeToChatInput);
})();
</script>
""", height=0)

# --- 导出数据 ---
st.divider()
user_turns = len([m for m in st.session_state.messages if m["role"] == "user"])

if user_turns < 3:
    st.warning(f"当前对话轮次：{user_turns}，**至少完成3轮对话**才能提交实验")
else:
    # 初始化实验完成状态
    if "experiment4_completed" not in st.session_state:
        st.session_state.experiment4_completed = False

    # 初始化实验数据
    if "experiment4_csv_data" not in st.session_state:
        st.session_state.experiment4_csv_data = None

    # "完成并导出实验数据"按钮 - 点击后固定显示
    if st.button("✅ 完成并导出实验数据") or st.session_state.experiment4_completed:
        if not st.session_state.experiment4_completed:
            first_intervene_turn = st.session_state.first_intervene if st.session_state.first_intervene else 0
            total_intervene_count = st.session_state.total_intervene
            total_turns = len([m for m in st.session_state.messages if m["role"] == "user"])

            full_dialogue = ""
            for msg in st.session_state.messages:
                role = "用户" if msg["role"] == "user" else "AI"
                full_dialogue += f"[{role}]: {msg['content']}\n\n"

            final_data = {
                "user_id": [st.session_state.user_id],
                "group": [st.session_state.group],
                "total_turns": [total_turns],
                "first_intervene_turn": [first_intervene_turn],
                "total_intervene_count": [total_intervene_count],
                "full_dialogue": [full_dialogue]
            }

            final_df = pd.DataFrame(final_data)
            st.session_state.experiment4_csv_data = final_df.to_csv(index=False, encoding="utf-8-sig")
            st.session_state.experiment4_completed = True

        # 显示CSV下载按钮
        if st.session_state.experiment4_csv_data:
            st.download_button(
                "📥 点击下载 CSV 文件",
                st.session_state.experiment4_csv_data,
                f"SeedAI_Group_{st.session_state.user_id}.csv",
                "text/csv"
            )

        # 问卷按钮 - 始终显示
        if st.button("📝 实验已经完成，请点击进行问卷填写", key="btn_questionnaire"):
            st.query_params["page"] = "questionnaire"
            st.rerun()

