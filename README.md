Для установки python зависимостей    
**pip install -r requirements.txt**    

скрипт копирует задачи из Azure в GitLab    
берет **ID** из листа **workitems.txt**    


Получить данные:    
**workitems.txt**    
запрос CLI (ниже) запишет в файл ID тэгнутых коммитов, текущего репозитория.     
**git log -E --grep=[#] | grep -oP '(?<=#)\d+' > workitems.txt**    
из-за особенностей цикла =) внутри скрипта, надо отредактировать файл и добавить в начало **пустую строку**.    
так же можно добавить ID задач по которым еще не было коммитов    

**userlist.csv**    
файл с пользователями    
ID из Gilab; логин Azure    
пример:    
9;KNovikova    

**gitlab_token**    
в вашем профиле GitLab    
**Edit profile > Access Tokens > заполнить и проставить галки > Create personal access token**    


**gitalab_project**    
можно увидеть на титульной странице нового проекта в GitLab    
(проект в котором будут созданы задачи)    


**gitlab_server**    
 можно спросить у DNS или администратора   
пример:    
"10.130.5.194"    

**azure_headers**  	- 	«Токен авторизации Azure»    
в вашем профиле Azure    
**Безопасность > Новый маркер > Полный доступ или Заполнить и проставить галки > Создать**    
`Предупреждение! Сделайте копию указанного выше маркера сейчас. Он не сохраняется, и у вас больше не будет возможности увидеть его.`    

К полученному токену, нужно добавить **“:”** (двоеточие) в начало и сконвертировать в **Base64**    
Полученный токен, добавить в скрипт    
было:    
**:cwivqkmz5a5ha5mzunasdfgstlq5isgrqcbfsyhhrkddfu555sq**    
стало после конвертации:    
**OjNqZmtpMnNxaG5ybmpiNDdvcTJrNWZ5NmtndGFscDdjZnB5anVrczVzM55yYXYzdnB5cnE=**   
    
[Base64 Encode and Decode - Online](https://www.base64encode.org/)    

Пример:    
```
gitalab_project = '10'
gitlab_server = "10.130.5.194"
gitlab_token = "mT3KrXT9ppaCc7yhJRGy" 


azure_headers = {
    'Authorization': 'Basic OjNqZmtpMnNxaG5ybmpiNDdvcTJrNWZ5NmtndGFscDdjZnB5anVrczVzM55yYXYzdnB5cnE='
    }
```

