import json

class Trigger:
	def __init__(self, triggername, starttime, endtime, groupnumber):
		self.triggername = triggername
		self.starttime = starttime
		self.endtime = endtime
		self.groupnumber = groupnumber
		self.events = []

	def __repr__(self):
		return (
			(
				"{"
				+ f'"triggername": "{self.triggername}", "starttime": {self.starttime}, "endtime": {self.endtime}, "groupnumber": {self.groupnumber}, "events": {[repr(event) for event in self.events]}'
				+ "}"
			)
			.replace("\\", "")
			.replace("'", "")
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def init(self):
		# TODO
		pass

	def addEvent(self, event):
		self.events.append(event)
