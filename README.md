# Тестовое задание: Анализ лайков во ВКонтакте

## Адрес страницы
Анализируемая страница: (https://vk.com/mnv_1997)

Примечание: страница друга(данные взяты с его согласия)

Таблица в формате CSV приложена в файле: [data.csv](data.csv)

---

## Сбор данных

Для сбора данных использовался официальный VK API. Собраны поля:
- ID поста
- Дата публикации
- Количество лайков
- Текст поста

День недели рассчитан программно на основе даты (`1 = понедельник, ..., 7 = воскресенье`).

Основной код приложен в файле: [main.py](main.py)

---

## SQL - запросы 

Работа проводилась с помощью СУБД PostgreSQL в программе pgAdmin 4

### 1. Вывод количества лайков в зависимости от времени публикации

**Запрос:**
```sql
SELECT
    CASE
        WHEN EXTRACT(HOUR FROM дата_поста) >= 0 AND EXTRACT(HOUR FROM дата_поста) < 8 THEN '00:00–08:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 8 AND EXTRACT(HOUR FROM дата_поста) < 12 THEN '08:00–12:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 12 AND EXTRACT(HOUR FROM дата_поста) < 18 THEN '12:00–18:00'
        ELSE '18:00–00:00'
    END AS Временной_период,
    COUNT(*) AS Количество_постов,
    SUM(количество_лайков) AS Общая_сумма_лайков,
    ROUND(AVG(количество_лайков), 2) AS Среднее_количество
FROM posts
GROUP BY
    CASE
        WHEN EXTRACT(HOUR FROM дата_поста) >= 0 AND EXTRACT(HOUR FROM дата_поста) < 8 THEN '00:00–08:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 8 AND EXTRACT(HOUR FROM дата_поста) < 12 THEN '08:00–12:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 12 AND EXTRACT(HOUR FROM дата_поста) < 18 THEN '12:00–18:00'
        ELSE '18:00–00:00'
    END
ORDER BY
    MIN(EXTRACT(HOUR FROM дата_поста));
```

**Результат запроса:**

<img width="813" height="182" alt="image" src="https://github.com/user-attachments/assets/8b4fdb7c-1e94-45d2-8999-345217822cbb" />

### 2. Вывод количества лайков по дням недели

**Запрос:**
```sql
SELECT
    день_недели,
    COUNT(*) AS Количество_постов,
    SUM(количество_лайков) AS Общая_сумма_лайков,
    ROUND(AVG(количество_лайков), 2) AS Среднее_количество
FROM posts
GROUP BY день_недели
ORDER BY день_недели;
```

**Результат запроса:**

<img width="768" height="276" alt="image" src="https://github.com/user-attachments/assets/900fe961-325e-4e0c-8c63-a929a3710bed" />

### 3. Объединённые данные

**Запрос:**
```sql
SELECT
    день_недели,
    CASE
        WHEN EXTRACT(HOUR FROM дата_поста) >= 0 AND EXTRACT(HOUR FROM дата_поста) < 8 THEN '00:00–08:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 8 AND EXTRACT(HOUR FROM дата_поста) < 12 THEN '08:00–12:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 12 AND EXTRACT(HOUR FROM дата_поста) < 18 THEN '12:00–18:00'
        ELSE '18:00–00:00'
    END AS Временной_период,
    COUNT(*) AS Количество_постов,
    SUM(количество_лайков) AS Общая_сумма_лайков,
    ROUND(AVG(количество_лайков), 2) AS Среднее_количество
FROM posts
GROUP BY
    день_недели,
    CASE
        WHEN EXTRACT(HOUR FROM дата_поста) >= 0 AND EXTRACT(HOUR FROM дата_поста) < 8 THEN '00:00–08:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 8 AND EXTRACT(HOUR FROM дата_поста) < 12 THEN '08:00–12:00'
        WHEN EXTRACT(HOUR FROM дата_поста) >= 12 AND EXTRACT(HOUR FROM дата_поста) < 18 THEN '12:00–18:00'
        ELSE '18:00–00:00'
    END
ORDER BY
    день_недели, MIN(EXTRACT(HOUR FROM дата_поста));
```

Результат запроса приложен в файле: [request-3.csv](request-3.csv)

### 4. Зависимость количества лайков от года

**Запрос:**
```sql
SELECT
    EXTRACT (YEAR FROM дата_поста) AS Год,
	COUNT(*) AS Количество_постов,
    SUM(количество_лайков) AS Общая_сумма_лайков,
    ROUND(AVG(количество_лайков), 2) AS Среднее_количество
FROM posts
GROUP BY Год
ORDER BY Год;
```

**Результат запроса:**

<img width="723" height="425" alt="image" src="https://github.com/user-attachments/assets/12753bda-f694-431b-acd9-7f963616e7de" />

### 5. Влияние промежутка времени между публикациями

**Запрос:**
```sql
SELECT
    id_поста,
    дата_поста,
    количество_лайков,
    LAG(дата_поста) OVER (ORDER BY дата_поста) AS дата_предыдущего_поста,
    дата_поста - LAG(дата_поста) OVER (ORDER BY дата_поста) AS интервал_между_постами
FROM posts
ORDER BY дата_поста;
```

---

# Визуализация

Для более полной картины было построено несколько графиков.

Они приложены в файле [graphs.ipynb](graphs.ipynb)


