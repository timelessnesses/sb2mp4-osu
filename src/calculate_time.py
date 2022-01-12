def calculateActivetime(self):
	return (
		(
			min(
				min([event.starttime for event in self.events])
				if len(self.events) > 0
				else float("+inf"),
				min([loop.starttime for loop in self.loops if len(loop.events) > 0])
				if len([loop for loop in self.loops if len(loop.events) > 0]) > 0
				else float("+inf"),
			),
			max(
				max([event.endtime for event in self.events])
				if len(self.events) > 0
				else float("-inf"),
				max([loop.endtime for loop in self.loops if len(loop.events) > 0])
				if len([loop for loop in self.loops if len(loop.events) > 0]) > 0
				else float("-inf"),
			),
		)
		if len(self.events) > 0
		or (len([0 for loop in self.loops if len(loop.events) > 0]) > 0)
		else None
	)

