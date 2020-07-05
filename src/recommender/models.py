from django.db import models, transaction
from django.urls import reverse

# Create your models here.
class MovieGenre(models.Model):
	title = models.CharField(max_length=100, null=False, unique=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("recommender:genre_detail", kwargs={"id": self.id})

class Algorithm(models.Model):
	name = models.CharField(max_length=100, null=False, unique=True)
	description = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("recommender:algo_detail", kwargs={"id": self.id})


class Dataset(models.Model):
	name = models.CharField(max_length=200, unique=True)
	size = models.PositiveIntegerField()
	category = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("recommender:dataset_detail", kwargs={"id": self.id})


class Token(models.Model):
	name = models.CharField(max_length=40, blank=False, null=False, unique=True)
	valid = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("recommender:token_detail", kwargs={"id": self.id})


class User(models.Model):
	user_id = models.PositiveIntegerField(null=True)
	name = models.CharField(max_length=200, null=True)
	account = models.CharField(max_length=200, null=True, unique=True)
	token = models.OneToOneField('Token', on_delete=models.CASCADE, blank=True, null=True)
	online_user = models.BooleanField(default=False)
	dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		if self.token != None:
			return self.token.name
		else:
			return str(self.user_id)+ " of Dataset " + str(self.dataset)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user_id', 'dataset'], name='unique_user_ds2')
		]

class Item(models.Model):
	item_id = models.PositiveIntegerField(null=True)
	name = models.CharField(max_length=200)
	dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE)
	genres = models.ManyToManyField('MovieGenre', related_name='items')
	imdb_id = models.PositiveIntegerField(null=True)
	amount_ratings = models.PositiveIntegerField(null=True, blank=True)
	poster = models.ImageField(upload_to = 'posters', height_field=None, width_field=None, max_length=200, null=True)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("study:rating_detail", kwargs={"id": self.id})

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['item_id', 'dataset'], name='unique_item_ds2')
		]

class Rating(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	item = models.ForeignKey('Item', on_delete=models.CASCADE)
	rating = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user', 'item'], name='unique_rating2')
		]


class Reclist(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE) # models.IntegerField() # FK
	algorithm = models.ForeignKey('Algorithm', on_delete=models.CASCADE) # models.IntegerField() # FK
	length = models.PositiveSmallIntegerField()
	items = models.ManyToManyField('Item', through='ReclistItem', related_name='reclists') # Menge FKs

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user', 'algorithm', 'length'], name='unique_recl_user2')
		]

	def get_absolute_url(self):
		return reverse("recommender:reclist_detail", kwargs={"id": self.id})

class ReclistItem(models.Model):
	reclist = models.ForeignKey('Reclist', on_delete=models.CASCADE, related_name='reclist_items')
	item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='reclist_items')
	prediction = models.DecimalField(max_digits=20, decimal_places=10)
	number = models.PositiveIntegerField()

	class Meta:
		ordering = ('number',)

class Evaluation(models.Model):
	study = models.ForeignKey('Study', on_delete=models.CASCADE)
	reclist = models.ForeignKey('Reclist', on_delete=models.CASCADE) # models.IntegerField() # FK
	user = models.ForeignKey('User', on_delete=models.CASCADE) # models.IntegerField() # FK
	accuracy_mae = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	accuracy_mse = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	accuracy_rmse = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	non_rating_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	utility = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	serendipity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	novelty = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	diversity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	unexpectedness = models.DecimalField(max_digits=10, decimal_places=2, null=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['study', 'reclist', 'user'], name='unique_study_eval')
		]

	def get_absolute_url(self):
		return reverse("recommender:evaluation_detail", kwargs={"id": self.id})

class Study(models.Model):
	name = models.CharField(max_length=200, unique=True)
	dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE)
	description = models.TextField(blank=True, null=True)
	active = models.BooleanField(default=False)
	algorithms = models.ManyToManyField('Algorithm', related_name='studies') # Menge FKs
	reclist_length = models.PositiveSmallIntegerField()

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("recommender:study_detail", kwargs={"id": self.id})

	def save(self, *args, **kwargs):
		if not self.active:
			return super(Study, self).save(*args, **kwargs)
		with transaction.atomic():
			Study.objects.filter(active=True).update(active=False)
			return super(Study, self).save(*args, **kwargs)
