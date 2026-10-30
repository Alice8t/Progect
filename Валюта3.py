from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import requests

currencies = {
    'EUR': 'Евро',
    'USD': 'Доллар США',
    'JPY': 'Японская йена',
    'GBP': 'Фунт стерлингов',
    'AUD': 'Австралийский доллар',
    'CAD': 'Канадский доллар',
    'CHF': 'Швейцарский франк',
    'CNY': 'Китайский юань',
    'RUB': 'Российский рубль',
    'KZT': 'Казахстанский тенге',
    'UZS': 'Узбекский сум'
}

def update_base_label(event, label_widget, combobox_widget):
    code = combobox_widget.get()
    name = currencies.get(code, 'Неизвестная валюта')
    label_widget.config(text=name)

def update_target_label(event):
    code = target_combobox.get()
    name = currencies.get(code, 'Неизвестная валюта')
    target_label.config(text=name)

# Старая логика: пока использует только base1, игнорируя base2
def exchange():
    base1_code = base1_combobox.get().strip()
    # base2_code сейчас не участвует в расчётах
    base2_code = base2_combobox.get().strip()
    target_code = target_combobox.get().strip()

    if not base1_code or not target_code:
        mb.showwarning('Внимание', 'Пожалуйста, выберите базовую и целевую валюты.')
        return

    if target_code not in currencies:
        mb.showerror('Ошибка', f'Валюта {target_code} не поддерживается в этом приложении.')
        return

    results = []

    # Пока делаем запрос только для base1 (логика будет расширена во 2-м коммите)
    for base_code in [base1_code]:
        try:
            url = f'https://open.er-api.com/v6/latest/{base_code}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('result') != 'success':
                error_type = data.get('error-type', 'Неизвестная ошибка API')
                mb.showerror('Ошибка API', f'API вернул ошибку для {base_code}: {error_type}')
                return

            rates = data.get('rates', {})
            if target_code in rates:
                exchange_rate = rates[target_code]
                base_name = currencies.get(base_code, base_code)
                target_name = currencies.get(target_code, target_code)
                results.append(f'{exchange_rate:.4f} {target_name} за 1 {base_name}')
            else:
                mb.showerror('Ошибка данных', f'Курс для пары {base_code}->{target_code} не найден в данных API.')
                return

        except requests.exceptions.Timeout:
            mb.showerror('Ошибка сети', f'Превышено время ожидания ответа от сервера для {base_code}.')
            return
        except requests.exceptions.ConnectionError:
            mb.showerror('Ошибка сети', f'Не удалось подключиться к серверу для {base_code}. Проверьте интернет.')
            return
        except requests.exceptions.RequestException as er:
            mb.showerror('Ошибка сети', f'Произошла ошибка при запросе для {base_code}: {er}')
            return
        except Exception as er:
            mb.showerror('Критическая ошибка', f'Непредвиденная ошибка: {er}')
            return

    if results:
        message = 'Курсы обмена:\n\n' + '\n'.join(results)
        mb.showinfo('Курсы обмена', message)

root = Tk()
root.title('Курсы обмена валют (UI с двумя базами)')
root.geometry('420x340')

# --- Первая базовая валюта (уже была) ---
Label(root, text='Базовая валюта 1').pack(pady=(15, 0))
base1_combobox = ttk.Combobox(root, values=list(currencies.keys()), state='readonly')
base1_combobox.pack(pady=3, padx=10)
base1_combobox.current(0)
base1_label = ttk.Label(root, text=currencies[base1_combobox.get()], font=('Arial', 10, 'bold'))
base1_label.pack()
base1_combobox.bind('<<ComboboxSelected>>', lambda e: update_base_label(e, base1_label, base1_combobox))

# --- ВТОРАЯ БАЗОВАЯ ВАЛЮТА (добавлена в 1-м коммите) ---
Label(root, text='Базовая валюта 2').pack(pady=(15, 0))
base2_combobox = ttk.Combobox(root, values=list(currencies.keys()), state='readonly')
base2_combobox.pack(pady=3, padx=10)
base2_combobox.current(1)  # По умолчанию USD
base2_label = ttk.Label(root, text=currencies[base2_combobox.get()], font=('Arial', 10, 'bold'))
base2_label.pack()
base2_combobox.bind('<<ComboboxSelected>>', lambda e: update_base_label(e, base2_label, base2_combobox))

# --- Целевая валюта (уже была) ---
Label(root, text='Целевая валюта').pack(pady=(15, 0))
target_combobox = ttk.Combobox(root, values=list(currencies.keys()), state='readonly')
target_combobox.pack(pady=3, padx=10)
target_combobox.current(8)
target_label = ttk.Label(root, text=currencies[target_combobox.get()], font=('Arial', 10, 'bold'))
target_label.pack()
target_combobox.bind('<<ComboboxSelected>>', update_target_label)

# Кнопка
btn = Button(root, text='Получить курсы обмена', command=exchange, bg='#dddddd', padx=10, pady=5)
btn.pack(pady=25)

root.mainloop()
