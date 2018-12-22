import os
import sys
import time
from collections import defaultdict, namedtuple
from queue import Queue, Empty
from threading import Thread, Event, Condition, current_thread

from file_finder import ImageFinder
from photohash.photohash import average_hash, hashes_are_similar

ImageInfo = namedtuple('ImageInfo', ['img_hash', 'img_path'])
class ImageHasher(object):

    def __init__(self, src_path, outbox, workers_count=5, progress_callback=None, done_callback=None):
        
        #image directory path
        self.src_path = src_path

        #inbox: queue to store unprocessed image 
        #from which threads will read the unprocessed image path
        self.inbox = Queue()

        #queue where threads will write the calculated hash and
        #the path of image as a tuple
        self.outbox = outbox

        #failed images will be logged here
        self.error = Queue()

        #event to watch for shutdown
        self.shutdown = Event()

        #event to indicate workers that 
        #we are done sending data
        self.done = Event()

        #condition to signal when queue is not empty
        self.empty = Condition()

        self.workers = []
        self.workers_count = workers_count

        self.progress_callback = progress_callback
        self.done_callback = done_callback

    def _worker(self):
        '''
        This is the worker which will get the image from 'inbox',
        calculate the hash and puts the result in 'outbox'
        '''

        while not self.shutdown.isSet():
            
            try:
                image_path = self.inbox.get_nowait()
            except Empty:
                print('no data found. isset: ' , self.done.isSet())
                if not self.done.isSet():
                    with self.empty:
                        self.empty.wait()
                        continue
                else:
                    break

            if not os.path.exists(image_path):
                self.error.put((image_path, 'Image Does not Exist'))
                
            try:
                print('[%s] Processing %s' % (current_thread().ident, image_path))
                image_hash = average_hash(image_path)
                info = ImageInfo(image_hash, image_path)
                print(info)
                self.outbox.put(info)
                print("Qsize: " , self.outbox.qsize())
            except IOError as err:
                print('ERROR: Got %s for image : %s' % (image_path, err))
            finally:
                if self.progress_callback:
                    self.progress_callback()

        print('Worker %s has done processing.' % current_thread().ident)

    def _start_workers(self):
        '''method to start all the worker threads'''
        for _ in range(self.workers_count):
            worker = Thread(target=self._worker)
            worker.start()
            self.workers.append(worker)

    def images_are_similar(self, image1_hash, image2_hash, tolerance=6):
        return hashes_are_similar(image1_hash, image2_hash, tolerance)

    @classmethod
    def group_by_similar_images(cls, outbox, tolerance=6):

        similar_images = defaultdict(list)
        print("Outbox Qsize:" , outbox.qsize())
        # images = [ (img_hash, img_path) for (img_hash, img_path) in outbox.get_nowait() ]
        images = []
        
        #TODO: figure out he issue with img_info and get going
        #for img in outbox.get_nowait():
        for _ in range(0, outbox.qsize()):
            img_info = outbox.get_nowait()
            print("TYpe: " , type(img_info))
            print(img_info)

            img_hash = img_info.img_hash
            img_path = img_info.img_path
            print(img_hash, img_path)
            images.append(img_info)

        seen = set()
        for index, img_info in enumerate(images):
            img_hash = img_info.img_hash
            img_path = img_info.img_path
            for i in range(index, len(images)):
                img1_hash = images[i].img_hash
                img1_path = images[i].img_path
                if img1_path in seen:
                    continue
                print("Checking for img1: ", img_hash, " img2:", img1_hash)
                if hashes_are_similar(img_hash, img1_hash, tolerance):
                    print("Image: ", img_hash , ' is similart to ', img1_hash)
                    similar_images[img_path].append(img1_path)
                    seen.add(img_path)
        print(similar_images)
        return similar_images

    def start(self):
        
        #lets start workers
        self._start_workers()
        print('Workers are started. Waiting for work...')

        #find images to put in inbox, workers are waiting
        images_path = ImageFinder.ifind(self.src_path)
        for image_path in images_path:
            print('Found image: %s' % image_path)
            with self.empty:
                #acquire the condition lock, put image path in inbox queue
                #and notify the worker thread who is waiting for an item to be put in the inbox queue
                self.inbox.put_nowait(image_path)
                self.empty.notify()

        #lets tell every worker we are done sending data
        #and exit once they are get Empty exception
        self.done.set()

        print('All images has been sent to worker. Waiting to finish')
        #all we have to do now is wait for
        #workers to finish processing
        for worker in self.workers:
            worker.join()
            print('Worker %s has done processing' % (worker.ident))

        # #now that we have all the images processed
        # #lets see how many duplicates are there
        # dupe_images = defaultdict(list)
        # while True:
        #     try:
        #         (image_hash, image_path) = self.outbox.get_nowait()
        #         dupe_images[image_hash].append(image_path)
        #     except Empty:
        #         break

        # for _hash, _paths in dupe_images.items():
        #     print('Hash: %s DupeCount: %s Paths: %s' % (_hash, len(_paths), ','.join(_paths)))
        if self.done_callback:
            self.done_callback()