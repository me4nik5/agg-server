from django.conf import settings
from django.db import models
from django.utils import timezone

import json
from .comparators.polyphone.polycompare import *

class Thread(models.Model):
	title = models.CharField(max_length=300)
	phonograms = models.TextField()
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.title

class Article(models.Model):
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title = models.CharField(max_length=300)
	text = models.TextField()
	phonograms = models.TextField(blank=True)
	date = models.DateTimeField(default=timezone.now)
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return (self.title + ' \n' +  self.text)

	def create_phonograms(self, round_dict = 1024):
		self.phonograms = json.dumps(polyconverter(text = str(self), round_dict = round_dict))
		self.save()

	def find_thread(self, min_coef = 0.185085, round_dec = 3, round_dict = 1024):
		isThreadFound = False
		round_order = 10 ** (round_dec)
		threads = Thread.objects.all()

		if self.phonograms is '' or self.phonograms is None:
			self.create_phonograms(round_dict = round_dict)

		if threads.exists():
			phonograms = json.loads(self.phonograms)
			if type(phonograms) is dict:
				for thread in threads:
					current_phonograms = json.loads(thread.phonograms)
					coef = polycompare(phonograms, current_phonograms)
					coef = round(coef * round_order) / round_order
					if (coef >= min_coef):
						self.thread = thread
						min_coef = coef
						if not isThreadFound:
							isThreadFound = True
			else:
				return None

		if not threads.exists() or not isThreadFound:
			self.thread = Thread.objects.create(title = self.title, phonograms = self.phonograms)

		self.save()

		return self.thread


