# импорт модулей и их компонентов
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import PySimpleGUI as sg
import matplotlib
import matplotlib.pyplot as plt
from numpy import *
matplotlib.use('TkAgg')

# Добавим холст - пустую рабочую область. Canvas позволяет разместить на себе картинку, видео, текст или любой другой объект.
# Диаграммы Matplotlib по умолчанию имеют панель инструментов (тулбар) внизу. 
# Однако нам требуется, чтобы панель навигации была встроена в холст отдельно. Сделаем это с помощью класса NavigationToolbar2Tk.
class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

sg.theme('SystemDefault1')

# размер полотна по умолчанию
xmin, xmax, ymin, ymax = plt.axis([-10, 10, -10, 10])
plt.grid()
x = linspace(-100, 100, 1000001)
xxxMINxxx, xxxMAXxxx = -1000, 1000
figure_x, figure_y, figure_w, figure_h = plt.gcf().bbox.bounds

# Добавим кнопки в боковой панели. 
graphics_column = [[]]
for i in range(100):
    i_layout = [[sg.InputText(key=f'input_text{i}', visible=False, enable_events=True),
      sg.Button(key=f'button{i}', enable_events=True, button_color=('red', 'red')),
      sg.ColorChooserButton('', key=f'color_choos{i}', button_color=('green', 'green'), target=f'input_text{i}'),
      sg.Checkbox('f(x) =', key=f'checkbox{i}', default=True, enable_events=True,background_color='#F0F0F0')]]
    graphics_column[0].append(sg.Column(i_layout, key=f'column{i}', visible=False))

# колонна (список функций и  настройки масштаба)
column1 = [[sg.Text('Графики:')],
           [sg.Column(graphics_column, size=(180, figure_h - 160), scrollable=True, vertical_scroll_only=True)],
           [sg.Text('Элементы управления')],
           [sg.InputText('-10.0', size=(8, 1), key='xmin'), sg.Text('<  x  <'), sg.InputText('10.0', size=(8, 1), key='xmax')],
           [sg.InputText('-10.0', size=(8, 1), key='ymin'), sg.Text('<  y  <'), sg.InputText('10.0', size=(8, 1), key='ymax')],
           [sg.Button('Применить настройки', enable_events=True, key='settings')]]

# Строка для ввода функции
layout = [[sg.Canvas(size=(figure_w, figure_h), key='canvas'),
           sg.Column(column1, size=(200, figure_h))],
          [sg.Text('f(x)  ='),
           sg.InputText(size=(38, 1), key='new_gr'),
           sg.Button('Добавить график', enable_events=True, key='add_graph'),
           sg.Canvas(key='controls')]]

# Выведем график на экран
window = sg.Window('Graphics', layout, finalize=True)
draw_figure_w_toolbar(window['canvas'].TKCanvas, plt.gcf(), window['controls'].TKCanvas)

current_graphics = []
other_graphics = list(range(100, -1, -1))
graphics_data = {}


while True:
    event, values = window.read()
    i = other_graphics.pop()

    # кнопка добавления графика
    if event == 'add_graph':
        window.Element(f'checkbox{i}').update(text='f(x) = ' + values['new_gr'])
        window.Element(f'column{i}').update(visible=True)
        with errstate(divide='ignore', invalid='ignore'):
            fig, = plt.plot(x, eval(values['new_gr'].replace('^', '**')), color='#0000FF')
            plt.draw()      
        graphics_data[i] = [fig, values['new_gr'].replace('^', '**'), '#0000FF']
        current_graphics.append(i)
        i = other_graphics.pop()

    # настройки масштаба
    if event == 'settings':
        xmin = float(values['xmin'])
        xmax = float(values['xmax'])
        ymin = float(values['ymin'])
        ymax = float(values['ymax'])
        xmin, xmax = plt.xlim(xmin, xmax)
        ymin, ymax = plt.ylim(ymin, ymax)
        plt.draw()

    # чекбокс отображения графика
    if 'checkbox' in event:
        a = int(event.split('checkbox')[-1])
        if values[event]:
            graphics_data[a][0], = plt.plot(x, eval(graphics_data[a][1]), color=graphics_data[a][2])
        else:
            graphics_data[a][0].remove()
        plt.draw()

    # кнопка изменения цвета
    if 'input_text' in event and values[event] != 'None':
        a = int(event.split('input_text')[-1])
        graphics_data[a][2] = values[event]
        plt.setp(graphics_data[a][0], color=graphics_data[a][2])
        plt.draw()
        window.Element(f'checkbox{a}').update(background_color=graphics_data[a][2])

    # кнопка удаления графика
    if 'button' in event:
        a = int(event.split('button')[-1])
        graphics_data[a][0].remove()
        current_graphics.remove(a)
        other_graphics.append(a)
        del graphics_data[a]
        window[f'column{a}'].update(visible=False)
        plt.draw()
window.close()
