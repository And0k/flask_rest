Системные технологии | Тестовое задание Python

Создать сервис, который будет принимать цветные изображения через REST POST,
переводить их в черно-белый цвет, складывать их папку на диске и отдавать через GET.
Сервис обернуть в докер контейнер.

Сервис получает через REST POST пакет завёрнутых в JSON ссылок(url) на изображения и параметр для отсечения уровня черный/белый для каждого изображения.
В ответ сервис отдаёт идентификатор результатов работы(guid).

В ответ на GET с параметром идентификатора результатов работы сервис отдаёт сами изображения.
