import typing
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from bloom import Article
from bloom.publish import publish, Platform
from bloom.upload import upload

Action = typing.Callable[[], None]


@dataclass
class MenuItem:
    key: str
    description: str
    action: Action


class Menu(OrderedDict):

    def __init__(self, items: typing.List[MenuItem]):
        super().__init__()
        for item in items:
            self[item.key] = item

    def print(self):
        for item in self.values():
            print(f'{item.key}: {item.description}')

    def select(self):
        while True:
            key = input('> ')
            key = key.strip()
            if key in self:
                item = self[key]
                break
            print('输入错误，请重试')
        return item

    def action(self):
        self.print()
        item = self.select()
        item.action()


def none_action() -> None:
    print('do nothing')


def menu_action(menu: Menu) -> Action:
    return lambda: menu.action()


def upload_action() -> Action:
    def upload_it():
        article = Article.open(Path('.'))
        upload(article)
    return upload_it


def publish_action(platform: str) -> Action:
    def publish_it():
        article = Article.open(Path('.'))
        publish(article, platform)
    return publish_it


def publish_menu_items() -> typing.List[MenuItem]:
    i = 1
    res = []
    for platform in Platform:
        item = MenuItem(key=str(i),
                        description=f'[{platform.value}] {platform.description()}',
                        action=publish_action(platform.value))
        res.append(item)
        i += 1
    return res


publish_menu = Menu(publish_menu_items())


top_menu = Menu([
    MenuItem(key='1', description='upload', action=upload_action()),
    MenuItem(key='2', description='publish', action=menu_action(publish_menu)),
])


def interact(menu: Menu = None):
    if menu is None:
        menu = top_menu

    menu.action()
