pszi-ab-emperor
=================
Агент Безопасности ПСЗИ 


Usage
--------
Необходимо добавить папку, в которой будет лежать файл ab_demon.py в initd 
конфигурационный файл должен быть расположен в '/etc/pszi_ab_emperor/ab_emperor.conf'
файл ab_demon.py умеет обрабатывать 3 команды: start, stop, restart


Requirements
-------------
    python_sz_daemon 
    rabbit_tools
    
    
Required settings 
---------------------

необходимые параметры в конфигурационном файле

    pid_file_path - путь до пид файла
    log_name - название лога
    sqllite3_db_path - путь до файла и файл SQLite
    log_files_dir - директория для лог файлов
    job_json_conf_path - путь до файла со схемой задач (пример файла в share/handle_scheme.json)
    date_format - формат даты и времени
    socket_path - адрес Linux сокета