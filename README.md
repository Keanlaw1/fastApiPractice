# Первое задание FastAPI 

Модели из Блогикума переписаны на SQLAlchemy. База данных SQLite

Есть категории, места, посты, комментарии и упрощенный пользователь. Для постов сделаны GET, POST, PUT и DELETE

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python create_db.py
python main.py
```

База создается пустой. Файл базы в репозиторий не входит.

## Как проверить API

Для начала сервер:
```powershell
python main.py
```

Откройте второй терминал и ниже по порядку

### 1. Создать пользователя

```powershell
$author = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/users/" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{"username":"student1"}'

$author
```
Появятся имя и номер пользователя. Ответ сохранен в $author
\
Если такой пользователь уже существует - нужно заменить student1 другим именем

### 2. Создать пост

```powershell
$body = @{
    title = "First post"
    text = "Hello"
    author_id = $author.id
} | ConvertTo-Json

$post = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/posts/" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$post
```

Появится созданный пост \
Номер автора берется из предыдущего ответа, номер поста сохраняется в $post\
Созданный пост должен быть в списке на http://127.0.0.1:8000/posts/

### 3. Изменить пост

```powershell
$body = @{
    title = "Updated post"
    text = "New text"
    author_id = $author.id
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/posts/$($post.id)/" `
    -Method Put `
    -ContentType "application/json" `
    -Body $body
```

В ответе будут новый заголовок и текст

### 4. Удалить пост

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/posts/$($post.id)/" `
    -Method Delete
```

Пост должен исчезнуть
