from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlFile
from pyforms.controls   import ControlText
from pyforms.controls   import ControlSlider
from pyforms.controls   import ControlPlayer
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlLabel
from pyforms.controls   import ControlProgress
from pyforms.controls   import ControlTableView
from pyforms.controls   import ControlImage
from pyforms import controls
import cv2

import math
from queue import Queue

from file_finder import ImageFinder
from image_hasher import ImageHasher

class ImageDeDuplicatorApp(BaseWidget):

    INDIR = "C:\\Users\\eulhaque\\Desktop\\Python\\image-deduplicator\\input\\"
    OUTDIR = "C:\\Users\\eulhaque\\Desktop\\Python\\image-deduplicator\\output\\"

    def __init__(self, *args, **kwargs):
        super().__init__('Computer vision algorithm example')

        self.set_margin(10)

        #Definition of the forms fields
        
        self._indir   = ControlText(label="Choose Dir:", value=self.INDIR)
        self._indir.value = self.INDIR

        self._outdir   = ControlText(label="Choose Output Dir:", value=self.OUTDIR)
        self._outdir.value = self.OUTDIR

        self._infiles     = []
        self._filescount  = ControlLabel("Total Files Selected: ")

        self._selectfiles = ControlButton('Select Files')
        self._selectfiles.value = self.__loadFiles

        # self._videofile  = ControlFile('Video')
        # self._outputfile = ControlText('Results output file')
        # self._threshold  = ControlSlider('Threshold', default=114, minimum=0, maximum=255)
        # self._blobsize   = ControlSlider('Minimum blob size', default=110, minimum=100, maximum=2000)
        # self._player     = ControlPlayer('Player')
        self._runbutton  = ControlButton('Run')

        # #Define the function that will be called when a file is selected
        # self._videofile.changed_event     = self.__videoFileSelectionEvent
        # #Define the event that will be called when the run button is processed
        self._runbutton.value       = self.__runEvent

        self._progress_label = ControlLabel("Progress:")
        self._progress       = ControlProgress("%")
        # #Define the event called before showing the image in the player
        # self._player.process_frame_event    = self.__process_frame

        self._image_tbls = controls.ControlList()

        #Define the organization of the Form Controls
        self._formset = [
            ('_indir', '_outdir'),
            ('_filescount', '_selectfiles'),
            '_image_tbls',
            '_runbutton',
            ('_progress_label', '_progress'), ''
        ]

    def __loadFiles(self):
        self._infiles = list(ImageFinder.ifind(self._indir.value))
        self._filescount.value = "Total Files Found to load: " + str(len(self._infiles))
        self._progress.max = len(self._infiles)

        image_per_row = 2
        rows_count = math.floor(len(self._infiles) / image_per_row)

        for row in range(rows_count):
            for c in range(image_per_row):
                img = ControlImage()
                img.parent = self._image_tbls
                print(self._infiles[c*row])
                img.value = self._infiles[c*row] # cv2.imread(self._infiles[c*row], 1)
                self._image_tbls.set_value(c, row, img)

    def __runEvent(self):
        """
        After setting the best parameters run the full algorithm
        """
        self.outbox = Queue()
        def update_progress():
            self._progress.value = self.outbox.qsize()

        def done_progress():
            self._progress.value = self._progress.max
            print("Completed")
        hasher = ImageHasher(self._indir.value, self.outbox, progress_callback=update_progress, done_callback=done_progress)
        hasher.start()

if __name__ == '__main__':

    from pyforms import start_app
    start_app(ImageDeDuplicatorApp)