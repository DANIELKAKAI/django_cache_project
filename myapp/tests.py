from django.test import TestCase
from django.urls import reverse

class AppTest(TestCase):
	def text_sample(self):
		url = reverse("sample")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
	def test_index(self):
		url = reverse("index")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)