from copy import copy

class Loop:
	def __init__(self, starttime, loopcount):
		self.starttime = starttime
		self.loopcount = loopcount
		self.events = []
		self.expandedEvents = []

	def __repr__(self):
		return (
			(
				"{"
				+ f'"starttime": {self.starttime}, "loopcount": {self.loopcount}, "events": {[repr(event) for event in self.events]}, "expandedEvents": {[repr(event) for event in self.expandedEvents]}'
				+ "}"
			)
			.replace("\\", "")
			.replace("'", "")
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def init(self):
		if self.loopcount <= 0:
			# today i learned that loops behave like this
			self.loopcount = 1
		self.looplength = self.events[-1].endtime
		for i in range(self.loopcount):
			for event in self.events:
				newEvent = copy(event)
				newEvent.starttime = (
					self.starttime + event.starttime + self.looplength * i
				)
				newEvent.endtime = self.starttime + event.endtime + self.looplength * i
				self.expandedEvents.append(newEvent)
		self.endtime = self.starttime + (self.events[-1].endtime) * self.loopcount

	def addEvent(self, event):
		self.events.append(event)
