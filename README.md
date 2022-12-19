# VK_screenshot_maker
Создание скрипта для автоматического снятия скриншотов из рекламных кабинетов ВК по условиям

##################################
<strong>ОБЩИЕ ДАННЫЕ РАБОТЫ ПРОГРАММЫ</strong>

##################################
Программа запускается через интерфейс. В рамках него доступно два активных поля для введения своих данных (логин / пароль). Введенные данные сохраняются на локальном диске пользователя в двоичном файле (в папке ~\VK Screenshots\settings) и не передаются во вне.
Также доступны две кнопки запуска алгоритмов программы:
  1. Кнопка "Клиенты" - Скрининг списка активных клиентов (у кого >100 показов за сегодня). Т.е. какие условия будут заданы пользователем в инетрфейсе для каждого клиента, чтобы снять необходимое количество скриншотов
  2. Кнопка "Старт" - Запуска основного функционала программы по снятию скриншотов, согласно заданным условиям в интерфейсе
 
В рамках интерфейса доступно еще одно активное поле - блок "Клиенты" (при первом запуске отсутсвует). В данном блоке добавляются условия снятия скриншотов через установку флажков для клиентов (галочки напротив имени клиента). По умолчанию флажки отсутсвуют. Наличие флажка у клиента означает, что алгоритм снимает ВСЕ активные креативы (>100 показов за сегодня) по всем РК (10 РК = ~45 креативов = ~45 скринов). Отсутсвие - снимает один креатив за одну РК (10 РК  - ~45 креативов = 10 скриншотов). Все примеры в скобках валидны при выполнении двух условий: эти клиенты / кампании / креативы крутятся сегодня и по ним не менее 100 показов за сегодня. Т.е. существует только два "вида" снятия скриншотов:
  1. Все скриншоты по клиенту, которые активны
  2. Только один скриншот по РК

ВАЖНО: Программа снимает только те креативы, где доступен "Предпросмотр" (кнопка в рамках интерфейса). К примеру, это недоступно для креативов "Сторис".

##################################
ПРИ ПЕРВОМ ЗАПУСКЕ
##################################
Программа запускает браузер "в режиме инкогнито" каждый раз. Это значит, что для входа в ВК необходимо ввести логин / пароль. По умолчанию в ВК в настройках включена двухфакторная аутентификация (подтверждение входа по паролю из СМС, как пример). Дабы каждый раз при входе в ВК не вводить этот пароль (муторно со временем), необходимо отключить двухфакторную аутентификацию (push со входом все также будет приходить на смартфон, если у вас установлено приложение, т.е. понимание, что кто-то, помимо вас, осуществил вход в ваш аккаунт, будет). Для отключения необходмио:
  1. Зайти в настройки аккаунта
  2. Перейти на вкладку "Безопасность"
  3. В строке "подтверждение входа" значение перевести в "Выкл"
  
После отключения рекомендовано установить сложный пароль для входа в аккаунт.

##################################
ИНСТРУКЦИЯ
##################################
1. Запускаем файл программы
2. Вводим в активные поля логин (пример: "89990005599") и пароль от своего аккаунта в ВК
3. Нажимаем кнопку "Клиенты" и дожидаемся окончания работы алгоритма. Об окончании оповестит информационная строка в интерфейсе
4. Выбираем (проставляем флажки) каким клиентам необходимо снять все креативы
5. Нажимаем кнопку "Старт" и дожидаемся окончания работы алгоритма. Об окончании оповестит информационная строка в интерфейсе
6. На рабочем столе появится / обновится папка VK Screenshots, откуда можно забрать полученные результаты

##################################
РЕЗУЛЬТАТ РАБОТЫ ПРОГРАММЫ
##################################
- Создание (при первом запуске) / обновление (при последующих) корневой папки на рабочем столе "VK Screenshots"
- Создание папок внутри корневой: ~VK Screenshots\*date\*client\*campaign\*creative - где:
	- *date - актуальная дата
	- *client - наименование клиента (согласно данным из кабинета ВК)
	- *campaign - наименование кампании (согласно данным из кабинета ВК)
	- *creative - наименование креатива (согласно данным из кабинета ВК)
	При наличии запрещенных символов в наименовании символы заменяются на "."
- Создание файла с текстовым результатом в папке: ~VK Screenshots\*date  - которая построена по древовидному принципу в виде словаря (ключ : ссылка). Список ключей:
	- клиент
	- кампания
	- креатив
	Наличие ключа на креатив в *txt файле указывает, что скриншот должен быть снят и сохранен в соответсвующей папке. Отсутствие ключа может говорить о внутренней ошибке (к примеру, ВК изменил тег на странице) или отсутствия возможности нацеливания (т.е.нет кнопки "Предпросмотр" на странице)
- Создание технической папки: ~VK Screenshots\settings  - где хранятся следующие данные:
	- clients - словарь активных клиентов (получен в результате работы кнопки "Клиенты")
	- clients_to_screen - словарь условий по клиентам (создан согласно проставленным флажкам пользователем в интерфейсе в блоке "клиенты")
	- logs - лог-файл с ошибками
	- to_log_in - двоичный файл с логином и паролем пользователя (!НЕ ПЕРЕДАВАТЬ!)

##################################
ВОЗМОЖНЫЕ ПРОБЛЕМЫ
##################################
- Программа работает только на Windows, поэтому функционировать на других ОС корректно не будет.
- В рамках алгоритма программы настроены TimeOut действий, т.е. если страница (а точнее нужный тег на странице) грузится >10 секунд, то скрипт работы прерывается. Поэтому при работе с очень слабым интернетом программа не будет функционировать
- Отсутствие скриншотов в папке: отсутствие кнопки "предпросмотр" или изменившийся тег на странице ВК
