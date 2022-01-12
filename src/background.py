class Background:
	def __init__(self, filepath, coordinates):
		self.filepath = filepath
		self.coordinates = coordinates

	def __repr__(self):
		return (
			(
				"{"
				+ f'"filepath": "{self.filepath}", "coordinates": {self.coordinates}'
				+ "}"
			)
			.replace("\\", "")
			.replace("'", "")
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def init(self):
		pass