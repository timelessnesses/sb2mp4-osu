import argparse
import json
import math
import os
import subprocess as sp
import sys
from time import perf_counter as pt
from dataclasses import dataclass
from enum import IntEnum

import cv2 as cv
import numpy as np
import pydub
from blend_modes import addition as additive
from PIL import Image, ImageDraw
from progress.bar import Bar

from easing import Easing
from parse_storyboard import ParseStoryboard
from storyboard import Storyboard

t = pt()
t2 = pt()

def applyEasing(easing, t):

	if easing == 0:
		return Easing(easing,t).Linear(t)
	elif easing == 1:
		return Easing(easing,t).Out(t)
	elif easing == 2:
		return Easing(easing,t).In(t)
	elif easing == 3:
		return Easing(easing,t).InQuad(t)
	elif easing == 4:
		return Easing(easing,t).OutQuad(t)
	elif easing == 5:
		return Easing(easing,t).InOutQuad(t)
	elif easing == 6:
		return Easing(easing,t).InCubic(t)
	elif easing == 7:
		return Easing(easing,t).OutCubic(t)
	elif easing == 8:
		return Easing(easing,t).InOutCubic(t)
	elif easing == 9:
		return Easing(easing,t).InQuart(t)
	elif easing == 10:
		return Easing(easing,t).OutQuart(t)
	elif easing == 11:
		return Easing(easing,t).InOutQuart(t)
	elif easing == 12:
		return Easing(easing,t).InQuint(t)
	elif easing == 13:
		return Easing(easing,t).OutQuint(t)
	elif easing == 14:
		return Easing(easing,t).InOutQuint(t)
	elif easing == 15:
		return Easing(easing,t).InSine(t)
	elif easing == 16:
		return Easing(easing,t).OutSine(t)
	elif easing == 17:
		return Easing(easing,t).InOutSine(t)
	elif easing == 18:
		return Easing(easing,t).InExpo(t)
	elif easing == 19:
		return Easing(easing,t).OutExpo(t)
	elif easing == 20:
		return Easing(easing,t).InOutExpo(t)
	elif easing == 21:
		return Easing(easing,t).InCirc(t)
	elif easing == 22:
		return Easing(easing,t).OutCirc(t)
	elif easing == 23:
		return Easing(easing,t).InOutCirc(t)
	elif easing == 24:
		return Easing(easing,t).InElastic(t)
	elif easing == 25:
		return Easing(easing,t).OutElastic(t)
	elif easing == 26:
		return Easing(easing,t).OutElasticHalf(t)
	elif easing == 27:
		return Easing(easing,t).OutElasticQuarter(t)
	elif easing == 28:
		return Easing(easing,t).InOutElastic(t)
	elif easing == 29:
		return Easing(easing,t).InBack(t)
	elif easing == 30:
		return Easing(easing,t).OutBack(t)
	elif easing == 31:
		return Easing(easing,t).InOutBack(t)
	elif easing == 32:
		return Easing(easing,t).InBounce(t)
	elif easing == 33:
		return Easing(easing,t).OutBounce(t)
	elif easing == 34:
		return Easing(easing,t).InOutBounce(t)

i = 0

totalLineNumber = 0

def calculateFrameIndex(self, time):
	if self.looptype == "LoopForever":
		return int(((time - self.activetime[0]) / self.framedelay) % (self.framecount))
	elif self.looptype == "LoopOnce":
		return (
			int(((time - self.activetime[0]) / self.framedelay))
			if time - self.activetime[0] < self.framecount * self.framedelay
			else self.framecount - 1
		)

# get osb file

parser = argparse.ArgumentParser(
	description="sb2mp4 (stole from walavouchey repo (gib meh excuse pzlpzlpzpzlpz uwu))"
)

parser.add_argument("osb_folder", help="The song folder that have osb file.")
parser.add_argument(
	"-diff",
	"--difficulty",
	help="The difficulty path that you want to render.",
	required=False,
)
parser.add_argument(
	"-w", "--width", help="The width of the video. (Default 1920)", required=False
)
parser.add_argument(
	"-he", "--height", help="The height of the video. (Default 1080)", required=False
)
parser.add_argument(
	"-f", "--fps", help="The fps of the video. (Default 30)", required=False
)
parser.add_argument(
	"-o", "--output", help="The output file name. (Default output.mp4)", required=False
)
parser.add_argument(
	"-s",
	"--start-time",
	help="The start time of the beatmap. (Default 0)",
	required=False,
)
parser.add_argument(
	"-d",
	"--duration",
	help="The duration of the beatmap. (Default end)",
	required=False,
)


files = parser.parse_args().osb_folder.strip("'\"") + "\\"
osbfile = None
for file in os.listdir(files):
	if file.endswith(".osb"):
		osbfile = file
		break
if osbfile is None:
	print("No .osb file found")
	raise
print(f"Parsing .osb file: {osbfile}")
diff = (
	parser.parse_args().difficulty
	if parser.parse_args().difficulty is not None
	else None
)
if diff:
	print(f"Parsing .osu file: {diff}")

frameW = parser.parse_args().width if parser.parse_args().width else 1920
frameH = parser.parse_args().height if parser.parse_args().height else 1080
fps = parser.parse_args().fps if parser.parse_args().fps else 30
outputFile = parser.parse_args().output if parser.parse_args().output else "output.mp4"

sb = Storyboard(
	files, ParseStoryboard(files, osbfile, diff, inDiff=True), (frameW, frameH)
)
print("Storyboard initialised")

# TODO: implement video background, improve performance
# TODO: think very hard about triggers
starttime = parser.parse_args().start_time if parser.parse_args().start_time else 0
duration = (
	pydub.utils.to_ms(parser.parse_args().duration)
	if parser.parse_args().duration
	else None
)

"""
testframe = sb.drawFrame(int(sys.argv[3]))
testframe = Image.fromarray(testframe)
testframe.show()
"""

frameCount = int(round(fps / (1000.0 / float(duration))))
with Bar(
	"Writing video...", max=frameCount, suffix="%(percent).1f%% - %(eta)ds"
) as bar:
	fourcc = cv.VideoWriter_fourcc(*"mp4v")
	writer = cv.VideoWriter("export.mp4", fourcc, fps, (frameW, frameH))
	for i in range(frameCount):
		frame = sb.drawFrame(starttime + i * 1000.0 / fps)
		frame = np.flip(frame, axis=2)
		writer.write(frame)
		bar.next()
	writer.release()
print("Generating audio...")
sb.generateAudio("export.mp3")
print("Merging audio and video...")
sp.Popen(
	f"ffmpeg -y -loglevel error -i export.mp4 -ss {starttime}ms -to {starttime + duration}ms -accurate_seek  -i export.mp3 {outputFile}"
)
print("Done")
