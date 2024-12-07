from .Base import BaseExtractor
from .. import ExtendedSupport

from .Instagram import Instagram
from .TikTok import TikTok
from .YouTube import YouTube
from .VK import VK

EXTRACTORS: dict[ExtendedSupport, BaseExtractor] = {
	ExtendedSupport.Instagram: Instagram,
	ExtendedSupport.TikTok: TikTok,
	ExtendedSupport.YouTube: YouTube,
	ExtendedSupport.VK: VK
}