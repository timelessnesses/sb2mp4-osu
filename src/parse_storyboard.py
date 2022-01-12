import os
from util import applyVariables, removeQuotes
from sprite import Sprite
from event import Event
from loop import Loop
from beatmapinfo import BeatmapInfo
from animation import Animation
from sample import Sample
from util import s

totalLineNumber = 0

def ParseStoryboard(directory, osbfile, diff=None, inDiff=False):
	variables = []
	objects = []
	with open(os.path.join(directory, osbfile), "r", encoding="utf-8") as file:
		section = ""
		currentObject = None
		currentLoop = None
		currentTrigger = None
		inLoop = False
		inTrigger = False
		lineNumber = 0
		info = dict()
		while True:
			lineNumber += 1
			global totalLineNumber
			totalLineNumber += 1
			line = file.readline()
			if not line:
				break
			# print(line, end="")

			if line.startswith("//"):
				continue

			# determine start of new section
			if "[Events]" in line:
				if currentObject is not None:
					if currentLoop is not None:
						currentObject.addLoop(currentLoop)
					if currentTrigger is not None:
						currentObject.addTrigger(currentTrigger)
					objects.append(currentObject)
				section = "Events"
				continue
			elif "[Variables]" in line:
				if currentObject is not None:
					if currentLoop is not None:
						currentObject.addLoop(currentLoop)
					if currentTrigger is not None:
						currentObject.addTrigger(currentTrigger)
					objects.append(currentObject)
				section = "Variables"
				continue
			elif "[General]" in line or "[Metadata]" in line:
				if currentObject is not None:
					if currentLoop is not None:
						currentObject.addLoop(currentLoop)
					if currentTrigger is not None:
						currentObject.addTrigger(currentTrigger)
					objects.append(currentObject)
				section = "BeatmapInfo"
				continue
			elif line.strip().startswith("["):
				if currentObject is not None:
					if currentLoop is not None:
						currentObject.addLoop(currentLoop)
					if currentTrigger is not None:
						currentObject.addTrigger(currentTrigger)
					objects.append(currentObject)
				section = ""
				continue

			# parse beatmap info
			if section == "BeatmapInfo":
				key = line.split(":")[0].strip()
				value = ":".join(line.split(":")[1:]).strip()
				if key and value:
					info[key] = value

			# parse variables
			if section == "Variables":
				values = line.split("=")
				if len(values) == 2:
					if values[1].endswith("\n"):
						values[1] = values[1][:-1]
					variables.append((values[0], values[1]))

			# parse events
			if section == "Events":
				depth = 0
				while line[depth].startswith(" "):
					depth += 1

				line = applyVariables(line.strip(), variables)
				split = line.split(",")

				if inLoop and depth < 2:
					inLoop = False
					if currentLoop is None:
						print(
							f"ParseError: No loop when there is supposed to be one.\n{osbfile}\nLine {line},\n{currentObject}"
						)
						raise
					if len(currentLoop.events) == 0 and currentLoop.loopcount != 0:
						print(
							f"ParseError: Empty loop.\n{osbfile}\nLine {lineNumber},\n{currentObject}"
						)
						raise
					currentObject.addLoop(currentLoop)

				if inTrigger and depth < 2:
					inTrigger = False
					if currentTrigger is None:
						print(
							f"ParseError: No trigger when there is supposed to be one.\n{osbfile}\nLine {line},\n{currentObject}"
						)
						raise
					currentObject.addTrigger(currentTrigger)

				# new objects
				if split[0] == "Sprite":
					if currentObject is not None:
						objects.append(currentObject)
					layer = split[1]
					origin = split[2]
					filepath = removeQuotes(split[3])
					coordinates = (float(split[4]), float(split[5]))
					currentObject = Sprite(layer, origin, filepath, coordinates)
				elif split[0] == "Animation":
					if currentObject is not None:
						objects.append(currentObject)
					layer = split[1]
					origin = split[2]
					filepath = removeQuotes(split[3])
					coordinates = (float(split[4]), float(split[5]))
					framecount = int(split[6])
					framedelay = float(split[7])
					looptype = split[8]
					currentObject = Animation(
						layer,
						origin,
						filepath,
						coordinates,
						framecount,
						framedelay,
						looptype,
					)
				elif split[0] == "Sample":
					time = float(split[1])
					layer = split[2]
					filepath = removeQuotes(split[3])
					volume = float(split[4])
					objects.append(Sample(time, layer, filepath, volume))
				elif split[0] == "0" and split[1] == "0":
					coordinates = (
						int(split[3]) + 320 if split[3] else 320,
						int(split[4]) + 240 if split[4] else 240,
					)
					print(type(coordinates))
					print(type(split))
					objects.append(Background(split[2], coordinates))

				# loops and triggers
				elif split[0] == "T":
					if inLoop:
						print(
							f"ParseError: Trigger detected inside loop.\n{osbfile}\nLine {lineNumber}, {line}"
						)
						raise
					triggername = split[1]
					starttime = float(split[2])
					loopcount = int(split[3])
					groupnumber = int(split[4]) if len(split) > 4 else 0
					currentTrigger = Trigger(
						triggername, starttime, loopcount, groupnumber
					)
					inTrigger = True
				elif split[0] == "L":
					if inTrigger:
						print(
							f"ParseError: Loop detected inside trigger.\n{osbfile}\nLine {lineNumber}, {line}"
						)
						raise
					starttime = float(split[1])
					loopcount = int(split[2])
					currentLoop = Loop(starttime, loopcount)
					inLoop = True

				# events
				elif split[0] == "F":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					startopacity = float(split[4])
					endopacity = float(split[5]) if len(split) > 5 else startopacity
					params = (startopacity, endopacity)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "S":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					startscale = float(split[4])
					endscale = float(split[5]) if len(split) > 5 else startscale
					params = (startscale, endscale)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "V":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					startx = float(split[4])
					starty = float(split[5])
					endx = float(split[6]) if len(split) > 6 else startx
					endy = float(split[7]) if len(split) > 7 else starty
					params = (startx, starty, endx, endy)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "R":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					startangle = float(split[4])
					endangle = float(split[5]) if len(split) > 5 else startangle
					params = (startangle, endangle)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "M":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					startx = float(split[4])
					starty = float(split[5])
					endx = float(split[6]) if len(split) > 6 else startx
					endy = float(split[7]) if len(split) > 7 else starty
					params = (startx, starty, endx, endy)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "MX":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					startx = float(split[4])
					endx = float(split[5]) if len(split) > 5 else startx
					params = (startx, endx)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "MY":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					starty = float(split[4])
					endy = float(split[5]) if len(split) > 5 else starty
					params = (starty, endy)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "C":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					color1 = (int(split[4]), int(split[5]), int(split[6]))
					color2 = (
						int(split[7]) if len(split) > 7 else color1[0],
						int(split[8]) if len(split) > 8 else color1[1],
						int(split[9]) if len(split) > 8 else color1[2],
					)
					params = (color1, color2)
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
				elif split[0] == "P":
					_type = split[0]
					easing = int(split[1])
					starttime = float(split[2])
					endtime = float(split[3]) if split[3] else starttime
					effect = split[4]
					params = effect
					event = Event(_type, easing, starttime, endtime, params)
					if inTrigger:
						currentTrigger.addEvent(event)
					elif inLoop:
						currentLoop.addEvent(event)
					else:
						currentObject.addEvent(event)
		if inLoop:
			inLoop = False
			if currentLoop is None:
				print(
					f"ParseError: No loop when there is supposed to be one.\n{osbfile}\nLine {lineNumber},\n{currentObject}"
				)
				raise
			if len(currentLoop.events) == 0:
				print(
					f"ParseError: Empty loop.\n{osbfile}\nLine {lineNumber},\n{currentObject}"
				)
				raise
			currentObject.addLoop(currentLoop)

		if inTrigger:
			inTrigger = False
			if currentTrigger is None:
				print(
					f"ParseError: No trigger when there is supposed to be one.\n{osbfile}\nLine {lineNumber},\n{currentObject}"
				)
				raise
			currentObject.addTrigger(currentTrigger)
		if currentObject is not None:
			objects.append(currentObject)
		objects.append(BeatmapInfo(info))
		if not inDiff:
			print(f"Parsed {totalLineNumber} line{s(lineNumber)}")
	if diff:
		osu = ParseStoryboard(directory, diff, inDiff=False)
		for o in osu:
			objects.append(o)
	sprites = [o for o in objects if isinstance(o, Sprite)]
	animations = [o for o in objects if isinstance(o, Animation)]
	samples = [o for o in objects if isinstance(o, Sample)]
	if inDiff:
		print(
			f"Discovered {len(sprites)} sprite{s(sprites)}, {len(animations)} animation{s(animations)} and {len(samples)} sample{s(samples)}"
		)
	return objects