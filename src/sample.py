class Sample:
	def __init__(self, starttime, layer, filepath, volume):
		self.starttime = starttime
		self.layer = layer
		self.filepath = filepath
		self.volume = volume

	def __repr__(self):
		return (
			(
				"{"
				+ f'"time": {self.time}, "layer": "{self.layer}", "filepath": "{self.filepath}", "volume": {self.volume}'
				+ "}"
			)
			.replace("\\", "")
			.replace("'", "")
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def init(self):
		pass
