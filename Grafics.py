import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Загрузка данных из Excel, пропуская первую строку
file_path = 'Data.xlsx'
df = pd.read_excel(file_path, engine='openpyxl', skiprows=1)

# Преобразуем имена столбцов в строки
df.columns = df.columns.astype(str)

# Выводим первые несколько строк данных
print(df.head())

# Определение столбца с временными метками
time_column = df.columns[0]


# Функция для обработки времени
def parse_time(value):
    try:
        return datetime.datetime.strptime(value.split()[1], '%H-%M-%S.%f')
    except (ValueError, IndexError):
        return None


# Преобразование времени с обработкой ошибок
df['Datetime'] = df[time_column].apply(parse_time)

# Удаление строк с некорректными временными метками
df = df.dropna(subset=['Datetime'])

# Вычисление времени в секундах относительно первой временной метки
initial_time = df['Datetime'].iloc[0]
df['Seconds'] = (df['Datetime'] - initial_time).dt.total_seconds()

# Определение максимального времени
max_time = df['Seconds'].max()

# Определение столбца перед '0.1' и столбцов '0.1', '0.2', '0.3'
index_0_1 = df.columns.get_loc('0.1')
columns = {
    'FR': df.columns[index_0_1 - 1],  # Предположим, что это столбец '0.0'
    'FL': '0.1',
    'RR': '0.2',
    'RL': '0.3'
}

# Запрашиваем у юзера, какие столбцы включить в график
print("Доступные столбцы для графика: ", list(columns.keys()))

while True:
    col_input = input(
        "Введите столбцы для отображения на графике (FR, FL, RR, RL) через запятую или 'stop' для завершения: ").strip()
    if col_input.lower() == 'stop':
        break

    selected_columns = [col.strip() for col in col_input.split(',')]

    # Проверка корректности ввода
    valid_columns = [col for col in selected_columns if col in columns]

    if valid_columns:
        # Вывод максимального времени
        print(f"Максимальное доступное время: {max_time} секунд")

        # Запрашиваем у пользователя интервал времени для отображения
        start_time = float(input("Введите начальное время (в секундах): ").strip())
        end_time = float(input("Введите конечное время (в секундах): ").strip())

        # Проверка корректности интервала времени
        if start_time < 0 or end_time > max_time or start_time >= end_time:
            print(
                f"Некорректный интервал времени. Убедитесь, что начальное время >= 0, конечное время <= {max_time}, и начальное время меньше конечного.")
            continue

        # Фильтрация данных по выбранному интервалу времени
        filtered_df = df[(df['Seconds'] >= start_time) & (df['Seconds'] <= end_time)]

        # Построение графика для выбранных столбцов и интервала времени
        plt.figure(figsize=(14, 8))
        for col in valid_columns:
            plt.plot(filtered_df['Seconds'], filtered_df[columns[col]], label=col)
        plt.xlabel('Время (секунды)')
        plt.ylabel('Давление')
        plt.title(
            f'Изменение давлениz по времени для {", ".join(valid_columns)} с {start_time} сек по {end_time} сек')
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        print("Ни один из введенных столбцов не найден в данных.")
