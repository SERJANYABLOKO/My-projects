# программа с двумя экранами
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView


# Экран (объект класса Screen) - это виджет типа "макет" (Screen - наследник класса RelativeLayout).
# ScreenManager - это особый виджет, который делает видимым один из прописанных в нём экранов.

class MainScr(Screen):
    def __init__(self, name='main'):
        super().__init__(name=name)  # имя экрана должно передаваться конструктору класса Screen

        btn_1 = Button(text="1")
        btn_2 = Button(text="2")
        btn_3 = Button(text="3")
        btn_4 = Button(text="4")

        text = Label(text='Выберите экран')

        h_1 = BoxLayout(orientation='horizontal')
        v_1 = BoxLayout(orientation='vertical', padding=8, spacing=8)

        btn_1.on_press = self.next
        btn_2.on_press = self.next_2
        btn_3.on_press = self.next_3
        btn_4.on_press = self.next_4
        h_1.add_widget(text)
        h_1.add_widget(v_1)
        v_1.add_widget(btn_1)
        v_1.add_widget(btn_2)
        v_1.add_widget(btn_3)
        v_1.add_widget(btn_4)


        self.add_widget(h_1)# экран - это виджет, на котором могут создаваться все другие (потомки)

    def next(self):
        self.manager.transition.direction = 'left'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'first'
    def next_2(self):
        self.manager.transition.direction = 'left'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'second'
    def next_3(self):
        self.manager.transition.direction = 'left'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'third'

    def next_4(self):
        self.manager.transition.direction = 'left'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'four'


class FirstScr(Screen):
    def __init__(self, name='first'):
        super().__init__(name=name)
        btn_1 = Button(text="Назад")
        btn_2 = Button(text="Выбор:1")
        air_1 = Label(text='')
        air_2 = Label(text='')

        v_1 = BoxLayout(orientation='vertical', padding=40)
        h_1 = BoxLayout(orientation='horizontal' )
        h_2 = BoxLayout(orientation='horizontal')

        v_1.add_widget(h_1)
        v_1.add_widget(h_2)

        h_1.add_widget(btn_2)
        h_1.add_widget(air_2)
        h_2.add_widget(air_1)
        h_2.add_widget(btn_1)

        btn_1.on_press = self.next
        self.add_widget(v_1)

    def next(self):
        self.manager.transition.direction = 'right'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'main'

class SecondScr(Screen):
    def __init__(self, name='second'):
        super().__init__(name=name)
        btn_1 = Button(text="Назад")
        btn_2 = Button(text="ОК")
        btn_3 = Label(text="Выбор:2")
        btn_4 = TextInput(hint_text='Введите пароль', size_hint=(4, 0.3))

        v_1 = BoxLayout(orientation='vertical', padding=8, spacing=8)
        h_1 = BoxLayout(orientation='horizontal', spacing=8)
        h_2 = BoxLayout(orientation='horizontal', spacing=8)

        v_1.add_widget(btn_3)

        v_1.add_widget(h_1)
        v_1.add_widget(h_2)

        h_1.add_widget(btn_4)
        h_2.add_widget(btn_2)
        h_2.add_widget(btn_1)

        btn_1.on_press = self.next
        self.add_widget(v_1)

    def next(self):
        self.manager.transition.direction = 'right'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'main'

class ThirdScr(Screen):
    def __init__(self, name='third'):
        super().__init__(name=name)
        btn = Button(text='Назад')
        image = AsyncImage(source='https://avatars.mds.yandex.net/i?id=dbebcfe5b29b6e2ae85dccda51572deb026aa15d-4668036-images-thumbs&n=13')

        v_1 = BoxLayout(orientation='vertical')

        v_1.add_widget(image)
        v_1.add_widget(btn)

        btn.on_press = self.next
        self.add_widget(v_1)

    def next(self):
        self.manager.transition.direction = 'right'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'main'


class FourScr(Screen):
    def __init__(self, name='four'):
        super().__init__(name=name)

        self.label = Label(text='Выбор 4' * 100, font_size='24sp', size_hint_y=10, halign='left', valign='top')
        btn = Button(text='назад')
        self.pols = ScrollView(size_hint = (1, 1))
        self.pols.add_widget(self.label)
        self.label.bind(size=self.resize)

        v_1 = BoxLayout(orientation='vertical')

        v_1.add_widget(self.pols)

        btn.on_press = self.next
        self.add_widget(v_1)

    def next(self):
        self.manager.transition.direction = 'right'  # объект класса Screen имеет свойство manager
        # - это ссылка на родителя
        self.manager.current = 'main'
    def resize(self):
        self.label.text_size = (self.label.width, None)
        self.label.texture_update()
        self.label.height = self.label.text_size[1]

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScr())
        sm.add_widget(FirstScr())
        sm.add_widget(SecondScr())
        sm.add_widget(ThirdScr())
        sm.add_widget(FourScr())
        # Будет показан FirstScr, потому что он добавлен первым. Это можно поменять вот так:
        # sm.current = 'second'
        return sm



app = MyApp()
app.run()