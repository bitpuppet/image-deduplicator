from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooser
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout

import math
from queue import Queue

from file_finder import ImageFinder
from image_hasher import ImageHasher

INDIR = "C:\\Users\\eulhaque\\Desktop\\Python\\image-deduplicator\\input\\"
OUTDIR = "C:\\Users\\eulhaque\\Desktop\\Python\\image-deduplicator\\output\\"

class MainScreen1(BoxLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.first = BoxLayout(orientantion='horizontal')
        self.add_widget(Label(text="Choose Dir"))

        self._indir = TextInput(multiline=False)
        self._indir.text = INDIR
        self.first.add_widget(self._indir)

        self._outdir = TextInput(multiline=False)
        self._outdir.text = OUTDIR
        self.first.add_widget(self._outdir)

        self.add_widget(self.first)

class GridMainScreen(GridLayout):

    def __init__(self, **kwargs):
        super(GridMainScreen, self).__init__(**kwargs)

        self.cols = 2
        self.add_widget(Label(text="Choose Dir"))

        self._indir = TextInput(multiline=False)
        self._indir.text = INDIR
        self.add_widget(self._indir)

        self._outdir = TextInput(multiline=False)
        self._outdir.text = OUTDIR
        self.add_widget(self._outdir)

class MainScreen(object):

    def __init__(self):

        self.root = BoxLayout(orientation='vertical')
        self._infiles  = []
        self._outfiles = []

        #row 1
        self.input_row = BoxLayout(orientation='horizontal')
        self.input_row.add_widget(Label(text='Choose Dir'))

        self._indir = TextInput()
        self._indir.text = INDIR
        self.input_row.add_widget(self._indir)

        self._outdir = TextInput()
        self._outdir.text = OUTDIR
        self.input_row.add_widget(self._outdir)

        self.load_button = Button(text='Load Files')
        self.load_button.on_press = self.load_files
        self.input_row.add_widget(self.load_button)

        #row 2
        self.start_row = BoxLayout(orientation='horizontal')
        self.info_label = Label(text='Total number of Files Selected: 0')
        self.start_button = Button(text='Start De-Duplicating')
        self.start_button.on_press = self.start_deduplicating
        self.start_row.add_widget(self.info_label)
        self.start_row.add_widget(self.start_button)

        #row 3
        self.pb_row = BoxLayout(orientation='horizontal')
        self.pb = ProgressBar(max=100)
        self.pb_row.add_widget(self.pb)

        #row 4
        self.images_row = GridLayout()
        self.images_row.cols = 3

        self.root.add_widget(self.input_row)
        self.root.add_widget(self.start_row)
        self.root.add_widget(self.pb_row)
        self.root.add_widget(self.images_row)

        self.outbox = Queue()

    def load_files(self):
        print(self._indir.text)
        self._infiles = list(ImageFinder.ifind(self._indir.text))
        self.info_label.text = "Total Files Found to load: " + str(len(self._infiles))
        self.pb.max = len(self._infiles)

    def update_progress(self):
        self.pb.value = self.outbox.qsize()
        print("Progress: ", self.pb.value)

    def done_progress(self):
        self.pb.value = self.pb.max
        print("Completed. Qsize: ",self.outbox.qsize())
        print(self.outbox.get_nowait())
        similar_images = ImageHasher.group_by_similar_images(self.outbox)

        scrollView = RecycleView()
        rv = RecycleBoxLayout()
        for img_path in similar_images:
            print("Adding to rv: "+ img_path)
            #button = Button()
            #button.text = "Image: " + img_path
            img = Image(source=img_path)
            #button.add_widget(img)
            rv.add_widget(img)
        
        scrollView.add_widget(rv)
        self.images_row.add_widget(scrollView)
        return
        image_per_row = 2
        rows_count = math.floor(len(self._infiles) / image_per_row)
        for row in range(rows_count):
            for c in range(image_per_row):
                img_path = self._infiles[c*row]
                img = Image(source=img_path)
                print(self._infiles[c*row])
                self.images_row.add_widget(img)

    def start_deduplicating(self):

        hasher = ImageHasher(self._indir.text, self.outbox, progress_callback=self.update_progress, done_callback=self.done_progress)
        hasher.start()

    def build(self):
        return self.root

class KivyApp(App):

    def build(self):

        return MainScreen().build()
        superBox        = BoxLayout(orientation='vertical')
        horizontalBox   = BoxLayout(orientation='horizontal')
        button1         = Button(text="One")
        button2         = Button(text="Two")

        horizontalBox.add_widget(button1)
        horizontalBox.add_widget(button2)

        verticalBox     = BoxLayout(orientation='vertical')
        button3         = Button(text="Three")
        button4         = Button(text="Four")

        verticalBox.add_widget(button3)
        verticalBox.add_widget(button4)
        superBox.add_widget(horizontalBox)
        superBox.add_widget(verticalBox)

        return superBox

        return MainScreen() #Label(text="Hello World")


if __name__ == '__main__':
    KivyApp().run()
