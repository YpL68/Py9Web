def higher_order(func):
    print('Получена функция {} в качестве аргумента'.format(func))
    func()
    return func


def hello_world():
    print('Hello world!')


def decorator_function(func):
    def wrapper():
        print('Функция-обёртка!')
        print('Оборачиваемая функция: {}'.format(func))
        print('Выполняем обёрнутую функцию...')
        func()
        print('Выходим из обёртки')
    return wrapper


main_function = decorator_function(hello_world)

main_function()
