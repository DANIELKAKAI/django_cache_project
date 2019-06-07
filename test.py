from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify

# Create your models here.

CATEGORIES = (
('tech-and-gadgets', 'tech & gadgets'), ('fashion-and-style', 'fashion & style'), ('home-and-living', 'home & living'))


class Author(models.Model):
    name = models.CharField(max_length=50)
    about = models.TextField(max_length=1000)
    author_image = models.ImageField(upload_to='images')
    author_banner = models.ImageField(upload_to='images')
    facebook_link = models.CharField(max_length=100)
    twitter_link = models.CharField(max_length=100)
    ig_link = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, default="")
    preview = models.TextField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    body = models.TextField(max_length=10000)
    views = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)
    banner_image = models.ImageField(upload_to='images')
    tag = models.ManyToManyField(Tag, verbose_name="post tags")
    image_1 = models.ImageField(upload_to='images', default='images/image.png', blank=True)
    image_2 = models.ImageField(upload_to='images', default='images/image.png', blank=True)
    image_3 = models.ImageField(upload_to='images', default='images/image.png', blank=True)
    image_4 = models.ImageField(upload_to='images', default='images/image.png', blank=True)
    image_5 = models.ImageField(upload_to='images', default='images/image.png', blank=True)
    content = RichTextUploadingField(blank=True, null=True)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
    def __str__(self):
        return self.title


class Subscribers(models.Model):
    email = models.EmailField(max_length=100)
    def __str__(self):
        return self.email
    class Meta:
        verbose_name_plural = "Subscribers"
