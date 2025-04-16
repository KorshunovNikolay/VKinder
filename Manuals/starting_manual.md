# Инструкция по запуску проекта

- Получить токен доступа ВКонтакте
    - [get_access_token.pdf](get_access_token.pdf)
- Получить токен группы ВКонтакте
    - [get_group_token.md](get_group_token.md)
- создать базу данных с помощью команды:
  ```  
  createdb -U postgres vkinder_db
  ```  
  ввести пароль пользователя postgres

- Создать в основном каталоге программы файл **.env**. Шаблон файла **.env**:
    ```
    # Токены без кавычек
    ACCESS_TOKEN=
    GROUP_TOKEN=
    
    # Доступ к БД. Пароль без кавычек
    LOGIN=postgres
    PASSWORD=
    DATABASE=vkinder_db
    SERVER_NAME=localhost
    SERVER_HOST=5432
    ```
- Установить необходимые пакеты с помощью команды:
  ```
  pip install -r requirements.txt
  ```
- Запустить файл **main.py**