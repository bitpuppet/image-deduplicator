#db_processor.py
from hashlib import md5
import sqlite3
from threading import Event

from msg_queue.client import QueueClient

class DbProcessor(object):

    def __init__(self, db_file, inbox, shutdown=Event()):
        '''db_file is the name of database file and `inbox` is the shared queue where image_hasher
        is putting all the image tuples and we'll fetch it from there to put into database'''
        self.db_file = db_file
        self.inbox = inbox
        self.con = sqlite3.connect(self.db_file)
        self.shutdown = shutdown
        
    def setup_db(self):
        CREATE_TBL = 'CREATE TABLE IF NOT EXISTS image (image_id, image_path, image_hash)'
        self.con.execute(CREATE_TBL)
        self.con.commit()
        
    def insert(self, image_path, image_hash):
        _digest = md5.md5(image_path)
        image_id = str(_digest.hexdigest())
        query = 'INSERT INTO image (image_id, image_path, image_hash) VALUES (?, ?, ?)'
        self.con.execute(query, (image_id, image_path, image_hash,))
        self.con.commit()
        
    def process(self):
            
        self.setup_db()
        while not self.shutdown.isSet():
            try:
                image_path, image_hash = self.inbox.get()
                self.insert(image_path, image_hash)
            except sqlite3.IntegrityError as err:
                print(err)
                
    def stop(self):
        self.shutdown.set()
        
if __name__ == '__main__':
    
    client = QueueClient('database_queue', '', 12000, 'abc')
    inbox = client.get_queue()
    processor = DbProcessor('image.db', inbox)
    try:
        processor.start()
    except KeyboardInterrupt:
        processor.stop()
