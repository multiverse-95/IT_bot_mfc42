## IT Bot mfc 42
### Описание бота
Проект «бот-айтишник» представляет собой бота для мессенджера телеграмм. Бот-айтишник способен будет ответить по вопросам 
АИС, ПК ПВД, 1С, Очередь.  Также бот-айтишник поможет по вопросам принтеров: бот спрашивает проблему
с принтером, модель принтера и отдел. Далее полученная информация будет отсылаться в IT-отдел.
### Цель
Упрощение работы сотрудникам IT-отдела МФЦ.
### Актуальность бота
1. Некоторые вопросы по АИС, ПК ПВД, 1С часто бывают однотипными – неправильно заполнили формы, прикрепили слишком большой файл и т.д. Ответы на такие вопросы можно автоматизировать, если мы заранее знаем коды ошибок. Зная коды ошибок, мы укажем боту эти ошибки и решения к ним. После чего, бот может автоматически подключаться к АИС и по номеру заявления находить ошибку. В итоге бот ответит человеку, как решить его проблему.
2. Проблемы с принтером. Рано или поздно в отделах случаются проблемы с принтером (закончился тонер, не печатает и т.д). В таком случае, с отделов звонят к IT-специалистам. Это часто отнимает время. Бот может помочь упростить эту задачу. Бот будет опрашивать сотрудника по его вопросам с принтером. В итоге, полученная информация автоматически отправляется в телеграмм группу IT-отдела.
### Команды бота
#### 1. Команда /start
Для того чтобы начать работу с ботом, необходимо его добавить к себе в телеграмм. Далее необходимо
написать команду /start
#### Скриншот - Команда /start
![Alt text](/screenshots/start.PNG "Скриншот - Команда /start")
#### 2. Команда /help
Команда /help отвечает за помощь пользователю (выводит доступные команды)
#### Скриншот - Команда /help
![Alt text](/screenshots/help.PNG "Скриншот - Команда /help")
#### 3. Команда /ais
Команда /ais отвечает за помощь по АИС. После отправки команды, бот нам предлагает два варианта:
"Проблемы с АИС" и "Проблемы с заявлением в АИС".
При ошибке с обращением необходимо ввести номер обращения. После чего бот проверит обращение и выдаст результат.
#### Скриншот - Команда /ais
![Alt text](/screenshots/ais_start.PNG "Скриншот - Команда /ais")
#### Скриншот - проблема с документом в аис
![Alt text](/screenshots/ais_doc_problem.PNG "Скриншот - проблема с документом в аис")
#### Скриншот - проблема с заявлением в аис
![Alt text](/screenshots/ais_request_problem.PNG "Скриншот - проблема с заявлением в аис")
#### 4. Команда /pkpvd
Команда /pkpvd отвечает за помощь по ПК ПВД. После отправки команды, бот нам предлагает два варианта:
"Не работает или зависает ПК ПВД", "Ошибка в обращении".
При ошибке с обращением необходимо ввести номер обращения. После чего бот проверит обращение и выдаст результат.
#### Скриншот - Команда /pkpvd
![Alt text](/screenshots/pkpvd.PNG "Скриншот - Команда /pkpvd")
#### Скриншот - Не работает или зависает ПК ПВД
![Alt text](/screenshots/pkpvd_appeal_problem.PNG "Скриншот - Не работает или зависает ПК ПВД")
#### Скриншот - Ошибка в обращении
![Alt text](/screenshots/pkpvd_appeal_problem2.PNG "Скриншот - Ошибка в обращении")
#### 5. Команда /1c
Команда /1c отвечает за помощь по 1с. После отправки команды, бот нам предлагает два варианта:
"Не работает/завис 1С", "Другая проблема с 1С"
#### Скриншот - Команда /1c
![Alt text](/screenshots/buh_1c.PNG "Скриншот - Команда /1c")
#### 6. Команда /queue
Команда /queue отвечает за помощь по очереди. После отправки команды, бот нам предлагает варианты:
"Завис талон", "Завис терминал", "Завис монитор", "Зависли кнопки", "Другая проблема с очередью".
#### Скриншот - Команда /queue
![Alt text](/screenshots/queue.PNG "Скриншот - Команда /queue")
#### 7. Команда /printer 
Команда /printer отвечает за помощь по принтеру. После отправки команды, бот нам предлагает варианты:
"картридж закончился", "плохо печатает", "не печатает", "другая проблема".
#### Скриншот - Команда /printer
![Alt text](/screenshots/printer_start.PNG "Скриншот - Команда /printer")
#### Скриншот - информация о заявке с принтером
![Alt text](/screenshots/printer_all_info.PNG "Скриншот - информация о заявке с принтером")
#### Скриншот - информация переслана в группу IT
![Alt text](/screenshots/group_info.PNG "Скриншот - информация переслана в группу IT")
#### 8. Команда /cancel 
Когда бот нас опрашивает и мы дали не тот вариант ответа, мы можем отменить действие и начать заново.
Для этого нужно написать команду /cancel.
#### Скриншот - Команда /cancel:
![Alt text](/screenshots/cancel.PNG "Скриншот - Команда /cancel")

Также бот реагирует на регулярные выражения. Вы можете просто боту написать: "1с завис" или "пк пвд", 
или "тонер кончился". Бот среагирует на текст и предложит вариант.
### P.S.
Структура бота взята с этого репозитория: https://github.com/MasterGroosha/telegram-tutorial-2/tree/master/code/04_fsm