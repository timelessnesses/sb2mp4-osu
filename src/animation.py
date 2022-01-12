class Animation:
	def __init__(
		self, layer, origin, filepath, coordinates, framecount, framedelay, looptype
	):
		self.layer = layer
		self.origin = origin
		self.filepath = filepath
		self.coordinates = coordinates
		self.framecount = framecount
		self.framedelay = framedelay
		self.looptype = looptype
		self.events = []
		self.loops = []
		self.triggers = []

	def __repr__(self):
		return (
			"{"
			+ f'"layer": "{self.layer}", "origin": "{self.origin}", "filepath": "{self.filepath}", "coordinates": "{self.coordinates}", "framecount": {self.framecount}, "framedelay": {self.framedelay}, "looptype": "{self.looptype}", "events": {[repr(event) for event in self.events]}, "loops": {[repr(loop) for loop in self.loops]}, "triggers": {[repr(trigger) for trigger in self.triggers]}'.replace(
				"\\", ""
			).replace(
				"'", ""
			)
			+ "}"
		)

	def __str__(self):
		return json.dumps(json.loads(repr(self)), indent=4)

	def init(self):
		for loop in self.loops:
			loop.init()
		for trigger in self.triggers:
			trigger.init()

		# TODO: consider triggers
		expandedEvents = self.events
		for loop in self.loops:
			for event in loop.expandedEvents:
				expandedEvents.append(event)
		self.expandedEvents = sorted(expandedEvents, key=lambda event: event.starttime)

		self.activetime = calculateActivetime(self)
		self.calculateFrameIndex = calculateFrameIndex

		self.positionKeyframes = calculatePositionKeyframes(self)
		self.rotationKeyframes = calculateRotationKeyframes(self)
		self.scaleKeyframes = calculateScaleKeyframes(self)
		self.colorKeyframes = calculateColorKeyframes(self)
		self.opacityKeyframes = calculateOpacityKeyframes(self)
		self.flipHKeyframes = calculateEffectKeyframes(self, "H")
		self.flipVKeyframes = calculateEffectKeyframes(self, "V")
		self.additiveKeyframes = calculateEffectKeyframes(self, "A")

	def positionAt(self, time):
		return keyframeValueAt(self.positionKeyframes, time)

	def rotationAt(self, time):
		return keyframeValueAt(self.rotationKeyframes, time)

	def scaleAt(self, time):
		return keyframeValueAt(self.scaleKeyframes, time)

	def colorAt(self, time):
		return keyframeValueAt(self.colorKeyframes, time)

	def opacityAt(self, time):
		return keyframeValueAt(self.opacityKeyframes, time)

	def effectAt(self, time, effect):
		return keyframeValueAt(
			self.flipHKeyframes
			if effect == "H"
			else self.flipVKeyframes
			if effect == "V"
			else self.additiveKeyframes
			if effect == "A"
			else None,
			time,
		)

	def frameIndexAt(self, time):
		if hasattr(self, "calculateFrameIndex"):
			frameIndex = self.calculateFrameIndex(self, time)
			if frameIndex >= self.framecount or frameIndex < 0:
				print(self)
				print(frameIndex)
				raise
			return frameIndex
		else:
			raise

	def addEvent(self, event):
		self.events.append(event)

	def addLoop(self, loop):
		self.loops.append(loop)

	def addTrigger(self, trigger):
		self.triggers.append(trigger)