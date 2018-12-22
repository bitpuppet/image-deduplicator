#server.py
import signal
from queue import Queue
from multiprocessing.managers import BaseManager

class QueueServer(object):

    def __init__(self, queue_server_host, queue_server_port, queue_server_authkey=None):
        '''
            host,port defines where your queuing server should be running while *authkey* 
            is going to be used to authenticate any communication between this queue server
            and clients connected to it. Clients will need to send the *authkey* to connect
            this queue server.
        '''
        self.host = queue_server_host
        self.port = queue_server_port
        self.authkey = queue_server_authkey

        '''
        Lets just say, we have a client that wants to put some image realted data into database 
        and also want to generate thumbnails from it (You know, where it is going,
        I'll give you a hint, checkout my last post about multi-threading)
        '''
        database_queue = Queue()
        thumbnail_queue = Queue()
        
        '''now we have a queue, but if since we want our clients to use it
        we'll need to register this queue with BaseManager via some callable that our client 
        can use to generate the proxy object. Yes, clients will be actually
        able to get the (proxy) object of this Queue and for them, they can
        pretty much use it like a regular queue (however, internally, BaseManager
        will be proxying that data sharing between client and server (and thats the 
        fun, we don't have to worry about locking, shared memory handling etc as 
        BaseManager will handle that, and for us it will be like using Queue between
        threads'''
        BaseManager.register('database_queue', callable=lambda:database_queue)
        BaseManager.register('thumbnail_queue', callable=lambda:thumbnail_queue)

        '''Now that we have registered our queue with BaseManager, we can instantiate
        manager object and start the server. As mentioned, BaseManager will spawn a 
        server in a subprocess and will handle all the communcation and data synchronization'''
        self.manager = BaseManager(address=(self.host, self.port), 
                                   authkey=self.authkey)
        
    def start(self):
        print('Starting Server Process...')
        self.manager.start()
        
    def stop(self):
        self.manager.shutdown()
        
if __name__ == '__main__':

    server = QueueServer('', 12000, 'abc')
    server.start()
        
    #this will make the process wait
    #signal.pause()
