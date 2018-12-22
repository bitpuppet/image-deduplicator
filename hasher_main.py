#hasher_main.py
import sys

from image_hasher import ImageHasher
from msg_queue.client import QueueClient

def main():
 
    src_path = '/vagrant/my_pictures/'
    workers_count = 5
 
    #we can use ArgumentParser but keeping things simple
    if len(sys.argv) >= 2:
        workers_count = int(sys.argv[1])
    print('Workers Count: %s' % (workers_count))

    #lets create a QueueClient object to connect to queue server to 
    #get the `database_queue` proxy object as `outbox` queue 
    q_client = QueueClient('database_queue', '', 12000, 'abc')
    outbox = q_client.get_queue()
    
    hasher = ImageHasher(src_path, outbox, workers_count)
    try:
        hasher.start()
    except KeyboardInterrupt:
        print('Got Shutdown. Stopping')
        hasher.shutdown.set()
        with hasher.empty: 
            hasher.empty.notifyAll()
 
if __name__ == '__main__':
    sys.exit(main())
