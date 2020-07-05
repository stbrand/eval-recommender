from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.views import View
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as DjUser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import *
from .forms import *
from django.forms import formset_factory

import os, csv, io, secrets

from collections import defaultdict
from surprise import Reader, Dataset as SurDataset
from surprise import SVD, SVDpp, SlopeOne, NMF, NormalPredictor
from surprise import KNNBaseline, KNNBasic, KNNWithMeans
from surprise import BaselineOnly, CoClustering


#####################
# HOME REGISTER
#####################

# function based view
def home_view(request, *args, **kwargs):
	return render(request, "recommender/home.html", {})

def register(request, *args, **kwargs):
	if request.method == "POST":
		# get entries from the django built-in UserCreationForm in template
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get("username")
			messages.success(request, f'Account created for {username}!')
			return redirect("recommender:home")
	else:
		# instantiate the empty django built-in UserCreationForm in template
		form = UserCreationForm()
	return render(request, "recommender/register.html", {'form': form})


#####################
# TOKEN VIEWS
#####################

# class based view
class TokenListView(ListView):
	template_name = "recommender/token_list.html"
	queryset = Token.objects.all().order_by("id")


# not used, just for deleting tokens
class TokenDetailView(DetailView):
	template_name = "recommender/token_detail.html"
	queryset = Token.objects.all()

	def get_object(self):
		id = self.kwargs.get("id")
		return get_object_or_404(Token, id=id)


@method_decorator(login_required, name="dispatch")
class TokenCreateView(CreateView):
	template_name = "recommender/token_create.html"
	form_class = TokenForm
	queryset = Token.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:tokens_list")


@method_decorator(login_required, name="dispatch")
class TokenDeleteView(DeleteView):
	template_name = "recommender/token_delete.html"
	queryset = Token.objects.all()

	def get_success_url(self):
		return reverse("recommender:tokens_list")


@login_required
def create_tokens(request, *args, **kwargs):
	# instantiate ten empty forms in template
	TokenFormSet = formset_factory(TokenForm, extra=10)
	if request.method == 'POST':
		# get data from forms in template
		formset = TokenFormSet(request.POST, request.FILES)
		if formset.is_valid():
			for form in formset:
				if form.is_valid() and form.cleaned_data != {}:
					form.save()
			return redirect("recommender:tokens_list")
	else:
		# instantiate empty form in template
		formset = TokenFormSet()
	return render(request, 'recommender/tokens_create.html', {'formset': formset})


@login_required
def generate_tokens(request, *args, **kwargs):
	if(request.GET.get("token_btn")):
		# get data from form in template
		# entry: how many tokens
		often = (int(request.GET.get('how_many')))
		for i in range(often):
			# generate secure random numbers, eight-part
			tok = (''.join([secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for i in range(8)]))
			# create and save token to database
			Token.objects.create(name=tok)
		return redirect("recommender:tokens_list")
	return render(request, 'recommender/token_generate.html', {})


#####################
# ALGORITHM VIEWS
#####################

class AlgorithmListView(ListView):
	template_name = "recommender/algorithm_list.html"
	queryset = Algorithm.objects.all().order_by("name")


class AlgorithmDetailView(DetailView):
	template_name = "recommender/algorithm_detail.html"
	queryset = Algorithm.objects.all()

	def get_object(self):
		id = self.kwargs.get("id")
		return get_object_or_404(Algorithm, id=id)


@method_decorator(login_required, name="dispatch")
class AlgorithmCreateView(CreateView):
	template_name = "recommender/algorithm_create.html"
	form_class = AlgorithmForm
	queryset = Algorithm.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:algorithms_list")


@method_decorator(login_required, name="dispatch")
class AlgorithmUpdateView(UpdateView):
	template_name = "recommender/algorithm_create.html"
	form_class = AlgorithmForm
	queryset = Algorithm.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:algorithms_list")


@method_decorator(login_required, name="dispatch")
class AlgorithmDeleteView(DeleteView):
	template_name = "recommender/algorithm_delete.html"
	queryset = Algorithm.objects.all()

	def get_success_url(self):
		return reverse("recommender:algorithms_list")


#####################
# GENRE VIEWS
#####################


class GenreListView(ListView):
	template_name = "recommender/genre_list.html"
	queryset = MovieGenre.objects.all().order_by("title")


class GenreDetailView(DetailView):
	template_name = "recommender/genre_detail.html"
	queryset = MovieGenre.objects.all()

	def get_object(self):
		id = self.kwargs.get("id")
		return get_object_or_404(Algorithm, id=id)


@method_decorator(login_required, name="dispatch")
class GenreCreateView(CreateView):
	template_name = "recommender/genre_create.html"
	form_class = GenreForm
	queryset = MovieGenre.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:genres_list")


@method_decorator(login_required, name="dispatch")
class GenreUpdateView(UpdateView):
	template_name = "recommender/genre_create.html"
	form_class = GenreForm
	queryset = MovieGenre.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:genres_list")


@method_decorator(login_required, name="dispatch")
class GenreDeleteView(DeleteView):
	template_name = "recommender/genre_delete.html"
	queryset = MovieGenre.objects.all()

	def get_success_url(self):
		return reverse("recommender:genres_list")


#####################
# STUDY VIEWS
#####################


class StudyListView(ListView):
	template_name = "recommender/study_list.html"
	queryset = Study.objects.all().order_by("id")


class StudyDetailView(DetailView):
	template_name = "recommender/study_detail.html"
	queryset = Study.objects.all()

	def get_object(self):
		my_id = self.kwargs.get("id")
		return get_object_or_404(Study, id=my_id)


@method_decorator(login_required, name="dispatch")
class StudyCreateView(CreateView):
	template_name = "recommender/study_create.html"
	form_class = StudyForm
	queryset = Study.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:studies_list")


@method_decorator(login_required, name="dispatch")
class StudyUpdateView(UpdateView):
	template_name = "recommender/study_create.html"
	form_class = StudyForm
	queryset = Study.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:studies_list")


@method_decorator(login_required, name="dispatch")
class StudyDeleteView(DeleteView):
	template_name = "recommender/study_delete.html"
	queryset = Study.objects.all()

	def get_success_url(self):
		return reverse("recommender:studies_list")


@login_required
def study_active_view(request, *args, **kwargs):
	# instantiate empty form in template
	form = StudyFilterForm()
	# context, hand form over to template
	context = {
		'form': form,
	}
	if request.method == "POST":
		# get entry from form in template, choose study
		form = StudyFilterForm(request.POST)

		if form.is_valid():
			# get chosen study and set it on true, save changes
			study = form.cleaned_data['study']
			study.active = True
			study.save()

			# context, hand study and form over to template
			context = {
				'study': study,
				'form': form,
			}
			return render(request, "recommender/study_active.html", context)

	return render(request, "recommender/study_active.html", context)



#####################
# DATASET VIEWS
#####################


class DatasetListView(ListView):
	template_name = "recommender/dataset_list.html"
	queryset = Dataset.objects.all().order_by("id")


class DatasetDetailView(DetailView):
	template_name = "recommender/dataset_detail.html"
	queryset = Dataset.objects.all()

	def get_object(self):
		id = self.kwargs.get("id")
		return get_object_or_404(Dataset, id=id)


@method_decorator(login_required, name="dispatch")
class DatasetCreateView(CreateView):
	template_name = "recommender/dataset_create.html"
	form_class = DatasetForm
	queryset = Dataset.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:datasets_list")


@method_decorator(login_required, name="dispatch")
class DatasetUpdateView(UpdateView):
	template_name = "recommender/dataset_create.html"
	form_class = DatasetForm
	queryset = Dataset.objects.all()

	def form_valid(self, form):
		return super().form_valid(form)

	def get_success_url(self):
		return reverse("recommender:datasets_list")


@method_decorator(login_required, name="dispatch")
class DatasetDeleteView(DeleteView):
	template_name = "recommender/dataset_delete.html"
	queryset = Dataset.objects.all()

	def get_success_url(self):
		return reverse("recommender:datasets_list")


#####################
# USER VIEWS
#####################


# show online users
class UserListView(ListView):
	template_name = "recommender/users_online_list.html"
	queryset = User.objects.filter(online_user=True).order_by("id")


def users_view(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# get online users, actually no longer needed in current version
	online_users = User.objects.filter(dataset=None)

	# context, hand users and form over to template
	context = {
		'online_users': online_users,
		'form': form,
	}

	if request.method == "POST":
		# get entry from form in template
		form = DatasetFilterForm(request.POST)

		if form.is_valid():
			# get chosen dataset
			dataset = form.cleaned_data['dataset']
			# get users of chosen dataset
			users = User.objects.filter(dataset=dataset).order_by("id")
			# get amount of users of chosen dataset and hand over to template
			amount = User.objects.filter(dataset=dataset).count()

			# context, hand over to template
			context = {
				'dataset': dataset,
				'online_users': online_users,
				'users': users,
				'form': form,
				'amount': amount
			}
			return render(request, "recommender/users.html", context)

	return render(request, "recommender/users.html", context)


# actually no longer needed in current version
@login_required
def generate_users(request, *args, **kwargs):
	# instantiate empty form in template
	form = UserCreateForm()
	if request.method == "POST":
		# get entries from form in template
		form = UserCreateForm(request.POST)

		if form.is_valid():
			# get dataset and number of users to generate
			dataset = form.cleaned_data['dataset']
			often = form.cleaned_data['number']
			# create and save users to database
			for i in range(often):
				user_id=i+1
				try:
					user = User.objects.get(user_id=user_id,dataset=dataset)
				except User.DoesNotExist:
					User.objects.create(user_id=user_id,dataset=dataset)
			# instantiate empty form in template
			form = UserCreateForm()
		return redirect("recommender:users_list")

	return render(request, 'recommender/users_generate.html', {'form':form})


#####################
# ITEM VIEWS
#####################


def items_view(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()

	# context, hand form over to template
	context = {
		'form': form,
	}

	if request.method == "POST":
		# get entry from form in template
		form = DatasetFilterForm(request.POST)

		if form.is_valid():
			# get chosen dataset, items and amount of items in dataset
			dataset = form.cleaned_data['dataset']
			items = Item.objects.filter(dataset=dataset).order_by("id")
			amount = Item.objects.filter(dataset=dataset).count()

			# hand over to template, items ordered
			context = {
				'dataset': dataset,
				'items': items,
				'form': form,
				'amount': amount
			}
			return render(request, "recommender/items.html", context)

	return render(request, "recommender/items.html", context)


#####################
# EVALUATION VIEWS
#####################

# class based view
class EvaluationListView(ListView):
	template_name = "recommender/evaluations_list.html"
	queryset = Evaluation.objects.all().order_by("id")


class EvaluationDetailView(DetailView):
	template_name = "recommender/evaluation_detail.html"
	queryset = Evaluation.objects.all()

	def get_object(self):
		id = self.kwargs.get("id")
		return get_object_or_404(Evaluation, id=id)


def evaluations_table_view(request, *args, **kwargs):
	# instantiate empty form in template
	form = StudyFilterForm()

	# context, hand form over to template
	context = {
		'form': form,
	}
	if request.method == "POST":
		# get entries from form in template
		form = StudyFilterForm(request.POST)

		if form.is_valid():
			# get study and evaluations of study (ordered by id)
			study = form.cleaned_data['study']
			evals = Evaluation.objects.filter(study=study).order_by("id")

			# hand over to template
			context = {
				'study': study,
				'evals': evals,
				'form': form,
			}
			return render(request, "recommender/evaluations_table.html", context)

	return render(request, "recommender/evaluations_table.html", context)


#####################
# RECLIST VIEWS
#####################

# class based view
class ReclistListView(ListView):
	template_name = "recommender/reclist_list.html"
	queryset = Reclist.objects.all().order_by("id")


class ReclistDetailView(DetailView):
	template_name = "recommender/reclist_detail.html"
	queryset = Reclist.objects.all()

	def get_object(self):
		id = self.kwargs.get("id")
		return get_object_or_404(Reclist, id=id)


@login_required
def reclists_existing(request, *args, **kwargs):
	# empty set
	my_set = set()
	# for all recommendation lists, save dataset, algorithm and length in set
	for reclist in Reclist.objects.all():
		tuple = (reclist.user.dataset, reclist.algorithm, reclist.length)
		my_set.add(tuple)

	# make list out of set and hand it over to template
	my_list = list(my_set)
	# hand list over to template
	context = {
		'my_list':my_list
	}

	return render(request, "recommender/reclists_existing.html", context)


@login_required
def reclist_view(request, *args, **kwargs):
	if request.method == "GET":
		# instantiate empty forms in template
		d_form = DatasetFilterForm()
		a_form = AlgorithmMultiForm()
		l_form = LengthMultiForm()

		# hand DatasetFilterForm over to template
		context = {
			'd_form': d_form,
		}

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			d_form = DatasetFilterForm(request.POST)
			if d_form.is_valid():
				# get dataset from form and save id in session variable
				dataset = d_form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				# instantiate empty form in template
				a_form = AlgorithmMultiForm()

				# hand chosen dataset and a_form over to template
				context = {
					'dataset': dataset,
					'a_form': a_form,
				}
				return render(request, "recommender/reclistitems.html", context)
		if request.POST.get("algo_btn"):
			# get entries from form in template
			a_form = AlgorithmMultiForm(request.POST)
			if a_form.is_valid():
				# get algorithms from form and save list in session variable
				algos = a_form.cleaned_data['algorithm']
				algo_list = []
				for algo in algos:
					algo_list.append(algo.id)
				request.session['algorithm'] = algo_list
				request.session.modified = True

				# get dataset from session variable
				dataset = Dataset.objects.get(id=request.session['dataset_id'])

				# instantiate empty form in template
				l_form = LengthMultiForm()

				# hand chosen dataset and algorithms and l_form over to template
				context = {
					'dataset': dataset,
					'algos': algos,
					'l_form': l_form,
				}
				return render(request, "recommender/reclistitems.html", context)
		if request.POST.get("length_btn"):
			# get entries from form in template
			l_form = LengthMultiForm(request.POST)
			if l_form.is_valid():
				# get lengths from form
				lengths = l_form.cleaned_data['length']

			# get recommendation lists, filtered by users of chosen dataset, chosen algorithms and chosen lenghts
			reclists = Reclist.objects.filter(user__in=User.objects.filter(dataset=request.session['dataset_id']), algorithm__in=Algorithm.objects.filter(id__in=request.session['algorithm']), length__in=lengths).order_by("id")
			dataset = Dataset.objects.get(id=request.session['dataset_id'])
			algos = Algorithm.objects.filter(id__in=request.session['algorithm'])

			# hand over to template
			context = {
				'dataset': dataset,
				'algos': algos,
				'lengths': lengths,
				'reclists': reclists,
			}
			return render(request, "recommender/reclistitems.html", context)

	return render(request, "recommender/reclistitems.html", context)


##########################################
# SURPRISE / CREATE RECOMMENDATION LISTS
##########################################

# Create Reclists / Make Predictions
@login_required
def surprise_predict(request, *args, **kwargs):
	# instantiate empty forms in template
	d_form = DatasetFilterForm()
	a_form = AlgorithmFilterForm()
	f_form = FilePathForm()

	# context, hand forms over to template
	context = {
		'd_form':d_form,
		'a_form':a_form,
		'f_form':f_form
	}

	if request.method == "POST":
		# get entries from forms in template
		d_form = DatasetFilterForm(request.POST)
		a_form = AlgorithmFilterForm(request.POST)
		f_form = FilePathForm(request.POST)
		if d_form.is_valid():
			dataset = d_form.cleaned_data['dataset']
		if a_form.is_valid():
			algorithm = a_form.cleaned_data['algorithm']
		if f_form.is_valid():
			path = f_form.cleaned_data['path_for_rating_file']
			line_format = f_form.cleaned_data['line_format']
			delimiter = f_form.cleaned_data['delimiter']
			skip_lines = f_form.cleaned_data['skip_lines']

		# get length from form in template
		length = request.POST.get('number')

		# call function (see below) and predict ratings with with the desired attributes
		predict_ratings(dataset, algorithm, int(length), path, line_format, delimiter, int(skip_lines))

		# instantiate empty forms in template
		d_form = DatasetFilterForm()
		a_form = AlgorithmFilterForm()
		f_form = FilePathForm()
		return redirect("recommender:reclists_existing")

	return render(request, "recommender/surprise_predict.html", context)


#####################
# RATING VIEWS
#####################

def ratings_view(request, *args, **kwargs):
	if request.method == "GET":
		# instantiate empty forms in template
		d_form = DatasetFilterForm()
		u_form = UserFilterForm(dataset=None)

		# context, hand form over to template
		context = {
			'd_form': d_form,
		}

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entry from form in template
			d_form = DatasetFilterForm(request.POST)

			if d_form.is_valid():
				# get dataset from form and save id in session variable
				dataset = d_form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				# instantiate form in template with dataset information
				u_form = UserFilterForm(dataset=dataset)
				# hand chosen dataset and UserFilterForm over to template
				context = {
					'dataset': dataset,
					'u_form': u_form,
				}
				return render(request, "recommender/ratings.html", context)
		if request.POST.get("user_btn"):
			# get user_id from form in template
			user = request.POST.get("user_id")
			# get ratings by user id
			ratings = Rating.objects.filter(user=user).order_by("id")
			# get user by user id
			user_obj = User.objects.get(id=user)
			rating_user = user_obj.user_id
			# count ratings
			amount = ratings.count()
			# get dataset from session variable
			dataset = Dataset.objects.get(id=request.session['dataset_id'])

			# hand over to template
			context = {
				'dataset': dataset,
				'rating_user': rating_user,
				'ratings': ratings,
				'amount': amount,
			}
			return render(request, "recommender/ratings.html", context)

	return render(request, "recommender/ratings.html", context)


@login_required
def ratings_online_users(request, *args, **kwargs):
	# get all online users
	users = User.objects.filter(online_user=True)
	# get all ratings of all online users
	ratings = Rating.objects.filter(user__in=users).order_by("id")

	# empty lists
	user_amount_list = []
	user_study_list= []
	user_user_list = []
	users_with_ratings = []

	# for all online users
	for user in users:
		# get the ratings of recommendation lists (evaluations)
		evals=Evaluation.objects.filter(user=user)
		# empty sets
		studies = set()
		offline_users = set()
		# for all evaluations of the online user
		for eval in evals:
			# add study to set
			studies.add(eval.study)
			# add mapped offline user to set
			offline_users.add(eval.reclist.user)
		if len(studies) > 0:
			# if such studies exist, store user and study tuples in list
			user_study = (user, studies.pop())
			user_study_list.append(user_study)
		if len(offline_users) > 0:
			# if such mapped_users exist, store user and mapped user tuples in list
			user_user = (user, offline_users.pop())
			user_user_list.append(user_user)
		# get ratings and amount of ratings of online user
		user_ratings = Rating.objects.filter(user=user)
		amount = user_ratings.count()
		if amount > 0:
			# if ratings exist, store user in list
			users_with_ratings.append(user)
		# store user and amount of ratings_view tuples in list
		user_amount = (user, amount)
		user_amount_list.append(user_amount)

	# hand user, ratings and all the lists over to template
	context = {
		'users': users,
		'ratings': ratings,
		'user_amount_list': user_amount_list,
		'user_study_list': user_study_list,
		'user_user_list': user_user_list,
		'users_with_ratings': users_with_ratings
	}

	return render(request, "recommender/ratings_online_users.html", context)


#################
# UPLOAD VIEWS
#################

# upload landing page
@login_required
def upload_central(request, *args, **kwargs):
	return render(request, 'recommender/upload_central.html', {})


############################################################
# UPLOAD MovieLens Latest Small, Latest Full, 20M, 25M
############################################################

@login_required
def movie_upload(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'MOVIE UPLOAD',
		'example': 'Datasets e.g.: MovieLens Latest Small, MovieLens Latest Full, MovieLens 25M Dataset, MovieLens 20M Dataset',
		'order': 'Order of the CSV should be a comma separated list of format "movieId,title,genres" (genres are separated by pipe: "|")',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entry from form in template
			form = DatasetFilterForm(request.POST)

			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'MOVIE UPLOAD',
					'example': 'Datasets e.g.: MovieLens Latest Small, MovieLens Latest Full, MovieLens 25M Dataset, MovieLens 20M Dataset',
					'order': 'Order of the CSV should be a comma separated list of format "movieId,title,genres" (genres are separated by pipe: "|")',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a csv file
	if not csv_file.name.endswith('.csv'):
		messages.error(request, 'THIS IS NOT A CSV FILE')

	data_set = csv_file.read().decode('UTF-8')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)
	# for all the lines in dataset file: create and save (or update) item objects
	for column in csv.reader(io_string, delimiter=',', quotechar='"'):
		obj, created = Item.objects.update_or_create(
			item_id=column[0],
			name=column[1],
			dataset=dataset
		)

		# array for genres
		array=column[2].split("|")

		i=0
		for i in range(len(array)):
			try:
				# add all the genres to item object, if genre exists in database
				obj.genres.add(MovieGenre.objects.get(title=array[i]))
			except MovieGenre.DoesNotExist:
				pass

	context = {}
	return render(request, template, context)


@login_required
def rating_upload(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'RATING UPLOAD',
		'example': 'Datasets e.g.: MovieLens Latest Small, MovieLens Latest Full, MovieLens 25M Dataset, MovieLens 20M Dataset',
		'order': 'Order of the CSV should be a comma separated list of format "userId,movieId,rating,(...)"',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			form = DatasetFilterForm(request.POST)

			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'RATING UPLOAD',
					'example': 'Datasets e.g.: MovieLens Latest Small, MovieLens Latest Full, MovieLens 25M Dataset, MovieLens 20M Dataset',
					'order': 'Order of the CSV should be a comma separated list of format "userId,movieId,rating,(...)"',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a csv file
	if not csv_file.name.endswith('.csv'):
		messages.error(request, 'THIS IS NOT A CSV FILE')

	data_set = csv_file.read().decode('UTF-8')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)

	# save the reader in a list, to use it twice subsequently
	reader = csv.reader(io_string, delimiter=',', quotechar='"')
	reader_list = list(reader)

	# find out how many users there are in the dataset, save the number in max
	max = 0
	for column in reader_list:
		if int(column[0]) > max:
			max = int(column[0])

	# create users in database (from user_id=1 to user_id=max), if they do not exist already
	for i in range(max):
		user_id=i+1
		try:
			user = User.objects.get(user_id=user_id,dataset=dataset)
		except User.DoesNotExist:
			User.objects.create(user_id=user_id,dataset=dataset)

	# for all the lines in dataset file: create and save (or update) rating objects
	for column in reader_list:
		try:
			obj, created = Rating.objects.update_or_create(
				user=User.objects.get(user_id=column[0], dataset=dataset),
				item=Item.objects.get(item_id=column[1], dataset=dataset),
				rating=column[2]
			)
		except (Item.DoesNotExist,User.DoesNotExist):
			pass

	# calculate and save amount of ratings for each item (see below)
	amount_ratings_dataset(dataset=dataset)

	context = {}
	return render(request, template, context)


@login_required
def link_upload(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'LINK UPLOAD',
		'example': 'Datasets e.g.: MovieLens Latest Small, MovieLens Latest Full, MovieLens 25M Dataset, MovieLens 20M Dataset',
		'order': 'Order of the CSV should be a comma separated list of format "movieId,imdbId,(...)"',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			form = DatasetFilterForm(request.POST)

			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'LINK UPLOAD',
					'example': 'Datasets e.g.: MovieLens Latest Small, MovieLens Latest Full, MovieLens 25M Dataset, MovieLens 20M Dataset',
					'order': 'Order of the CSV should be a comma separated list of format  "movieId,imdbId,(...)"',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a csv file
	if not csv_file.name.endswith('.csv'):
		messages.error(request, 'THIS IS NOT A CSV FILE')

	data_set = csv_file.read().decode('UTF-8')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)

	# for all the lines in dataset file: get desired item object and add imdb_id
	for column in csv.reader(io_string, delimiter=',', quotechar='"'):
		try:
			obj=Item.objects.get(item_id=column[0], dataset=dataset)
			obj.imdb_id=column[1]
			obj.save()
		except Item.DoesNotExist:
			pass

	context = {}
	return render(request, template, context)



####################################
# UPLOAD MovieLens 1M, 10M
####################################


@login_required
def movie_upload_1M_10M(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'MOVIE UPLOAD',
		'example': 'Datasets e.g.: MovieLens 1M Dataset, MovieLens 10M Dataset',
		'order': 'Order of the .DAT- OR .CSV-FILE should be a double colon ("::") separated list of format "movieId::title::genres" (genres are separated by pipe: "|")',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			form = DatasetFilterForm(request.POST)

			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'MOVIE UPLOAD',
					'example': 'Datasets e.g.: MovieLens 1M Dataset, MovieLens 10M Dataset',
					'order': 'Order of the .DAT- OR .CSV-FILE should be a double colon ("::") separated list of format "movieId::title::genres" (genres are separated by pipe: "|")',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a .csv or .dat file
	if not (csv_file.name.endswith('.dat') or csv_file.name.endswith('.csv')):
		messages.error(request, 'THIS IS NOT A .DAT- OR .CSV-FILE')

	data_set = csv_file.read().decode('UTF-8')
	# replace delimiter '::' with ':', because delimiter in csv.reader has to be single digit
	data_set = data_set.replace('::', ':')
	# optional: replace 'Children's' with 'Children', because 'Children's' isn't in database
	data_set = data_set.replace('Children\'s', 'Children')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)

	# for all the lines in dataset file: create and save (or update) item object
	for column in csv.reader(io_string, delimiter=':', quotechar='"'):
		obj, created = Item.objects.update_or_create(
			item_id=column[0],
			name=column[1],
			dataset=dataset
		)

		# array for genres
		array=column[2].split("|")

		for i in range(len(array)):
			try:
				# add all the genres to item object, if genre exists in database
				obj.genres.add(MovieGenre.objects.get(title=array[i]))
			except MovieGenre.DoesNotExist:
				pass

	context = {}
	return render(request, template, context)


@login_required
def rating_upload_1M_10M(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'RATING UPLOAD',
		'example': 'Datasets e.g.: MovieLens 1M Dataset, MovieLens 10M Dataset',
		'order': 'Order of the .DAT- OR .CSV-FILE should be a double colon ("::") separated list of format "userId::movieId::rating,(...)"',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			form = DatasetFilterForm(request.POST)

			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'RATING UPLOAD',
					'example': 'Datasets e.g.: MovieLens 1M Dataset, MovieLens 10M Dataset',
					'order': 'Order of the .DAT- OR .CSV-FILE should be a double colon ("::") separated list of format "userId::movieId::rating,(...)"',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a .csv or a .dat file
	if not (csv_file.name.endswith('.dat') or csv_file.name.endswith('.csv')):
		messages.error(request, 'THIS IS NOT A .DAT- OR .CSV-FILE')

	data_set = csv_file.read().decode('UTF-8')
	# replace delimiter '::' with ':', because delimiter in csv.reader has to be single digit
	data_set = data_set.replace('::', ':')
	# optional: replace 'Children's' with 'Children', because 'Children's' isn't in database
	data_set = data_set.replace('Children\'s', 'Children')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)

	# save the reader in a list, to use it twice subsequently
	reader = csv.reader(io_string, delimiter=':', quotechar='"')
	reader_list = list(reader)

	# find out how many users there are in the dataset, save the number in max
	max = 0
	for column in reader_list:
		if int(column[0]) > max:
			max = int(column[0])

	# create users in database (from user_id=1 to user_id=max), if they do not exist already
	for i in range(max):
		user_id=i+1
		try:
			user = User.objects.get(user_id=user_id,dataset=dataset)
		except User.DoesNotExist:
			User.objects.create(user_id=user_id,dataset=dataset)

	# for all the lines in dataset file: create and save (or update) rating object
	for column in reader_list:
		try:
			obj, created = Rating.objects.update_or_create(
				user=User.objects.get(user_id=column[0], dataset=dataset),
				item=Item.objects.get(item_id=column[1], dataset=dataset),
				rating=column[2]
			)
		except (Item.DoesNotExist,User.DoesNotExist):
			pass

	# calculate and save amount of ratings for each item (see below)
	amount_ratings_dataset(dataset=dataset)

	context = {}
	return render(request, template, context)




###############################
# UPLOAD MovieLens 100K
###############################


@login_required
def movie_upload_100K(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()
	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'MOVIE UPLOAD',
		'example': 'Dataset e.g.: MovieLens 100K Dataset',
		'order': 'Order of the .ITEM- OR .CSV-FILE should be a "|" separated list of format "movieId | movie title | release date | video release date | IMDb URL | unknown | Action | Adventure | Animation | Children | Comedy | Crime | Documentary | Drama | Fantasy | Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi | Thriller | War | Western |" (for genres: 1 if TRUE, 0 else)',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			form = DatasetFilterForm(request.POST)

			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'MOVIE UPLOAD',
					'example': 'Dataset e.g.: MovieLens 100K Dataset',
					'order': 'Order of the .ITEM- OR .CSV-FILE should be a "|" separated list of format "movieId | movie title | release date | video release date | IMDb URL | unknown | Action | Adventure | Animation | Children | Comedy | Crime | Documentary | Drama | Fantasy | Film-Noir | Horror | Musical | Mystery | Romance | Sci-Fi | Thriller | War | Western |" (for genres: 1 if TRUE, 0 else)',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a csv file
	if not (csv_file.name.endswith('.item') or csv_file.name.endswith('.csv')):
		messages.error(request, 'THIS IS NOT A .ITEM OR .CSV FILE')

	data_set = csv_file.read().decode('UTF-8')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)

	# for all the lines in dataset file: create and save (or update) item object
	for column in csv.reader(io_string, delimiter='|', quotechar='"'):
		obj, created = Item.objects.update_or_create(
			item_id=column[0],
			name=column[1],
			dataset= dataset
		)
		# add genre, if there's a 1 in the respective column in the dataset file
		if column[6] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Action'))
			except MovieGenre.DoesNotExist:
				pass
		if column[7] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Adventure'))
			except MovieGenre.DoesNotExist:
				pass
		if column[8] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Animation'))
			except MovieGenre.DoesNotExist:
				pass
		if column[9] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Children'))
			except MovieGenre.DoesNotExist:
				pass
		if column[10] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Comedy'))
			except MovieGenre.DoesNotExist:
				pass
		if column[11] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Crime'))
			except MovieGenre.DoesNotExist:
				pass
		if column[12] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Documentary'))
			except MovieGenre.DoesNotExist:
				pass
		if column[13] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Drama'))
			except MovieGenre.DoesNotExist:
				pass
		if column[14] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Fantasy'))
			except MovieGenre.DoesNotExist:
				pass
		if column[15] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Film-Noir'))
			except MovieGenre.DoesNotExist:
				pass
		if column[16] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Horror'))
			except MovieGenre.DoesNotExist:
				pass
		if column[17] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Musical'))
			except MovieGenre.DoesNotExist:
				pass
		if column[18] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Mystery'))
			except MovieGenre.DoesNotExist:
				pass
		if column[19] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Romance'))
			except MovieGenre.DoesNotExist:
				pass
		if column[20] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Sci-Fi'))
			except MovieGenre.DoesNotExist:
				pass
		if column[21] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Thriller'))
			except MovieGenre.DoesNotExist:
				pass
		if column[22] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='War'))
			except MovieGenre.DoesNotExist:
				pass
		if column[23] == '1':
			try:
				obj.genres.add(MovieGenre.objects.get(title='Western'))
			except MovieGenre.DoesNotExist:
				pass

	context = {}
	return render(request, template, context)


@login_required
def rating_upload_100K(request, *args, **kwargs):
	# instantiate empty form in template
	form = DatasetFilterForm()

	# declaring template
	template = "recommender/upload.html"

	# context, handed over to template
	context = {
		'title': 'RATING UPLOAD',
		'example': 'Dataset e.g.: MovieLens 100K Dataset',
		'order': 'Order of the .DATA- OR .CSV-FILE should be a tab separated list of format "userId  itemId  rating  (...)"',
		'form': form
	}

	# GET request returns the value of the data with the specified key.
	if request.method == "GET":
		return render(request, template, context)

	if request.method == "POST":
		if request.POST.get("dataset_btn"):
			# get entries from form in template
			form = DatasetFilterForm(request.POST)
			if form.is_valid():
				# get dataset from form and save id in session variable
				dataset = form.cleaned_data['dataset']
				request.session['dataset_id'] = dataset.id
				request.session.modified = True
				context = {
					'title': 'RATING UPLOAD',
					'example': 'Dataset e.g.: MovieLens 100K Dataset',
					'order': 'Order of the .DATA- OR .CSV-FILE should be a tab separated list of format "userId  itemId  rating  (...)"',
					'form': form,
					'dataset': dataset
				}
				return render(request, template, context)

	# CSV file reading
	csv_file = request.FILES['file']

	# let's check if it is a .csv or .data file
	if not (csv_file.name.endswith('.data') or csv_file.name.endswith('.csv')):
		messages.error(request, 'THIS IS NOT A .DATA OR .CSV FILE')

	data_set = csv_file.read().decode('UTF-8')

	# get dataset from session variable
	dataset = Dataset.objects.get(id=request.session['dataset_id'])

	# setup a stream, loop through each line, handle a data in a stream
	io_string = io.StringIO(data_set)
	next(io_string)

	# save the reader in a list, to use it twice subsequently
	reader = csv.reader(io_string, delimiter='\t', quotechar='"')
	reader_list = list(reader)

	# find out how many users there are in the dataset, save the number in max
	max = 0
	for column in reader_list:
		if int(column[0]) > max:
			max = int(column[0])

	# create users in database (from user_id=1 to user_id=max), if they do not exist already
	for i in range(max):
		user_id=i+1
		try:
			user = User.objects.get(user_id=user_id,dataset=dataset)
		except User.DoesNotExist:
			User.objects.create(user_id=user_id,dataset=dataset)

	# for all the lines in dataset file: create and save (or update) rating object
	for column in reader_list:
		try:
			obj, created = Rating.objects.update_or_create(
				user=User.objects.get(user_id=column[0], dataset=dataset),
				item=Item.objects.get(item_id=column[1], dataset=dataset),
				rating=column[2]
			)
		except (Item.DoesNotExist,User.DoesNotExist):
			pass

	# calculate and save amount of ratings for each item (see below)
	amount_ratings_dataset(dataset=dataset)

	context = {}
	return render(request, template, context)




################################################
# AMOUNT RATINGS FUNCTIONS
################################################

def amount_ratings_dataset(dataset):
	# given a dataset, count and save the amount of ratings for all the items
	items = Item.objects.filter(dataset=dataset)
	for item in items:
		amount_ratings = Rating.objects.filter(item=item).count()
		item.amount_ratings = amount_ratings
		item.save()


def amount_ratings(dataset_id):
	# given a dataset id, count and save the amount of ratings for all the items
	dataset = Dataset.objects.get(id=dataset_id)
	amount_ratings_dataset(dataset)



################################################
# SURPRISE PREDICT FUNCTIONS
################################################
# in variation taken from and inspired by the python surprise library (see surprise.readthedocs.io)


def get_top_n(predictions, n=10):
    '''Return the top-N recommendation for each user from a set of predictions.

    Args:
    predictions(list of Prediction objects): The list of predictions, as
    returned by the test method of an algorithm.
    n(int): The number of recommendation to output for each user (default is 10).

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
    [(raw item id, rating estimation), ...] of size n.
    '''
    # first map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


# predict ratings for all pairs (u, i) that are NOT in the training set.
# value = dataset, arg = algorithm, number = top n
def predict_ratings(dataset, algorithm, number, file_path, format, delimiter, skip_lines):
	if (dataset.name == 'MovieLens 100K' or dataset.name == '100K'):
		# (SurDataset = surprise dataset) #ml-100k' is built-in
		data = SurDataset.load_builtin('ml-100k')

	# As we're loading a custom dataset, we need to define a reader. In the
	# movielens-100k dataset, each line has the following format:
	# 'user item rating timestamp', separated by '\t' characters.
	else:
		reader = Reader(line_format = format, sep = delimiter, skip_lines = skip_lines)
		data = SurDataset.load_from_file(file_path, reader=reader)

	trainset = data.build_full_trainset()

	# hardcoded algorithms from database -> call the the corresponding functions in surprise
	if (algorithm.name == 'SVD'):
		surprise_algo = SVD()

	elif (algorithm.name == 'SVD++'):
		surprise_algo = SVDpp()

	elif (algorithm.name == 'NMF'):
		surprise_algo = NMF()

	elif (algorithm.name == 'Slope One'):
		surprise_algo = SlopeOne()

	elif (algorithm.name == 'k-NN'):
		surprise_algo = KNNBasic()

	elif (algorithm.name == 'Centered k-NN'):
		surprise_algo = KNNWithMeans()

	elif (algorithm.name == 'k-NN Baseline'):
		surprise_algo = KNNBaseline()

	elif (algorithm.name == 'Co-Clustering'):
		surprise_algo = CoClustering()

	elif (algorithm.name == 'Baseline'):
		surprise_algo = BaselineOnly()

	elif (algorithm.name == 'Random'):
		surprise_algo = NormalPredictor()

	# make predictions from train- and testsets
	surprise_algo.fit(trainset)
	testset = trainset.build_anti_testset()
	predictions = surprise_algo.test(testset)

	# calculate and save the top-n recommendations for users
	top_n = get_top_n(predictions, number)

    # save the recommended items for each user in the corresponding recommendation lists
	for uid, user_ratings in top_n.items():
		try:
			rl = Reclist.objects.get(user=User.objects.get(dataset=dataset, user_id=uid),algorithm=algorithm,length=number)
		except(Reclist.DoesNotExist):
			rl = Reclist.objects.create(user=User.objects.get(dataset=dataset, user_id=uid),algorithm=algorithm,length=number)
			print(rl)
			i = 1
			# save the recommended items for each user with the rank in the list (for ordering the recommendation lists)
			for (iid, prd) in user_ratings:
				try:
					ReclistItem.objects.get(reclist=rl,item=Item.objects.get(dataset=Dataset.objects.get(id=dataset.id), item_id=iid),prediction=prd,number=i)
				except(ReclistItem.DoesNotExist):
					ReclistItem.objects.create(reclist=rl,item=Item.objects.get(dataset=Dataset.objects.get(id=dataset.id), item_id=iid),prediction=prd,number=i)
				i = i+1
