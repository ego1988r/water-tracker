import flet as ft
import os
from datetime import datetime
    
DATA_FILE = os.path.join(os.path.dirname(__file__), "water_data.txt")
ALCOHOL_FILE = os.path.join(os.path.dirname(__file__), "alcohol_data.txt")
USER_FILE = os.path.join(os.path.dirname(__file__), "user_data.txt")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.txt")
RESET_FILE =os.path.join(os.path.dirname(__file__), "last_reset.txt")
    
def load_data(file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except:
                return ""
        return ""
    
def load_float(file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return float(f.read().strip())
            except:
                return 0.0
        return 0.0
    
def save_data(file_path, value):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(value))
    
def get_today_history():
        today = datetime.now().strftime("%Y-%m-%d")
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(today):
                        history.append(line.strip())
        return history
    
def add_to_history(drink_name, volume, effective_volume):
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        if effective_volume == volume:
            record = f"{today} — {drink_name} {volume} мл"
        else:
            record = f"{today} — {drink_name} {volume} мл (учтено {effective_volume} мл)"
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(record + "\n")
    
def show_snack(page, message, is_warning=False):
        color = "#FF5252" if is_warning else "#4FC3F7"
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF"),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()
    
def main(page: ft.Page):
        page.title = "Живой мужик"
        page.window.width = 450
        page.window.height = 800
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#4FC3F7",
                secondary="#00BCD4",
                background="#162436",
                surface="#1F3550",
                on_primary="#FFFFFF",
                on_secondary="#FFFFFF",
                on_background="#FFFFFF",
                on_surface="#FFFFFF",
            ),
        )
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
    
        def show_onboarding(page):
            page.clean()
            name_input = ft.TextField(
                hint_text="Как тебя зовут?",
                width=300,
                text_align=ft.TextAlign.CENTER,
                bgcolor="#1F3550",
                color="#FFFFFF",
                border_color="#4FC3F7",
            )
            def go_to_weight(e):
                name = name_input.value.strip()
                if name == "":
                    show_snack(page, "Введи имя!", is_warning=True)
                    return
                save_data(USER_FILE, name.capitalize())
                show_weight_screen(page, name.capitalize())
            content = ft.Column([
                ft.Container(height=80),
                ft.Text("Живой мужик", size=32, weight=ft.FontWeight.BOLD, color="#4FC3F7", text_align=ft.TextAlign.CENTER),
                ft.Container(height=40),
                ft.Text("Давай познакомимся", size=20, color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                ft.Container(height=30),
                name_input,
                ft.Container(height=30),
                ft.ElevatedButton("Далее", on_click=go_to_weight, width=200, height=50, bgcolor="#4FC3F7", color="#162436"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
            page.add(content)
            page.update()
    
        def show_weight_screen(page, name):
            page.clean()
            weight_input = ft.TextField(
                hint_text="Сколько ты весишь (кг)?",
                width=300,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor="#1F3550",
                color="#FFFFFF",
                border_color="#4FC3F7",
            )
            def start_tracker(e):
                try:
                    weight = float(weight_input.value.replace(',', '.'))
                    if weight < 30 or weight > 300:
                        show_snack(page, "Введи нормальный вес!", is_warning=True)
                        return
                    save_data(USER_FILE, f"{name}|{weight}")
                    show_tracker(page, name, weight)
                except:
                    show_snack(page, "Введи число!", is_warning=True)
            content = ft.Column([
                ft.Container(height=80),
                ft.Text(f"Привет, {name}!", size=28, weight=ft.FontWeight.BOLD, color="#4FC3F7", text_align=ft.TextAlign.CENTER),
                ft.Container(height=30),
                ft.Text("Рассчитаем норму воды", size=18, color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                ft.Text("Формула: вес × 30 мл", size=14, color="#78909C", text_align=ft.TextAlign.CENTER),
                ft.Container(height=30),
                weight_input,
                ft.Container(height=30),
                ft.ElevatedButton("Начать", on_click=start_tracker, width=200, height=50, bgcolor="#4FC3F7", color="#162436"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
            page.add(content)
            page.update()
    
        def show_tracker(page, name, weight=None):
            page.clean()
            user_data = load_data(USER_FILE).split("|")
            saved_name = user_data[0].capitalize() if len(user_data) > 0 else name
            saved_weight = float(user_data[1]) if len(user_data) > 1 else (weight if weight else 140.0)
            if weight is None:
                weight = saved_weight
            norm = weight * 30
            drunk = load_float(DATA_FILE)
            alcohol = load_float(ALCOHOL_FILE)
            current_volume = 250
            
            percent = int(drunk / norm * 100) if drunk > 0 else 0
            progress_text = ft.Text(f"Выпито: {int(drunk)} мл из {int(norm)} мл ({percent}%)", size=20, color="#4FC3F7", weight=ft.FontWeight.BOLD)
            progress_bar = ft.ProgressBar(value=drunk / norm if drunk < norm else 1.0, color="#00BCD4", bgcolor="#1F3550", height=16, border_radius=8)
    
            remaining = int(norm - drunk)
            hour = datetime.now().hour
            if remaining <= 0:
                fact_text = "Норма выполнена. Поддерживай уровень."
            elif hour < 10:
                fact_text = f"Утро. Осталось {remaining} мл. Выпей стакан воды, чтобы запустить организм."
            elif hour < 18:
                fact_text = f"Осталось {remaining} мл. Это примерно {remaining // 250} стаканов."
            elif hour < 22:
                fact_text = f"Вечер. Осталось {remaining} мл. Старайся допить до 20:00, потом лучше не пить."
            else:
                fact_text = f"Поздно. Остаток {remaining} мл переносится на завтра, чтобы не бегать в туалет ночью."
            status_text = ft.Text(fact_text, size=14, color="#B0BEC5", text_align=ft.TextAlign.CENTER, italic=True)
    
            alcohol_text = ft.Text(f"Алкоголь сегодня: {int(alcohol)} мл", size=14, color="#FF8A80" if alcohol > 0 else "#78909C")
            vol_text = ft.Text(f"Выбран объём: {current_volume} мл", size=16, color="#B0BEC5")
    
            vol_buttons = {}
            for v in [200, 250, 500]:
                vol_buttons[v] = ft.ElevatedButton(f"{v} мл", width=110, height=45, color="#162436" if v == current_volume else "#FFFFFF", bgcolor="#4FC3F7" if v == current_volume else "#1F3550")
        
            custom_btn = ft.ElevatedButton("Свой", width=110, height=45, color="#FFFFFF", bgcolor="#1F3550")
            custom_input = ft.TextField(hint_text="мл", width=100, height=45, text_align=ft.TextAlign.CENTER, keyboard_type=ft.KeyboardType.NUMBER, bgcolor="#1F3550", color="#FFFFFF", visible=False)
            apply_custom_btn = ft.ElevatedButton("OK", width=80, height=45, bgcolor="#4FC3F7", color="#162436", visible=False)
        
            def set_volume(vol):
                def handler(e):
                    nonlocal current_volume
                    current_volume = vol
                    vol_text.value = f"Выбран объём: {current_volume} мл"
                    for v, btn in vol_buttons.items():
                        btn.color = "#162436" if v == current_volume else "#FFFFFF"
                        btn.bgcolor = "#4FC3F7" if v == current_volume else "#1F3550"
                    custom_btn.color = "#FFFFFF"
                    custom_btn.bgcolor = "#1F3550"
                    custom_input.visible = False
                    apply_custom_btn.visible = False
                    page.update()
                return handler
    
            def enable_custom(e):
                for v, btn in vol_buttons.items():
                    btn.color = "#FFFFFF"
                    btn.bgcolor = "#1F3550"
                custom_btn.color = "#162436"
                custom_btn.bgcolor = "#4FC3F7"
                custom_input.visible = True
                apply_custom_btn.visible = True
                page.update()
    
            def apply_custom_volume(e):
                nonlocal current_volume
                try:
                    val = int(custom_input.value)
                    if val > 0:
                        current_volume = val
                        vol_text.value = f"Выбран объём: {current_volume} мл"
                        custom_input.visible = False
                        apply_custom_btn.visible = False
                        custom_btn.color = "#FFFFFF"
                        custom_btn.bgcolor = "#1F3550"
                        page.update()
                except:
                    show_snack(page, "Введи число!", is_warning=True)
    
            vol_buttons[200].on_click = set_volume(200)
            vol_buttons[250].on_click = set_volume(250)
            vol_buttons[500].on_click = set_volume(500)
            custom_btn.on_click = enable_custom
            apply_custom_btn.on_click = apply_custom_volume
            
            def add_drink(drink_name, coeff):
                def handler(e):
                    nonlocal drunk
                    if coeff == 0.0:
                        return
                    effective = int(current_volume * coeff)
                    drunk += effective
                    p = int(drunk / norm * 100)
                    progress_text.value = f"Выпито: {int(drunk)} мл из {int(norm)} мл ({p}%)"
                    progress_bar.value = drunk / norm if drunk < norm else 1.0
                    remaining = int(norm - drunk)
                    glasses = remaining // 250 if remaining > 0 else 0
                    hour = datetime.now().hour
                    if remaining <= 0:
                        status_text.value = "Норма выполнена. Поддерживай уровень."
                    elif hour < 10:
                        status_text.value = f"Утро. Осталось {remaining} мл. Выпей стакан воды, чтобы запустить организм."
                    elif hour < 18:
                        status_text.value = f"Осталось {remaining} мл. Это примерно {remaining // 250} стаканов."
                    elif hour < 22:
                        status_text.value = f"Вечер. Осталось {remaining} мл. Старайся допить до 20:00, потом лучше не пить."
                    else:
                        status_text.value = f"Поздно. Остаток {remaining} мл переносится на завтра, чтобы не бегать в туалет ночью." 
                    save_data(DATA_FILE, drunk)
                    add_to_history(drink_name, current_volume, effective)
                    update_history_list()
                    show_snack(page, f"Добавлено: {drink_name} {current_volume} мл")
                    page.update()
                return handler
        
            def add_alcohol(e):
                nonlocal alcohol
                alcohol += current_volume
                alcohol_text.value = f"Алкоголь сегодня: {int(alcohol)} мл"
                alcohol_text.color = "#FF8A80"
                save_data(ALCOHOL_FILE, alcohol)
                add_to_history("Алкоголь", current_volume, 0)
                update_history_list()
                show_snack(page, "Алкоголь обезвоживает! Выпей стакан чистой воды.", is_warning=True)
                page.update()
        
            history_list = ft.Column([], spacing=8, scroll=ft.ScrollMode.AUTO)
        
            def update_history_list():
                history_list.controls.clear()
                today_history = get_today_history()
                if not today_history:
                    history_list.controls.append(ft.Text("Пока нет записей за сегодня", color="#78909C", size=14))
                else:
                    for record in reversed(today_history):
                        history_list.controls.append(ft.Text(record, color="#FFFFFF", size=14, font_family="Consolas"))
                page.update()
        
            update_history_list()
    
            def reset_day(e):
                nonlocal drunk, alcohol
                drunk = 0
                alcohol = 0
                progress_text.value = f"Выпито: 0 мл из {int(norm)} мл (0%)"
                progress_bar.value = 0
                alcohol_text.value = "Алкоголь сегодня: 0 мл"
                alcohol_text.color = "#78909C"
                status_text.value = f"Осталось {int(norm)} мл. Начни день со стакана воды."
                save_data(DATA_FILE, 0)
                save_data(ALCOHOL_FILE, 0)
                today = datetime.now().strftime("%Y-%m-%d")
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        for line in lines:
                            if not line.startswith(today):
                                f.write(line)
                update_history_list()
                show_snack(page, "День сброшен")
                page.update()
        
            drinks_row1 = ft.Row([
                ft.ElevatedButton("Вода", on_click=add_drink("Вода", 1.0), width=130, height=55, bgcolor="#1F3550"),
                ft.ElevatedButton("Кофе", on_click=add_drink("Кофе", 0.9), width=130, height=55, bgcolor="#1F3550"),
                ft.ElevatedButton("Чай", on_click=add_drink("Чай", 0.9), width=130, height=55, bgcolor="#1F3550"),
            ])
            drinks_row2 = ft.Row([
                ft.ElevatedButton("Молоко", on_click=add_drink("Молоко", 1.0), width=130, height=55, bgcolor="#1F3550"),
                ft.ElevatedButton("Газировка", on_click=add_drink("Газировка", 0.9), width=130, height=55, bgcolor="#1F3550"),
                ft.ElevatedButton("Сок", on_click=add_drink("Сок", 0.9), width=130, height=55, bgcolor="#1F3550"),
            ])
            drinks_row3 = ft.Row([
                ft.ElevatedButton("Энергетик", on_click=add_drink("Энергетик", 0.7), width=130, height=55, bgcolor="#1F3550"),
                ft.ElevatedButton("Алкоголь", on_click=add_alcohol, width=130, height=55, bgcolor="#3E1F2E"),
            ])
            
            content = ft.Column([
                ft.Text(f"Привет, {saved_name}!", size=24, color="#4FC3F7", weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                progress_text,
                progress_bar,
                ft.Container(height=10),
                status_text,
                ft.Container(height=10),
                alcohol_text,
                ft.Container(height=20),
                vol_text,
                ft.Container(height=10),
                ft.Row([vol_buttons[200], vol_buttons[250], vol_buttons[500], custom_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([custom_input, apply_custom_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
                drinks_row1,
                drinks_row2,
                drinks_row3,
                ft.Container(height=20),
                ft.Divider(color="#1F3550"),
                ft.Text("История за сегодня:", size=16, color="#B0BEC5", weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(content=history_list, height=200, bgcolor="#1F3550", border_radius=10, padding=10),
                ft.Container(height=20),
                ft.ElevatedButton("Сбросить день", on_click=reset_day, width=200, height=50, color="#FFFFFF", bgcolor="#C62828"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
            page.add(content)
            page.update()
    
        saved_name = load_data(USER_FILE)
        if saved_name == "":
            show_onboarding(page)
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            last_reset = load_data(RESET_FILE)
            if last_reset != today:
                save_data(DATA_FILE, 0)
                save_data(ALCOHOL_FILE, 0)
                save_data(RESET_FILE, today)
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                        f.write("")
            show_tracker(page, saved_name) 
        
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8501)
