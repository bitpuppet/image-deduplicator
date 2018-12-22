#client.py
'''we are going to need the BaseManager class again'''
from multiprocessing.managers import BaseManager

class QueueClient(object):
    
    def __init__(self, queue_name, server_host, server_port, server_authkey):
        '''clients need to know which queue on our server they want to use'''
        self.queue_name = queue_name

        '''as name suggested queue_server, queue_port and server_authkey
        are needed to connect to our queue server
        '''
        self.host = server_host
        self.port = server_port
        self.authkey = server_authkey
        
        '''Now it is an important step, we need to tell BaseManager class about this queue
        so when we connect with our server, we can get the proxy object of our queue. 
        Notice here, we are not passing any callable here for the same reason'''
        BaseManager.register(self.queue_name)
        
        '''lets create an instance of BaseManager class so we can connect to server'''
        self.manager = BaseManager(address=(self.host, self.port), 
                                   authkey=self.authkey)
        self.manager.connect()
        
    def get_queue(self):
        '''this is an important method, we'll use getattr() method to inspect
        the availability of queue in our manager instance and returns the queue.
        Remember in QueueServer class, we register a callable that returns the 
        actual database_queue object, here is what we are asking for manager to
        give us that callable object which we can call to get the proxy queue object
        '''
        queue_callable = getattr(self.manager, self.queue_name)
        
        '''now that we have the callable, we'll just call this and it will return the
        proxy queue object (remember it is a proxy object and we can perform all the 
        operations that Queue.Queue class provides and it'll be communicated back to
        our server on the original queue'''
        return queue_callable()
