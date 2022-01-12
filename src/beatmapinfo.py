class BeatmapInfo:
	def __init__(self, beatmapInfo):
		self.beatmapInfo = beatmapInfo

	def __repr__(self):
		return (
			("{" + f'"beatmapInfo": "{self.beatmapInfo}"' + "}")
			.replace("\\", "")
			.replace("'", "")
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def init(self):
		pass
