import requests
import psycopg2
from datetime import datetime

# Вставляются нужные значения
VK_TOKEN = 'Сервисный ключ доступа'
VK_DOMAIN = 'Короткое имя страницы ВКонтакте'
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'vk_posts',
    'user': 'postgres',
    'password': 'пароль'
}

# Проверка обязательных параметров
if not VK_TOKEN:
    raise ValueError("Отсутствует VK_TOKEN")
if not VK_DOMAIN:
    raise ValueError("Отсутствует VK_DOMAIN")
if not all([DB_CONFIG['database'], DB_CONFIG['user'], DB_CONFIG['password']]):
    raise ValueError("Не указаны параметры подключения к БД")

# Параметры сбора
MAX_POSTS = 500  # Максимальное количество постов для сбора
BATCH_SIZE = 100  # Максимум за один запрос (ограничение VK API)

print(f"Начало сбора постов")

# Подключение к БД
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("Подключение к PostgreSQL установлено.")
except Exception as e:
    print(f"Ошибка подключения к БД: {e}")
    exit(1)

all_posts = []
offset = 0

# Сбор постов
while len(all_posts) < MAX_POSTS:
    print(f"Запрос постов: offset={offset}, всего собрано: {len(all_posts)}")

    url = 'https://api.vk.com/method/wall.get'
    params = {
        'access_token': VK_TOKEN,
        'v': '5.199',
        'domain': VK_DOMAIN,
        'count': min(BATCH_SIZE, MAX_POSTS - len(all_posts)),
        'offset': offset,
        'filter': 'owner'  # Не добавляются репосты
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Ошибка при запросе к VK API: {e}")
        break

    if 'error' in data:
        print(f"Ошибка VK API: {data['error']['error_msg']}")
        break

    posts = data['response']['items']
    if not posts:
        print("Больше постов нет.")
        break

    all_posts.extend(posts)
    offset += BATCH_SIZE

# Вставка в базу данных
inserted_count = 0
for post in all_posts:
    post_id = post['id']
    date_ts = post['date']
    post_date = datetime.fromtimestamp(date_ts)
    weekday = post_date.isoweekday()  # 1 = понедельник, ..., 7 = воскресенье
    likes = post.get('likes', {}).get('count', 0)
    text = post.get('text', '')[:10000]  # Ограничение длины текста

    if not text.strip():
        text = "[Текст отсутствует]"

    # Проверка на дубликат
    cur.execute("SELECT 1 FROM posts WHERE id_поста = %s", (post_id,))
    if cur.fetchone():
        continue

    cur.execute("""
        INSERT INTO posts (id_поста, дата_поста, день_недели, количество_лайков, текст_поста)
        VALUES (%s, %s, %s, %s, %s)
    """, (post_id, post_date, weekday, likes, text))

    inserted_count += 1

# Сохраняем изменения
conn.commit()
cur.close()
conn.close()

print(f"\nГотово!")
print(f"Всего получено постов: {len(all_posts)}")
print(f"Новых записей добавлено в БД: {inserted_count}")
