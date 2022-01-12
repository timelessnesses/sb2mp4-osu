class Easing:
	def __init__(self,easing,t):
		def r(f, t):
			return 1 - f(1 - t)

		def io(f, t):
			return 0.5 * (f(2 * t) if t < 0.5 else (2 - f(2 - 2 * t)))

		self.Linear = lambda x: x
		self.InQuad = lambda x: x ** 2
		self.OutQuad = lambda x: r(InQuad, x)
		self.Out = lambda x: OutQuad(x)
		self.In = lambda x: InQuad(x)
		self.InOutQuad = lambda x: io(InQuad, x)
		self.InCubic = lambda x: x ** 3
		self.OutCubic = lambda x: r(InCubic, x)
		self.InOutCubic = lambda x: io(InCubic, x)
		self.InQuart = lambda x: x ** 4
		self.OutQuart = lambda x: r(InQuart, x)
		self.InOutQuart = lambda x: io(InQuart, x)
		self.InQuint = lambda x: x ** 5
		self.OutQuint = lambda x: r(InQuint, x)
		self.InOutQuint = lambda x: io(InQuint, x)
		self.InSine = lambda x: 1 - math.cos(x * math.pi / 2)
		self.OutSine = lambda x: r(InSine, x)
		self.InOutSine = lambda x: io(InSine, x)
		self.InExpo = lambda x: 2 ** (10 * (x - 1))
		self.OutExpo = lambda x: r(InExpo, x)
		self.InOutExpo = lambda x: io(InExpo, x)
		self.InCirc = lambda x: 1 - math.sqrt(1 - x * x)
		self.OutCirc = lambda x: r(InCirc, x)
		self.InOutCirc = lambda x: io(InCirc, x)
		self.OutElastic = (
			lambda x: 2 ** (-10 * x) * math.sin((x - 0.075) * (2 * math.pi) / 0.3) + 1
		)
		self.InElastic = lambda x: r(OutElastic, x)
		self.OutElasticHalf = (
			lambda x: 2 ** (-10 * x) * math.sin((0.5 * x - 0.075) * (2 * math.pi) / 0.3) + 1
		)
		self.OutElasticQuarter = (
			lambda x: 2 ** (-10 * x) * math.sin((0.25 * x - 0.075) * (2 * math.pi) / 0.3)
			+ 1
		)
		self.InOutElastic = lambda x: io(InElastic, x)
		self.InBack = lambda x: x ** 2 * ((1.70158 + 1) * x - 1.70158)
		self.OutBack = lambda x: r(InBack, x)
		self.InOutBack = lambda x: io(InBack, x)
		self.OutBounce = (
			lambda x: 7.5625 * x ** 2
			if x < 1 / 2.75
			else 7.5625 * (x - (1.5 / 2.75)) * (x - (1.5 / 2.75)) + 0.75
			if x < 2 / 2.75
			else 7.5625 * (x - (2.25 / 2.75)) * (x - (2.25 / 2.75)) + 0.9375
			if x < 2.5 / 2.75
			else 7.5625 * (x - (2.625 / 2.75)) * (x - (2.625 / 2.75)) + 0.984375
		)
		self.InBounce = lambda x: r(OutBounce, x)
		self.InOutBounce = lambda x: io(OutBounce, x)