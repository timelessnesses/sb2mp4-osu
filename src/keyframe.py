def k(keyframes, time):
	keyframe = None
	endKeyframe = None
	for i, k in enumerate(keyframes):
		if len(k) == 0:
			print(keyframes)
			print(k)
		if k[0] > time:
			keyframe = keyframes[i - 1]
			endKeyframe = keyframes[i]
			break
		else:
			continue
	if keyframe is None:
		keyframe = keyframes[-1]
	if keyframe[2] is None:
		return keyframe[1]
	if time == keyframe[3]:
		return keyframe[1]
	t = (time - keyframe[3]) / (endKeyframe[0] - keyframe[3])
	t = applyEasing(keyframe[2], t)
	if type(keyframe[1]) is tuple:
		return tuple(
			keyframe[1][i] + (endKeyframe[1][i] - keyframe[1][i]) * t
			for i in range(len(keyframe[1]))
		)
	return keyframe[1] + (endKeyframe[1] - keyframe[1]) * t


def keyframeValueAt(keyframes, time):
	if len(keyframes) == 2 and type(keyframes[1]) is list:
		x = k(keyframes[0], time)
		y = k(keyframes[1], time)
		return (x, y)
	else:
		return k(keyframes, time)


# keyframes (time, value, easing, actualStarttime)
def calculatePositionKeyframes(self):
	keyframes = []
	applicableEvents = [
		event for event in self.expandedEvents if event.type.startswith("M")
	]
	if len(applicableEvents) == 0:
		# the initial position is used only if there are no move commands
		keyframes.append((float("-inf"), self.coordinates, None))
		return keyframes
	# the interaction between incompatible commands (Move with MoveX or MoveY, or Scale with ScaleVec)
	# is undefined and i'm not dealing with that. maybe i'll check how lazer does it if i find time
	moveCompatible = True if applicableEvents[0].type == "M" else False
	applicableEvents = (
		[event for event in applicableEvents if event.type == "M"]
		if moveCompatible
		else [
			[event for event in applicableEvents if event.type == "MX"],
			[event for event in applicableEvents if event.type == "MY"],
		]
	)
	# two sets of keyframes are used for MX and MY commands
	if moveCompatible:
		i = -2
		for event in applicableEvents:
			i += 2
			appendEndtime = True if event.endtime > event.starttime else False
			if i == 0:
				# the starting event overrides the sprite's initial position
				keyframes.append(
					(float("-inf"), (event.params[0], event.params[1]), None)
				)
				keyframes.append(
					(
						event.starttime,
						(event.params[0], event.params[1])
						if appendEndtime
						else event.params[1],
						event.easing if appendEndtime else None,
						event.starttime,
					)
				)
				if appendEndtime:
					keyframes.append(
						(event.endtime, (event.params[2], event.params[3]), None)
					)
					i += 1
				continue
			if keyframes[i - 1][0] >= event.starttime:
				# the first event overrides subsequent overlapping events,
				# but their interpolation still starts from their respective start times
				keyframes.append(
					(
						keyframes[i - 1][0],
						(event.params[0], event.params[1])
						if appendEndtime
						else event.params[1],
						event.easing if appendEndtime else None,
						event.starttime,
					)
				)
				i -= 1
			else:
				keyframes.append(
					(
						event.starttime,
						(event.params[0], event.params[1])
						if appendEndtime
						else event.params[1],
						event.easing if appendEndtime else None,
						event.starttime,
					)
				)
			if appendEndtime:
				keyframes.append(
					(event.endtime, (event.params[2], event.params[3]), None)
				)
			else:
				i -= 1
	else:
		keyframes = [[], []]
		if len(applicableEvents[0]) == 0:
			keyframes[0].append((float("-inf"), self.coordinates[0], None))
		else:
			i = -2
			for event in applicableEvents[0]:
				i += 2
				appendEndtime = True if event.endtime > event.starttime else False
				if i == 0:
					keyframes[0].append((float("-inf"), event.params[0], None))
					keyframes[0].append(
						(
							event.starttime,
							event.params[0] if appendEndtime else event.params[1],
							event.easing if appendEndtime else None,
							event.starttime,
						)
					)
					if appendEndtime:
						keyframes[0].append((event.endtime, event.params[1], None))
						i += 1
					continue
				if keyframes[0][i - 1][0] >= event.starttime:
					keyframes[0].append(
						(
							keyframes[0][i - 1][0],
							event.params[0] if appendEndtime else event.params[1],
							event.easing if appendEndtime else None,
							event.starttime,
						)
					)
					i -= 1
				else:
					keyframes[0].append(
						(
							event.starttime,
							event.params[0] if appendEndtime else event.params[1],
							event.easing if appendEndtime else None,
							event.starttime,
						)
					)
				if appendEndtime:
					keyframes[0].append((event.endtime, event.params[1], None))
				else:
					i -= 1
		if len(applicableEvents[1]) == 0:
			keyframes[1].append((float("-inf"), self.coordinates[1], None))
		else:
			i = -2
			for event in applicableEvents[1]:
				i += 2
				appendEndtime = True if event.endtime > event.starttime else False
				if i == 0:
					keyframes[1].append((float("-inf"), event.params[0], None))
					keyframes[1].append(
						(
							event.starttime,
							event.params[0] if appendEndtime else event.params[1],
							event.easing if appendEndtime else None,
							event.starttime,
						)
					)
					if appendEndtime:
						keyframes[1].append((event.endtime, event.params[1], None))
						i += 1
					continue
				if keyframes[1][i - 1][0] >= event.starttime:
					keyframes[1].append(
						(
							keyframes[1][i - 1][0],
							event.params[0] if appendEndtime else event.params[1],
							event.easing if appendEndtime else None,
							event.starttime,
						)
					)
					i -= 1
				else:
					keyframes[1].append(
						(
							event.starttime,
							event.params[0] if appendEndtime else event.params[1],
							event.easing if appendEndtime else None,
							event.starttime,
						)
					)
				if appendEndtime:
					keyframes[1].append((event.endtime, event.params[1], None))
				else:
					i -= 1
	return keyframes


def calculateRotationKeyframes(self):
	keyframes = []
	applicableEvents = [event for event in self.expandedEvents if event.type == "R"]
	if len(applicableEvents) == 0:
		# the default rotation is 0
		keyframes.append((float("-inf"), 0, None))
		return keyframes
	i = -2
	for event in applicableEvents:
		i += 2
		appendEndtime = True if event.endtime > event.starttime else False
		if i == 0:
			keyframes.append((float("-inf"), event.params[0], None))
			keyframes.append(
				(
					event.starttime,
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			if appendEndtime:
				keyframes.append((event.endtime, event.params[1], None))
				i += 1
			continue
		if keyframes[i - 1][0] >= event.starttime:
			keyframes.append(
				(
					keyframes[i - 1][0],
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			i -= 1
		else:
			keyframes.append(
				(
					event.starttime,
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
		if appendEndtime:
			keyframes.append((event.endtime, event.params[1], None))
		else:
			i -= 1
	return keyframes


def calculateScaleKeyframes(self):
	keyframes = []
	applicableEvents = [
		event for event in self.expandedEvents if event.type == "S" or event.type == "V"
	]
	if len(applicableEvents) == 0:
		# the default scale is (1, 1)
		keyframes.append((float("-inf"), (1, 1), None))
		return keyframes
	scaleCompatible = True if applicableEvents[0].type == "S" else False
	applicableEvents = [
		event
		for event in applicableEvents
		if ((event.type == "S") if scaleCompatible else event.type == "V")
	]
	i = -2
	startScale = (
		lambda e: (e.params[0], e.params[0])
		if scaleCompatible
		else (e.params[0], e.params[1])
	)
	endScale = (
		lambda e: (e.params[1], e.params[1])
		if scaleCompatible
		else (e.params[2], e.params[3])
	)
	for event in applicableEvents:
		i += 2
		appendEndtime = True if event.endtime > event.starttime else False
		if i == 0:
			keyframes.append((float("-inf"), startScale(event), None))
			keyframes.append(
				(
					event.starttime,
					startScale(event) if appendEndtime else startScale(event),
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			if appendEndtime:
				keyframes.append((event.endtime, endScale(event), None))
				i += 1
			continue
		if keyframes[i - 1][0] >= event.starttime:
			keyframes.append(
				(
					keyframes[i - 1][0],
					startScale(event) if appendEndtime else startScale(event),
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			i -= 1
		else:
			keyframes.append(
				(
					event.starttime,
					startScale(event) if appendEndtime else startScale(event),
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
		if appendEndtime:
			keyframes.append((event.endtime, endScale(event), None))
		else:
			i -= 1
	return keyframes


def calculateColorKeyframes(self):
	keyframes = []
	applicableEvents = [event for event in self.expandedEvents if event.type == "C"]
	if len(applicableEvents) == 0:
		# the default color is (255, 255, 255)
		keyframes.append((float("-inf"), (255, 255, 255), None))
		return keyframes
	i = -2
	for event in applicableEvents:
		i += 2
		appendEndtime = True if event.endtime > event.starttime else False
		if i == 0:
			keyframes.append((float("-inf"), event.params[0], None))
			keyframes.append(
				(
					event.starttime,
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			if appendEndtime:
				keyframes.append((event.endtime, event.params[1], None))
				i += 1
			continue
		if keyframes[i - 1][0] >= event.starttime:
			keyframes.append(
				(
					keyframes[i - 1][0],
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			i -= 1
		else:
			keyframes.append(
				(
					event.starttime,
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
		if appendEndtime:
			keyframes.append((event.endtime, event.params[1], None))
		else:
			i -= 1
	return keyframes


def calculateOpacityKeyframes(self):
	keyframes = []
	applicableEvents = [event for event in self.expandedEvents if event.type == "F"]
	if len(applicableEvents) == 0:
		# the default opacity is 1
		keyframes.append((float("-inf"), 1, None))
		return keyframes
	i = -2
	for event in applicableEvents:
		i += 2
		appendEndtime = True if event.endtime > event.starttime else False
		if i == 0:
			keyframes.append((float("-inf"), event.params[0], None))
			keyframes.append(
				(
					event.starttime,
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			if appendEndtime:
				keyframes.append((event.endtime, event.params[1], None))
				i += 1
			continue
		if keyframes[i - 1][0] >= event.starttime:
			keyframes.append(
				(
					keyframes[i - 1][0],
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
			i -= 1
		else:
			keyframes.append(
				(
					event.starttime,
					event.params[0] if appendEndtime else event.params[1],
					event.easing if appendEndtime else None,
					event.starttime,
				)
			)
		if appendEndtime:
			keyframes.append((event.endtime, event.params[1], None))
		else:
			i -= 1
	return keyframes


def calculateEffectKeyframes(self, effect):
	keyframes = []
	applicableEvents = [
		event
		for event in self.expandedEvents
		if event.type == "P" and event.params == effect
	]
	if len(applicableEvents) == 0:
		# effects are deactivated by default
		keyframes.append((float("-inf"), False, None))
		return keyframes
	i = -2
	for event in applicableEvents:
		i += 2
		appendEndtime = True if event.starttime > event.endtime else False
		if i == 0:
			keyframes.append((float("-inf"), True, None))
			if appendEndtime:
				keyframes.append((event.starttime, False, None))
			else:
				i -= 1
			continue
		if keyframes[i - 1][0] >= event.starttime:
			keyframes.append((keyframes[i - 1][0], True, None))
			i -= 1
		else:
			keyframes.append((event.starttime, True, None))
		if appendEndtime:
			keyframes.append((event.endtime, False, None))
		else:
			i -= 1
	return keyframes