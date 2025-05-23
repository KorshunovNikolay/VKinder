# Командный проект по курсу «Профессиональная работа с Python»: VKinder

## _Общее описание_
Программа реализует функционал VK-бота для поиска кандидатов, подходящих для знакомства, и оценки их пользователем ВК. 
Бот взаимодействует с пользователем через личные сообщения в ВКонтакте, предоставляя интерфейс для просмотра профилей кандидатов и управления списком избранных.

## _Основные компоненты_
В работе программы участвуют пять основных модулей:
1. **_main_** - реализует запуск и внешний функционал VK-бота с помощью класса **VkBotServer**
2. **_vk_** - реализует взаимодействие VK-бота с VK API с помощью класса **VkBotApi**
3. **_models_** - описывает модели для создаваемой базы данных с использованием **SQLAlchemy**
4. **_database_** - реализует функционал для взаимодействия с базой данных с помощью класса **VkBotDatabase**
5. **_keyboards_** - содержит набор клавиатур для VK-бота

## _Логика работы бота_
- При первом обращении пользователя бот заполняет базу данных подходящими кандидатами (занимает некоторое время). 

Схема БД:
![database scheme](database_scheme.png)

- Кандидаты подбираются на основе информации, указанной в профиле пользователя. Критерии поиска кандидатов:
  - **_пол_** - противоположный полу пользователя;
  - **_возраст_** - возраст пользователя ± 5 лет (если пользователь указал свою дату рождения). Минимальный возраст кандидата - 18 лет, максимальный - 99 лет;
  - **_город_** - учитывается, если пользователь указал его в своем профиле.

- Кандидат для показа пользователю выбирается случайным образом из "неотмеченных", т.е. не добавленных ни в черный список, ни в избранные.

- Далее бот выводит в чат с пользователем информацию о кандидате в формате:
    ```
    - три фотографии (определяются количеством лайков),
    - имя и фамилия,
    - ссылка на профиль.
    ```

## _Особенности_
- Бот поддерживает следующие команды:
  ```
  start - начинает работу с ботом, собирает базу кандидатов
  next/continue - показывает следующего кандидата
  ❤ - добавляет кандидата в избранное
  👎 - добавляет кандидата в черный список
  ⭐ - выводит список избранных кандидатов
  ```
- Все события логируются в файл db_log.log в формате:
  ```
  YYYY-MM-DD HH:MM:SS - LEVEL – MESSAGE
  ```
- Бот включает базовую обработку ошибок при:
  - отправке сообщений
  - загрузке фотографий
  - работе с базой данных

## _Требования_
Все необходимые зависимости и их версии указаны в файле _requirements.txt_

Для работы с VK API необходим токен доступа ВКонтакте - **ACCESS_TOKEN**

Для работы с VK Сообществом необходим токен группы ВКонтакте - **GROUP_TOKEN**

Все необходимые инструкции по получению токенов и запуску проекта находятся в папке **_Manuals_**

### Участники проекта:
- Николай Коршунов https://github.com/KorshunovNikolay
- Ника Слесарева https://github.com/Lampropeltiss
- Андрей Доценко https://github.com/addozenko

