class Event:
	def __init__(self, _type, easing, starttime, endtime, params):
		self.type = _type
		self.easing = easing
		self.starttime = starttime
		self.endtime = endtime
		self.params = params

	def __repr__(self):
		return (
			(
				"{"
				+ f'"type": "{self.type}", "easing": {self.easing}, "starttime": {self.starttime}, "endtime": {self.endtime}, "params": "{self.params}"'
				+ "}"
			)
			.replace("\\", "")
			.replace("'", "")
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def valueAt(self, time):
		def interpolate(self, value1, value2, time):
			if self.endtime == self.starttime:
				return value2
			t = (time - self.starttime) / (self.endtime - self.starttime)
			t = applyEasing(self.easing, t)
			return value1 + (value2 - value1) * t

		if (
			self.type == "F"
			or self.type == "S"
			or self.type == "R"
			or self.type == "MX"
			or self.type == "MY"
		):
			return interpolate(self, self.params[0], self.params[1], time)
		elif self.type == "M" or self.type == "V":
			return (
				interpolate(self, self.params[0], self.params[2], time),
				interpolate(self, self.params[1], self.params[3], time),
			)
		elif self.type == "C":
			return (
				int(interpolate(self, self.params[0][0], self.params[1][0], time)),
				int(interpolate(self, self.params[0][1], self.params[1][1], time)),
				int(interpolate(self, self.params[0][2], self.params[1][2], time)),
			)
		elif self.type == "P":
			return True
