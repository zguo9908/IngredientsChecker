from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import time
import os
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from nltk.metrics.distance import edit_distance
import math
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pytesseract

try:
    from PIL import Image
except ImportError:
    import Image


Builder.load_string('''
<StartScreen>:
    GridLayout:
        cols: 1
        size: root.width, root.height

        Button:
            text: 'Camera'
            font_size: 48
            on_press: root.manager.current = 'camera'
            background_normal: 'white.png'
            background_down: 'gray.png'
            background_color: 0, .6, .8, 1
        Button:
            text: 'Upload'
            font_size: 48
            on_press: root.manager.current = 'upload'
            background_normal: 'white.png'
            background_down: 'gray.png'
            background_color: 0, .8, .4, 1
<CameraScreen>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: True
    Button:
        text: 'Capture Image'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
        background_normal: 'white.png'
        background_down: 'gray.png'
        background_color: .094, .77, .71, 1
<UploadScreen>:
    GridLayout:
        cols: 1
        FileChooserIconView: 
            id: filechooser
            path: root.get_path()
            canvas.before: 
                Color: 
                    rgb: 0, .41, .55
                Rectangle: 
                    pos: self.pos 
                    size: self.size 
            on_selection: root.select(*args)
<ResultScreen>:
    GridLayout:
        cols: 1
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        GridLayout:
            size_hint_y: None
            height: self.minimum_height
            cols: 2
            Button:
                text: 'Ingredients'
                background_normal: 'white.png'
                background_down: 'gray.png'
                background_color: 0, .6, .8, 1
                size_hint_y: None
                height: 100
                on_press: root.manager.current = 'ingredients'
            Button:
                text: 'Start Over'
                background_normal: 'white.png'
                background_down: 'gray.png'
                background_color: 0, .6, .8, 1
                size_hint_y: None
                height: 100
                on_press: root.manager.current = 'start'
        Label:
            name: 'results'
            text: "Results"
            color: 0, 0, 0, 1
            font_size: 48
            size_hint_y: None
            height: 100
            background_color: .5, .5, .5, 1
        Image:
            id: results_im
            allow_stretch: True
<IngredientsScreen>
    ScrollView:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        GridLayout:
            size_hint_y: None
            height: self.minimum_height
            cols: 1
            GridLayout:
                size_hint_y: None
                height: self.minimum_height
                cols: 2
                Button:
                    text: 'Results'
                    background_normal: 'white.png'
                    background_down: 'gray.png'
                    background_color: 0, .6, .8, 1
                    size_hint_y: None
                    height: 100
                    on_press: root.manager.current = 'result'
                Button:
                    text: 'Start Over'
                    background_normal: 'white.png'
                    background_down: 'gray.png'
                    background_color: 0, .6, .8, 1
                    size_hint_y: None
                    height: 100
                    on_press: root.manager.current = 'start'
            Label:
                text: 'Ingredients'
                font_size: 48
                color: 0, 0, 0, 1
                size_hint_y: None
                height: 100
            Label:
                text: 'High Risk'
                font_size: 36
                color: 0, 0, 0, 1
                size_hint: None, None
                width: self.texture_size[0] + dp(20)
                height: self.texture_size[1] + dp(10)
            Label:
                id: high
                color: .8, .07, 0, 1
                size_hint: None, None
                width: self.texture_size[0] + dp(20)
                height: self.texture_size[1] + dp(10)
            Label:
                text: 'Medium Risk'
                font_size: 36
                color: 0, 0, 0, 1
                size_hint: None, None
                width: self.texture_size[0] + dp(20)
                height: self.texture_size[1] + dp(10)
            Label:
                id: med
                color: .8, .47, .13, 1
                size_hint: None, None
                width: self.texture_size[0] + dp(20)
                height: self.texture_size[1] + dp(10)
            Label:
                text: 'Low Risk'
                font_size: 36
                color: 0, 0, 0, 1
                size_hint: None, None
                width: self.texture_size[0] + dp(20)
                height: self.texture_size[1] + dp(10)
            Label:
                id: low
                color: 0, .55, .27, 1
                size_hint: None, None
                width: self.texture_size[0] + dp(20)
                height: self.texture_size[1] + dp(10)
''')

def get_ingredients_list():
    ingredients_list = {}
    for i in range(1, 47):
        url = "https://cosmily.com/ingredients?page="+str(i)
        x = urlopen(url)
        data = x.read()
        soup = BeautifulSoup(data, 'html.parser')
        outer = soup.find_all("tr")
        for o in outer:
            soup_inner = BeautifulSoup(str(o), 'html.parser')
            link = soup_inner.find("a")
            rating = soup_inner.find_all("td")
            for r in rating:
                try:
                    int(r.text)
                    rating = r
                    break
                except ValueError:
                    pass
            if link is not None and link.text != '' and rating.text != '':
                print(link.text + ': ' + rating.text)
                ingredients_list[link.text.upper()] = int(rating.text)
    return ingredients_list


def spell_fix(word, db):
    try:
        if db[word]:
            return word
    except KeyError:
        pass

    smallest_chem = ''
    smallest_ed = math.inf
    for chem in db.keys():
        curr_ed = edit_distance(word, chem)
        if curr_ed < smallest_ed:
            smallest_chem = chem
            smallest_ed = curr_ed
    return smallest_chem


def get_hazard_levels(chems, db):
    hazard_levels = []
    for c in chems:
        hazard_levels.append(db[c])
    return hazard_levels


def get_db_subset(key_subset, db):
    db_subset = {}
    for k in key_subset:
        db_subset[k] = db[k]
    return db_subset


def store_database(db, db_filename):
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    cur.execute('CREATE TABLE chemicals (name VARCHAR, rating TINYINT, PRIMARY KEY (name))')
    for chem in db.keys():
        cur.execute('INSERT INTO chemicals (name, rating) VALUES (?, ?)', (chem, db[chem]))
    conn.commit()
    conn.commit()
    conn.close()


def load_database(db_filename):
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    cur.execute('SELECT * FROM chemicals')
    data = cur.fetchall()
    db = {}
    for chem, rating in data:
        db[chem] = rating
    return db


def process_image(image_name, db):
    print("RAW:")
    ingredients_raw = pytesseract.image_to_string(image_name)
    print(ingredients_raw)
    ingredients = re.split(r"[,:]+", ingredients_raw)
    ingredients = [spell_fix(elt.upper().replace('\n', ' ').strip(), db) for elt in ingredients
                   if len(elt) > 0 and elt.lower() != 'ingredients']
    print("PROCESSED:")
    print(ingredients)
    return ingredients


def create_plot(ewg_list):
    # read in ewg scores
    ewg = np.array(ewg_list)
    rating = np.chararray(len(ewg_list))
    pie = np.zeros(3)
    # convert ewg scores to low/medium/high
    for i in range(0, len(ewg_list)):
        if ewg[i] <= 2:
            rating[i] = "low"
            pie[0] += 1
        elif ewg[i] <= 6:
            rating[i] = "medium"
            pie[1] += 1
        else:
            rating[i] = "high"
            pie[2] += 1

    # Data to plot
    labels = 'Low Hazard', 'Medium Hazard', 'High Hazard'
    colors = ['gold', 'lightcoral', 'lightskyblue']
    # ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0, 0, 0)  # explode 1st slice
    # Plot
    plt.pie(pie, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    from io import BytesIO
    plt.savefig('results.png')


class StartScreen(Screen):
    pass


class CameraScreen(Screen):
    def capture(self):
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = 'IMG_{}.png'.format(timestr)
        camera.export_to_png(filename)
        process_image(filename, DATABASE)
        self.manager.current = 'result'


class UploadScreen(Screen):
    def get_path(self):
        return os.getcwd()

    def select(self, *args):
        self.manager.current = 'result'
        try:
            fc = self.ids['filechooser']
            ingredients = process_image(args[1][0], DATABASE)
            hazard_levels = get_hazard_levels(ingredients, DATABASE)
            create_plot(hazard_levels)
            self.manager.get_screen('result').load_result(get_db_subset(ingredients, DATABASE))
            self.manager.get_screen('ingredients').load_ingredients(get_db_subset(ingredients, DATABASE))
            path = fc.selection[0]
            fc.selection.remove(path)
        except IndexError:
            pass

class ResultScreen(Screen):
    def test(self):
        print(self)
        print(self.parent)

    def load_result(self, db_subset):
        results_im = self.ids['results_im']
        results_im.source = 'results.png'


class IngredientsScreen(Screen):
    def load_ingredients(self, db_subset):
        high = ''
        med = ''
        low = ''
        for chem in db_subset.keys():
            ewg_level = db_subset[chem]
            if ewg_level > 6:
                high += chem + ': ' + str(ewg_level) + '\n'
            elif ewg_level > 2:
                med += chem + ': ' + str(ewg_level) + '\n'
            else:
                low += chem + ': ' + str(ewg_level) + '\n'
        high_label = self.ids['high']
        med_label = self.ids['med']
        low_label = self.ids['low']
        high_label.text = high
        med_label.text = med
        low_label.text = low


DATABASE = load_database('chemicals_db.sqlite')
sm = ScreenManager()
sm.add_widget(StartScreen(name='start'))
sm.add_widget(CameraScreen(name='camera'))
sm.add_widget(UploadScreen(name='upload'))
sm.add_widget(ResultScreen(name='result'))
sm.add_widget(IngredientsScreen(name='ingredients'))


class IngredientsCheckerApp(App):
    def build(self):
        return sm

if __name__ == "__main__":
    IngredientsCheckerApp().run()
