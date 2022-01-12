from sprite import Sprite
from animation import Animation
from event import Event
from util import s
from sample import Sample
from background import Background
from beatmapinfo import BeatmapInfo
totalLineNumber = 0

class Storyboard:
	def __init__(self, directory, objects, frameSize):
		print(f"Initialising {len(objects)} object{s(objects)}")
		for o in objects:
			o.init()
		print("Initialised objects")
		self.objects = objects
		self.sprites = []
		self.animations = []
		self.samples = []
		self.spritesAndAnimations = []
		self.beatmapInfo = None
		backgrounds = []
		for o in self.objects:
			if isinstance(o, Sprite):
				self.sprites.append(o)
				self.spritesAndAnimations.append(o)
			if isinstance(o, Animation):
				self.animations.append(o)
				self.spritesAndAnimations.append(o)
			if isinstance(o, Sample):
				self.samples.append(o)
			if isinstance(o, Background):
				print("Found background")
				backgrounds.append(o)
			if isinstance(o, BeatmapInfo):
				self.beatmapInfo = o.beatmapInfo

		# cache and calculate background position beforehand
		self.frameSize = frameSize
		self.background = backgrounds[0] if len(backgrounds) > 0 else None
		self.directory = directory
		backgroundImage = (
			cv.resize(
				np.array(
					Image.open(
						os.path.join(self.directory, self.background.filepath)
					).convert("RGBA")
				),
				(
					int(frameSize[0] * self.frameSize[1] / float(self.frameSize[1])),
					self.frameSize[1],
				),
			)
			if self.background
			else None
		)
		self.frameScale = self.frameSize[0] / 854.0
		self.xOffset = int(
			(self.frameSize[0] - self.frameSize[1] * 4 / 3.0) * 0.5
		)  # to centre the image regardless of aspect ratio
		print(
			f"Background: {None if self.background is None else self.background.filepath}"
		)

		framePosition = (
			self.xOffset + int(self.background.coordinates[0] * self.frameScale),
			int(self.background.coordinates[1] * self.frameScale),
		)
		w = backgroundImage.shape[1]
		h = backgroundImage.shape[0]
		y1, y2 = framePosition[1], framePosition[1] + h
		x1, x2 = framePosition[0], framePosition[0] + w
		sy1, sy2 = 0 if y1 >= 0 else -y1, h if y2 <= self.frameSize[1] else h - (
			y2 - self.frameSize[1]
		)
		sx1, sx2 = 0 if x1 >= 0 else -x1, w if x2 <= self.frameSize[0] else w - (
			x2 - self.frameSize[0]
		)
		y1 = np.clip(y1, 0, self.frameSize[1])
		y2 = np.clip(y2, 0, self.frameSize[1])
		x1 = np.clip(x1, 0, self.frameSize[0])
		x2 = np.clip(x2, 0, self.frameSize[0])
		imageAlpha = backgroundImage[sy1:sy2, sx1:sx2, 3] / 255.0
		dummyImage = np.array(Image.new("RGB", self.frameSize))
		dummyImageAlpha = 1.0 - imageAlpha[sy1:sy2, sx1:sx2]
		for c in range(3):
			dummyImage[y1:y2, x1:x2, 2 if c == 0 else 0 if c == 2 else 1] = (
				imageAlpha * dummyImage[sy1:sy2, sx1:sx2, c]
				+ dummyImageAlpha * dummyImage[y1:y2, x1:x2, c]
			)
		self.backgroundImage = dummyImage
		self.blankImage = np.array(Image.new("RGB", self.frameSize))

		# cache sprites
		spriteImages = dict()
		for sprite in self.sprites:
			if not sprite.filepath in spriteImages:
				spriteImages[sprite.filepath] = np.array(
					Image.open(os.path.join(directory, sprite.filepath)).convert("RGBA")
				)
		self.spriteImages = spriteImages

		animationImages = dict()
		for animation in self.animations:
			if not animation.filepath in animationImages:
				base = ".".join(animation.filepath.split(".")[:-1])
				ext = "." + animation.filepath.split(".")[-1]
				animationImages[animation.filepath] = [
					np.array(
						Image.open(
							os.path.join(directory, base + str(i) + ext)
						).convert("RGBA")
					)
					for i in range(animation.framecount)
				]
		self.animationImages = animationImages

	def generateAudio(self, outFile):
		command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
		command.append("-i")
		command.append(
			f"\"{os.path.join(self.directory, self.beatmapInfo['AudioFilename'].strip())}\""
		)
		delays = [
			int(self.beatmapInfo["AudioLeadIn"])
			if "AudioLeadIn" in self.beatmapInfo
			else 0
		]
		for sample in self.samples:
			command.append("-i")
			command.append(f'"{os.path.join(self.directory, sample.filepath)}"')
			delays.append(int(sample.starttime))
		command.append("-filter_complex")
		command.append(
			'"'
			+ ";".join(
				[
					f"[{i}:a]adelay=delays={delays[i]}:all=1[d{i}]"
					for i in range(len(delays))
				]
			)
			+ ";"
			+ ";".join(
				[
					f"%samix=inputs={len(delays)}[a]"
					% "".join([f"[d{i}]" for i in range(len(delays))])
				]
			)
			+ '"'
		)
		command.append("-map")
		command.append("[a]")
		command.append(outFile)
		# print(" ".join(command))
		sp.Popen(" ".join(command))

	def drawFrame(self, time):
		global i
		i += 1
		global t
		global t2
		t2 = pt()
		t = pt()
		frameImage = None

		if (
			self.background is not None
			and self.background.filepath not in self.spriteImages
		):
			# TODO: implement video
			frameImage = copy(self.backgroundImage)
		else:
			frameImage = copy(self.blankImage)

		# print(f" Active objects: {len([o for o in self.spritesAndAnimations if o.activetime is not None and o.activetime[0] <= time and o.activetime[1] > time])}           ", end="\r")
		# loop over all active objects
		for o in [
			o
			for o in self.spritesAndAnimations
			if o.activetime is not None
			and o.activetime[0] <= time
			and o.activetime[1] > time
		]:
			# check if sprite should be drawn
			alpha = o.opacityAt(time)
			if alpha == 0:
				continue
			scaleX, scaleY = o.scaleAt(time)
			if scaleX == 0 or scaleY == 0:
				continue

			image = (
				copy(self.spriteImages[o.filepath])
				if isinstance(o, Sprite)
				else copy(self.animationImages[o.filepath][o.frameIndexAt(time)])
			)
			scale = (abs(scaleX) * self.frameScale, abs(scaleY) * self.frameScale)
			newSize = (int(image.shape[1] * scale[0]), int(image.shape[0] * scale[1]))

			# check if resulting sprite is less than a pixel (sort of)
			if newSize[0] <= 0 or newSize[1] <= 0:
				continue

			width1 = newSize[0]
			height1 = newSize[1]

			# calculate rotation
			rotation = o.rotationAt(time)
			shouldRotate = True if rotation != 0 else False
			width2, height2 = (newSize[0], newSize[1])
			rotMatrix = None
			if shouldRotate:
				(w, h) = newSize
				(cx, cy) = (w // 2, h // 2)
				rotMatrix = cv.getRotationMatrix2D(
					(cx, cy), -rotation * 180 / math.pi, 1.0
				)
				cos = np.abs(rotMatrix[0, 0])
				sin = np.abs(rotMatrix[0, 1])
				width2 = int((h * sin) + (w * cos))
				height2 = int((h * cos) + (w * sin))
				rotMatrix[0, 2] += (width2 / 2) - cx
				rotMatrix[1, 2] += (height2 / 2) - cy

			# figure out where the origin point went
			dx = 0.5 * (width2 - width1)
			dy = 0.5 * (height2 - height1)
			midx = width2 * 0.5
			midy = height2 * 0.5
			origin = (
				(dx, dy)
				if o.origin == "TopLeft"
				else (midx, dy)
				if o.origin == "TopCentre"
				else (width2 - dx, dy)
				if o.origin == "TopRight"
				else (dx, midy)
				if o.origin == "CentreLeft"
				else (midx, midy)
				if o.origin == "Centre"
				else (width2 - dx, midy)
				if o.origin == "CentreRight"
				else (dx, height2 - dy)
				if o.origin == "BottomLeft"
				else (midx, height2 - dy)
				if o.origin == "BottomCentre"
				else (width2 - dx, height2 - dy)
				if o.origin == "BottomRight"
				else None
			)
			if shouldRotate:
				origin = (origin[0] - midx, origin[1] - midy)
				origin = (
					origin[0] * math.cos(rotation) - origin[1] * math.sin(rotation),
					origin[1] * math.cos(rotation) + origin[0] * math.sin(rotation),
				)
				origin = (origin[0] + midx, origin[1] + midy)

			position = o.positionAt(time)
			framePosition = (
				int(position[0] * self.frameScale - origin[0]) + self.xOffset,
				int(position[1] * self.frameScale - origin[1]),
			)
			y1, y2 = framePosition[1], framePosition[1] + height2
			x1, x2 = framePosition[0], framePosition[0] + width2
			sy1, sy2 = 0 if y1 >= 0 else -y1, height2 if y2 <= self.frameSize[
				1
			] else height2 - (y2 - self.frameSize[1])
			sx1, sx2 = 0 if x1 >= 0 else -x1, width2 if x2 <= self.frameSize[
				0
			] else width2 - (x2 - self.frameSize[0])
			y1 = np.clip(y1, 0, self.frameSize[1])
			y2 = np.clip(y2, 0, self.frameSize[1])
			x1 = np.clip(x1, 0, self.frameSize[0])
			x2 = np.clip(x2, 0, self.frameSize[0])

			# check if in bounds
			if not (y2 - y1 > 0 and x2 - x1 > 0):
				continue

			# apply flips
			flipH = o.effectAt(time, "H") or scaleX < 0
			flipV = o.effectAt(time, "V") or scaleY < 0
			flip = -1 if flipH and flipV else 0 if flipV else 1 if flipH else None
			if flip is not None:
				image = cv.flip(image, flip)

			# apply color and fade
			color = o.colorAt(time)
			for c in range(3):
				if color[c] != 255:
					np.multiply(
						image[:, :, c],
						color[c] / 255.0,
						casting="unsafe",
						out=image[:, :, c],
					)
			if alpha != 1:
				np.multiply(image[:, :, 3], alpha, casting="unsafe", out=image[:, :, 3])

			# apply scale
			image = cv.resize(image, newSize)

			# apply rotation
			if shouldRotate:
				image = cv.warpAffine(image, rotMatrix, (width2, height2))

			# put image on frame
			imageAlpha = image[sy1:sy2, sx1:sx2, 3] / 255.0
			if o.effectAt(time, "A"):
				for c in range(3):
					frameImage[y1:y2, x1:x2, c] = np.clip(
						imageAlpha * image[sy1:sy2, sx1:sx2, c]
						+ frameImage[y1:y2, x1:x2, c],
						0,
						255,
					)
			else:
				frameAlpha = 1.0 - imageAlpha
				for c in range(3):
					frameImage[y1:y2, x1:x2, c] = (
						imageAlpha * image[sy1:sy2, sx1:sx2, c]
						+ frameAlpha * frameImage[y1:y2, x1:x2, c]
					)
		return frameImage


