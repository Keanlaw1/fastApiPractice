# 2-й семестр FastApi

## Что сделано по заданиям

- **Задание 1 — FastAPI** <br>
Модели из Блогикума переписаны на SQLAlchemy. База данных SQLite
Есть категории, места, посты, комментарии и упрощенный пользователь. Для постов сделаны GET, POST, PUT и DELETE

- **Задание 2 — PostgreSQL** <br>
Подключил PostgreSQL вместо SQLite. Вынес запросы к базе в repositories.py и добавил функции для всех пяти моделей

- **Задание 3 — Alembic** <br>
Сгенерировал первую миграцию и проверил, что она создаёт все таблицы в пустой базе PostgreSQL

- **Задание 4 — Обработка ошибок** <br>
Возвращается:<br>
`409` -- если имя пользователя занято<br>
`404` -- если пост или автор не найден<br>
`422` -- если данные запроса не прошли проверку

## Запуск

Нужен PostgreSQL. Внутри создать в pgAdmin пустую базу blogicum_alembic <br>
Приложение подключается к ней на порту 5432 под пользователем postgres
<br>
ДалееЖ
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:POSTGRES_DB = "blogicum_alembic"
$env:POSTGRES_PASSWORD = (Get-Credential -UserName postgres -Message "Пароль PostgreSQL").GetNetworkCredential().Password
python -m alembic upgrade head
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

## Как проверить API

Оставим сервер запущенным. Во втором терминале и выполним запросы ниже по порядку

### 1. Создать пользователя

```powershell
$api = "http://127.0.0.1:8001"
$author = Invoke-RestMethod -Method Post -Uri "$api/users/" -ContentType "application/json" -Body '{"username":"student1"}'
$author
```
Ответ будет имя и id пользователя <br>
Если такой пользователь уже существует - нужно заменить student1 другим именем

### 2. Создать пост

```powershell
$post = curl.exe -sS "$api/posts/" `
    -F "title=First post" `
    -F "text=Hello" `
    -F "author_id=$($author.id)" `
    -F "image=@C:\path\photo.jpg" | ConvertFrom-Json

$post
Invoke-RestMethod -Method Get -Uri "$api/posts/"
```

Появится созданный пост \
Номер автора берется из предыдущего ответа, номер поста сохраняется в $post\
Созданный пост должен быть в списке на http://127.0.0.1:8001/posts/

### 3. Изменить пост

```powershell
$body = @{title = "Updated post"; text = "New text"; author_id = $author.id} | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "$api/posts/$($post.id)/" -ContentType "application/json" -Body $body
```

В ответе будут новый заголовок и текст

### 4. Удалить пост

```powershell
Invoke-RestMethod -Method Delete -Uri "$api/posts/$($post.id)/"
```

Пост должен исчезнуть

## Как проверить API иначе

Запустите сервер и откройте [Swagger](http://127.0.0.1:8001/docs)<br>
Для каждого запроса раскройте нужную строку, нажмите Try it out, заполните поля и нажмите Execute

1. **POST /users/ --- создать пользователя**<br>
Вставьте {"username": "student1"} и запомните id из ответа. Если такое имя уже есть, возьмите другое.


2. **POST /posts/ --- создайть пост**<br>
Заполните поля title, text, в author_id укажите id пользователя из первого шага<br>
В поле image выберите фото JPEG или PNG до 5 Mb<br>
Запомните id созданного поста. По ссылке image_url из ответа можно открыть фото


3. **GET /posts/ --- открыть список постов**<br>
После создания поста в общем списке можно увидеть пост


4. **PUT /posts/{post_id}/ --- изменить пост**<br>
Укажите id поста и отправьте {"title": "Новый заголовок", "text": "Новый текст", "author_id": 1}. В author_id снова укажите id своего пользователя


5. **POST /posts/{post_id}/comments/ --- добавить комментарий**<br>
Укажите id поста и отправьте {"text": "Классное фото!", "author_id": 1}<br>
Вместо 1 подставьте id пользователя


6. **GET /posts/{post_id}/comments/ --- открыть комментарии**<br>
Укажите тот же id поста. В списке должен появиться ваш комментарий.


7. **POST /posts/{post_id}/likes/ --- поставить лайк**<br>
Укажите id поста и отправьте {"user_id": 1}<br>
Вместо 1 подставьте id пользователя. Если отправить тот же запрос ещё раз, сервер вернёт `409`


8. **GET /posts/{post_id}/likes/ --- проверить количество лайков**<br>
Укажите id поста. В ответе будет число лайков в поле count


9. **DELETE /posts/{post_id}/likes/{user_id}/ --- убрать лайк**<br>
Укажите id поста и id пользователя. Снова проверьте количество лайков и оно будет меньше на один


10. **DELETE /posts/{post_id}/ --- удалить пост**<br>
Укажите тот же id поста. В GET /posts/ можно увидеть что поста больше нет...