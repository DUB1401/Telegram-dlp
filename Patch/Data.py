from Source.UI.Templates import Animation
from Source.Core.GetText import _

INTERVAL = 1.5

def GenerateStartAnimation(name: str) -> Animation:
	"""
	Генерирует стартовую анимацию мультфильма.
		name – название мультфильма.
	"""

	CartoonsStartAnimation = Animation()
	CartoonsStartAnimation.set_delay(3)
	CartoonsStartAnimation.set_interval(3)
	CartoonsStartAnimation.add_lines(_("А пока ждёте, посмотрите лучше наш мультик! 😉"))
	CartoonsStartAnimation.add_lines(name)

	return CartoonsStartAnimation