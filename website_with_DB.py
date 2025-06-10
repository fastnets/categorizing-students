import gradio as gr
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import joblib
import warnings
from data_base import SavesDataUsers, SavesDataStudents
import matplotlib

matplotlib.use('Agg')
warnings.filterwarnings("ignore")

# Загрузка данных и модели
df = pd.read_csv("dlya_modeli.csv")
model = joblib.load("model_1.pkl")

subjects = [
    "Вероятность и статистика", "Геометрия", "Обществознание",
    "Русский язык", "Современная литература", "Труд",
    "Физ-ра", "Физика", "Химия"
]
def create_header():
    return gr.Markdown("""
        <div class="header full-width">
            <div class="logo" onclick="window.location.href='/'">
                <span></span><span>Aristhesis</span>
            </div>
        </div>
    """)

def get_student_class_data(student_id, class_num):
    # print(df['Student'][])
    student_data = df[(df['Student'] == student_id) & (df['Class'] == class_num)]
    if student_data.empty:
        raise ValueError(f"Ученик {student_id} в классе {class_num} не найден.")
    return student_data


def predict_grades(student_id, class_num):
    student_data = get_student_class_data(student_id, class_num)
    prediction = model.predict(student_data)
    return prediction[:9] if len(prediction) >= 9 else list(prediction) + [3] * (9 - len(prediction))

def create_class_chart():
    """Создает график успеваемости класса."""
    grades = ['Отлично', 'Хорошо', 'Удовлетворительно', 'Неудовлетворительно']
    counts = [8, 9, 10, 5]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(grades, counts, color=['#4CAF50', '#8BC34A', '#FFC107', '#F44336'])

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{height}', ha='center', va='bottom')

    ax.set_ylabel('Количество учеников')
    ax.set_title('Статистика по 10Б классу')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=80)
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def create_risk_chart(prediction):
    prediction = prediction[:len(subjects)]
    risk_levels = [5 - grade + 1 for grade in prediction]
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#ff5252' if r >= 4 else '#ffb74d' if r >= 3 else '#66bb6a' for r in risk_levels]
    ax.barh(subjects, risk_levels, color=colors)
    ax.set_xlim(0, 5)
    ax.set_xticks(range(0, 6))
    ax.set_xlabel('Уровень риска (1-5)', fontsize=12)
    ax.set_title('Риски успеваемости по предметам', fontsize=14, pad=20)
    plt.tight_layout()
    return fig


def get_recommendations(prediction):
    risk_subjects = [subject for subject, grade in zip(subjects, prediction) if grade in (2, 3)]
    if risk_subjects:
        return f"Подтяните знания в следующих предметах: {', '.join(risk_subjects)}"
    return "Нет предметов с низкими оценками."


def calculate_average_grade(prediction):
    return round(sum(prediction) / len(prediction), 2)


def generate_grades_html(prediction):
    prediction = (prediction + [0] * 9)[:9]
    headers = ''.join(f"<th>{subj}</th>" for subj in subjects)
    values = ''.join(f"<td>{int(grade)}</td>" for grade in prediction)
    return f"""
    <table class="grades-table">
        <tr>{headers}</tr>
        <tr>{values}</tr>
    </table>
    """


custom_css = """

.full-width {
    width: 100%;
    padding: 0;
    margin: 0;
}
.app.svelte-wpkpf6.svelte-wpkpf6:not(.fill_width) {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important; 
}
.main-container {
    font-family: 'Segoe UI', sans-serif;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    display: flex;
    align-items: center;
    justify-content: center; /* Центрирует содержимое */
    padding: 15px 0; /* Убираем отступы по бокам */
    background-color: #F3F8FF;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.logo {
    font-size: 24px;
    font-weight: bold;
    color: #02033B;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo span:first-child {
    background: linear-gradient(90deg, #FFC247, #FC6F11);
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: normal;
}

.first-page {
    display: flex;
    flex-direction: column;
}

.main-text {
    font-size: 52px;
    font-weight: 800;
    color: #02033B;
    margin-bottom: 30px;
    line-height: 1.2;
}

.sub-text {
    font-size: 18px;
    color: #1B1E56;
    margin-bottom: 40px;
    max-width: 80%;
}

.start-button {
    background: linear-gradient(90deg, #FFCB52, #FCA024);
    border: none;
    border-radius: 50px;
    padding: 14px 28px;
    font-size: 19px;
    font-weight: 700;
    color: black;
    cursor: pointer;
    width: fit-content;
}

/* Стили для страницы входа */
.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 40px;
}

.login-title {
    font-size: 52px;
    font-weight: 600;
    margin-bottom: 30px;
    text-align: center;
}

.login-input {
    width: 100%;
    padding: 12px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.login-button {
    width: 100%;
    padding: 12px;
    background-color: #000;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 15px;
}

.recovery-link {
    text-align: center;
    color: #000;
    text-decoration: underline;
    cursor: pointer;
    font-size: 14px;
    background: none !important;
    border: none !important;
}

/* Стили для страницы восстановления */
.recovery-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 40px;
}

.recovery-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 15px;
    text-align: center;
}

.recovery-text {
    text-align: center;
    margin-bottom: 30px;
    font-size: 16px;
}

.recovery-input {
    width: 100%;
    padding: 12px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.recovery-button {
    width: 100%;
    padding: 12px;
    background-color: #000;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
}

.back-button {
    display: block;
    margin-top: 20px;
    text-align: center;
    color: #000;
    text-decoration: underline;
    cursor: pointer;
    font-size: 14px;
    background: none !important;
    border: none !important;
}

/* Стили для страницы информации */
.profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
}

.profile-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
}

.profile-section {
    margin-bottom: 30px;
}

.profile-divider {
    border-top: 1px solid #ddd;
    margin: 20px 0;
}

.analyze-button {
    background-color: #000;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin: 20px 0;
    display: block;
    width: 100%;
}

.grades-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.grades-table th, .grades-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}

.grades-table th {
    background-color: #f2f2f2;
}

.risk-chart-container {
    margin: 20px 0;
    width: 100%;
}

.risk-scale {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 600px;
    margin: 10px auto 0;
}

.risk-scale-item {
    text-align: center;
    width: 25%;
}

.recommendations {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 4px;
    margin-top: 20px;
}

/* Стили для страницы учителя */
.class-teacher-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
}

.class-teacher-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
}

.class-selector {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}

.class-selector select, .class-selector input {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.stats-container {
    margin: 20px 0;
}

.stats-scale {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

.student-list {
    margin: 15px 0;
    padding: 0;
    list-style-type: none;
}

.student-list li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.risk-scale-numbers {
    display: flex;
    justify-content: space-between;
    width: 100px;
    margin: 10px 0;
}

footer {
    display: none !important;
}
"""
def show_home():
    return [
        gr.update(visible=True),  # home_page
        gr.update(visible=False),  # entry_page
        gr.update(visible=False),  # recovery_page
        gr.update(visible=False),  # student_page
        gr.update(visible=False)  # teacher_page
    ]


def show_entry():
    return [
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False)
    ]


def show_recovery():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False)
    ]


# def show_student(student_id=None):
#     return [
#         gr.update(visible=False),  # home_page
#         gr.update(visible=False),  # entry_page
#         gr.update(visible=False),  # recovery_page
#         gr.update(visible=True),   # student_page
#         gr.update(visible=False),  # teacher_page
#         gr.update(),  # placeholder для risk_chart
#         gr.update(),  # placeholder для recommendations
#         gr.update(),  # placeholder для avg_grade
#         gr.update(),  # placeholder для prediction
#         gr.update(),  # placeholder для grades_html
#         gr.update(),  # placeholder для student_info
#         student_id  # Обновляем current_student_id
#     ]
def show_student(student_id=None):
    return [
        gr.update(visible=False),  # home_page
        gr.update(visible=False),  # entry_page
        gr.update(visible=False),  # recovery_page
        gr.update(visible=True),   # student_page
        gr.update(visible=False)   # teacher_page
    ]

def show_teacher():
    return [
        gr.update(visible=False),  # home_page
        gr.update(visible=False),  # entry_page
        gr.update(visible=False),  # recovery_page
        gr.update(visible=False),  # student_page
        gr.update(visible=True),  # teacher_page
        gr.update(value=""),  # student_info_display (или None, если не нужен текст)
        None  # current_user_id
    ]

def check_user(login, password):
    users_db = SavesDataUsers().get_data_user()
    for user in users_db:
        if users_db[user]["login"] == login and users_db[user]["password"] == password:
            if users_db[user]["type"] == "student":
                stud_data = SavesDataStudents().get_data_student(user_id=user)
                student_id = stud_data['student_id']
                user_info_text = (
                    f"**ФИО:** {stud_data['surname']} {stud_data['name']} {stud_data['patronymic']}<br>"
                    f"**Класс:** {stud_data['number']}{stud_data['liter']}"
                )
                # Теперь возвращаем только то, что указано в outputs
                return [
                    *show_student(student_id),
                    user_info_text,
                    student_id
                ]
            elif users_db[user]["type"] in ["teacher", "class_teacher", "director"]:
                user_info_text = "Я УЧИТЕЛЬ, Я УЧИИИИИИТЕЕЕЛЬ ДЕТКА!"
                return [
                    *show_teacher(),
                    user_info_text,
                    None
                ]
    raise gr.Error("Неверный логин или пароль")


def analyze_student(student_id):
    try:
        stud_data = SavesDataStudents().get_data_student(student_id=student_id)
        print(f'{stud_data}')
        class_num = stud_data['number']
        prediction = predict_grades(student_id, class_num)
        risk_fig = create_risk_chart(prediction)
        recommendations = get_recommendations(prediction)
        avg_grade = calculate_average_grade(prediction)
        grades_html = generate_grades_html(prediction)
        return [
            risk_fig,
            gr.Markdown(f"<div class='recommendations'>{recommendations}</div>"),
            avg_grade,
            grades_html,
            prediction
        ]
    except Exception as e:
        raise gr.Error(f"Ошибка анализа: {str(e)}")


with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
    current_user_id = gr.State()
    create_header()
    with gr.Column(visible=True, elem_classes=["main-container"]) as home_page:
        gr.Markdown("""
        <div class="first-page">
            <div class="main-text">Система категоризации обучающихся<br>по уровням прогнозируемой успеваемости</div>
            <div class="sub-text">На основе данных об оценках, посещаемости и других показателях система определяет риск низкой успеваемости.</div>
        </div>
        """)
        start_btn = gr.Button("Начать работу!", elem_classes="start-button")

    with gr.Column(visible=False, elem_classes=["login-container"]) as entry_page:
        gr.Markdown("<div class='login-title'>Вход</div>")
        login_input = gr.Textbox(label="", placeholder="Логин", elem_classes="login-input")
        password_input = gr.Textbox(label="", placeholder="Пароль", type="password", elem_classes="login-input")
        login_btn = gr.Button("Вход", elem_classes="login-button")
        recovery_btn_link = gr.Button("восстановить логин/пароль", elem_classes="recovery-link")

    with gr.Column(visible=False, elem_classes=["recovery-container"]) as recovery_page:
        gr.Markdown("""<div class="recovery-title">Восстановление логина/пароля</div>""")
        gr.Markdown(
            """<div class="recovery-text">Введите эл. почту или номер телефона, для отправки письма на вашу эл. почту</div>""")
        recovery_input = gr.Textbox(label="", placeholder="Эл.почта / Номер телефона", elem_classes="recovery-input")
        recovery_btn = gr.Button("Отправить", elem_classes="recovery-button")

    with gr.Column(visible=False, elem_classes=["profile-container"]) as student_page:
        gr.Markdown("<div class='profile-title'>Информация о себе</div>")
        user_info_display = gr.Markdown(elem_classes="student-info", show_label=False)
        analyze_btn = gr.Button("Проанализировать", elem_classes="analyze-button")

        avg_grade_output = gr.Textbox(label="Средняя оценка")
        grades_table = gr.HTML("")
        gr.Markdown("### Ваша успеваемость")
        risk_chart = gr.Plot(label="Риски успеваемости")
        gr.Markdown("### Риски")
        gr.Markdown("""
                        **Шкала уровней риска:**
                        - 1-2: Низкий риск
                        - 3: Средний риск
                        - 4-5: Высокий риск
                        """)
        gr.Markdown("### Рекомендации")
        recommendations_output = gr.Markdown("")

    class_chart = create_class_chart()

    with gr.Column(visible=False, elem_classes=["class-teacher-container"]) as teacher_page:
        gr.Markdown("""<div class="class-teacher-title">Информация о классе</div>""")

        with gr.Column():
            gr.Markdown("Выберите класс и предмет, который необходимо проанализировать.")

            with gr.Row(elem_classes="class-selector"):
                subject = gr.Dropdown(subjects, label="Предмет")
                class_num = gr.Number(label="Класс", value=8)
                class_letter = gr.Textbox(label="Литер класса", value="Б")

            analyze_btn_teacher = gr.Button("Проанализировать", elem_classes="analyze-button")
            gr.Markdown("""<div class="profile-divider"></div>""")

        


    start_btn.click(
        lambda: [gr.update(visible=False), gr.update(visible=True)],
        outputs=[home_page, entry_page]
    )

    recovery_btn_link.click(
        show_recovery,
        outputs=[
            home_page, entry_page, recovery_page, student_page, teacher_page
        ]
    )
    login_btn.click(
        fn=check_user,
        inputs=[login_input, password_input],
        outputs=[
            home_page, entry_page, recovery_page, student_page, teacher_page,
            user_info_display, current_user_id
        ]
    )

    analyze_btn.click(
        fn=analyze_student,
        inputs=[current_user_id],
        outputs=[
            risk_chart,
            recommendations_output,
            avg_grade_output,
            grades_table,
            gr.State()
        ]
    )

demo.launch(share=True)
