from multiprocessing import Condition, Lock
from multiprocessing import Value


class Table():

    def __init__(self, NPHIL, manager):
        self.current_phil = None
        self.forks = manager.list([True for i in range(NPHIL)])
        self.nphil = NPHIL
        self.mutex = Lock()
        self.free_fork = Condition(self.mutex)

    def set_current_phil(self, phil):
        self.current_phil = phil

    def get_current_phil(self):
        return self.current_phil

    def fork_available(self):
        phil = self.get_current_phil()
        return self.forks[phil] and self.forks[(phil + 1) % self.nphil]

    def wants_eat(self, phil):
        self.mutex.acquire()
        self.free_fork.wait_for(self.fork_available)
        self.forks[phil] = False
        self.forks[(phil + 1) % self.nphil] = False
        self.mutex.release()

    def wants_think(self, phil):
        self.mutex.acquire()
        self.forks[phil] = True
        self.forks[(phil + 1) % self.nphil] = True
        self.free_fork.notify_all()  
        self.mutex.release()
        
class CheatMonitor():

	def __init__(self):
		self.eating = Value ('i',0)
		self.thinking = Value('i',0)
		self.mutex = Lock()
		self.other_eating = Condition(self.mutex)
		
	def wants_think(self,phil):
		self.mutex.acquire()
		self.other_eating.wait_for(lambda : self.eating.value==2)
		self.eating.value -= 1
		self.mutex.release()
		
	def is_eating(self,phil):
		self.mutex.acquire()
		self.eating.value += 1
		self.other_eating.notify()
		self.mutex.release()
	
	