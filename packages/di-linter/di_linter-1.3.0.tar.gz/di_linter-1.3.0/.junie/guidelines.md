Этот проект статического анализатора кода на базе flake8.
Проверка инъекций зависимостей, код линтера в [linter_di.py](../linter_dependency_injection/linter_di.py)
Тестовые примеры в [project](/home/user/my/di-linter/example/project), 
конфиг [di.toml](/home/user/my/di-linter/example/di.toml)

Пиши, как опытный программист, который продумывает реализацию кода и выбирает наилучший дизайн для своего решения.
Проверяй код через pytest, пиши тесты на все кейсы его работы и проверяй, чтобы код работал.
Пиши код без комментариев.
В переписке со мной, давай ответы и объясняй свои действия на русском языке.

У меня установлен пакетный менеджер UV
Запускай проверку на моих примерах 
1. в CLI через команду "flake8 --select=DI /home/user/my/di-linter/example/project/packet/my_module.py"
2. в CLI через команду "di-linter /home/user/my/di-linter/example/project/packet"