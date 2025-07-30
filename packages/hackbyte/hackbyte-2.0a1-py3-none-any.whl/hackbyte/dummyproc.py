from . import logs as LOG
class DummyProcess:
	def __init__(self):
		self.pid = 9999
		LOG.warn("This is dummy mode. No real processes are used.")