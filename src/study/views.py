from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User as DjUser
from recommender.models import *
from .forms import RatingForm, RatingHdForm, RatingHdFormSet, EvaluationForm
from recommender.forms import UserLoginForm

import random, math




###################
# MAPPING OF USERS
###################

class Most_rated_neighbours():
	"""
	base class for Mapping
	purpose: finding the users (nr_users) which rated the most of the most rated items (nr_ratings)
	"""
	def __init__(self, online_user, nr_ratings = None, nr_users = None, dataset = None, mapped_user = None):
		self.online_user = online_user
		self.nr_ratings = nr_ratings
		self.nr_users = nr_users
		self.dataset = Study.objects.get(active=True).dataset
		self.mapped_user = mapped_user

	# help method for most_rated_items_raters
	def sortbySecond(val):
		return val[1]

	# finding the users (arg: nr_users) which rated the most of the most rated items (arg: nr_ratings)
	def most_rated_items_raters(self):
		# items of dataset of current active study
		items = Item.objects.filter(dataset=self.dataset)
		# a number, given by nr_ratings, of most_rated items (items sorted)
		most_rated = items.order_by("-amount_ratings")[:self.nr_ratings]
		my_list = []
		# for all users: count the ratings of the most rated items, save in tuple
		for user in User.objects.filter(dataset=self.dataset):
			i = 0
			for item in most_rated:
				try:
					Rating.objects.get(user=user, item=item)
					i = i + 1
					my_tuple = (user, i)
				except(Rating.DoesNotExist):
					pass
			# save tuples in list
			my_list.append(my_tuple)
		# sort list by second entry (amount ratings per user)
		my_list.sort(key = sortbySecond, reverse = True)
		# get the first number (given by nr_users) of users
		user_list = [user[0] for user in my_list[:self.nr_users]]
		# get a random user of user_list and return the user
		self.mapped_user = random.choice(user_list)
		return self.mapped_user


class Mapping(Most_rated_neighbours):
	"""
	extending class Most_rated_neighbours
	purpose: mapping the online user randomly to an offline user, included in the dataset
	"""
	def random(self):
		# am Ende rausnehmen (if und else):
		if self.dataset.id == 81:
			random_user_id = 53
			print(random_user_id)
			while random_user_id in (53,55,85,87,92,127,138,147,158,163,175,194,207,245,250,281,289,315,320,333,358,360,388,397,406,431,442,478,481,499,502,506,508,518,538,545,576,578):
				random_user_id = random.randrange(610)
				print(random_user_id)
			self.mapped_user = User.objects.get(dataset=self.dataset, user_id=random_user_id)

		else:
			# count users of current dataset
			sum_user = User.objects.filter(dataset=self.dataset).count()
			if (sum_user) > 0:
				random_user_id = random.randrange(sum_user)
				# get and return a random user
				self.mapped_user = User.objects.get(dataset=self.dataset, user_id=random_user_id)
		return self.mapped_user



##########################################################
# ACCURACY FUNCTIONS FOR CALCULATION FOR THE EVALUATIONS
##########################################################

# mean absolute error
def accuracy_mae(evaluation):
	reclist = evaluation.reclist
	user = evaluation.user

	sum = 0
	i = 0
	mae = 0

	# for all items in recommendation list
	for ri in reclist.reclist_items.all():
		try:
			# get rating of online user
			user_rating = Rating.objects.get(user=user,item=ri.item).rating
			# difference between rating of online user and predicted rating of offline user
			diff = abs(user_rating - ri.prediction)
			sum = sum + diff
			i = i+1
		except (Rating.DoesNotExist):
			print("Rating does not exist")
	# return MAE
	mae = sum/i
	return mae


# mean squared error
def accuracy_mse(evaluation):
	reclist = evaluation.reclist
	user = evaluation.user

	sum = 0
	i = 0
	mse = 0

	# for all items in recommendation list
	for ri in reclist.reclist_items.all():
		try:
			# get rating of online user
			user_rating = Rating.objects.get(user=user,item=ri.item).rating
			# difference between rating of online user and predicted rating of offline user
			diff = abs(user_rating - ri.prediction)
			# difference to square
			sq_diff = math.pow(diff,2)
			sum = sum + sq_diff
			i = i+1
		except (Rating.DoesNotExist):
			print("Rating does not exist")
	# return MSE
	mse = sum/i
	return mse


# root mean squared error
def accuracy_rmse(evaluation):
	return math.sqrt(accuracy_mse(evaluation))



###########################################
# ACTUAL VIEWS
###########################################

# function based view
def home_view(request, *args, **kwargs):
	# get active study
	study = Study.objects.get(active=True)
	# context, hand over to template
	context = {
		'study': study,
	}
	return render(request, "study/home.html", context)


def login_view(request, *args, **kwargs):
	# instantiate empty form in template
	form = UserLoginForm()
	if request.method == "POST":
		# get entries from form in template
		form = UserLoginForm(request.POST)
		if form.is_valid():
			# get token by user in form field
			new_token = form.cleaned_data['token']
			# get token by entry, returns object, if exists (else 404)
			obj_token = get_object_or_404(Token, name=new_token)
			# cancel validity of token
			obj_token.valid = False
			obj_token.save()
			obj = str(obj_token)
			# create user in recommender database, as online user
			User.objects.create(token=obj_token,online_user=True)
			# create Django user (username is his token) and login
			object = DjUser.objects.create(username=obj)
			login(request, object)

			return redirect("study:start")
	else:
		# instantiate empty form in template
		form = UserLoginForm()
	return render(request, 'study/login.html', {'form': form})


def start_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	# user is logged in
	else:
		# get token by django username and user by token
		token_obj = Token.objects.get(name=request.user.username)
		user_obj = User.objects.get(token=token_obj)
		# empty set
		reclists = set()
		algos = []
		# get active study
		study = Study.objects.get(active=True)
		# get all algorithms to be compared in the study and save in list (algos)
		algo_query = study.algorithms.all()
		for a in algo_query:
			algos.append(a)
		# test whether evaluations for this study and user already exist in the database
		evals = Evaluation.objects.filter(study=study, user=user_obj)
		# test whether the length of algos and evals are the username
		# if yes: user already exists in study
		if (len(evals) == len(algos)):
			# add all recommendation lists that already exist in the database
			for eval in evals:
				reclists.add(eval.reclist)
		else:
			# random mapping of online user to offline user in dataset
			mapping = Mapping(user_obj)

			# Mapping variant I

			mapped_user = mapping.random()

			# Mapping variant II
			# random mapping to one of 50 offline users which rated the most of the 25 most rated items

			#mapping.nr_ratings = 25
			#mapping.nr_users = 50
			#mapped_user = mapping.most_rated_items_raters()

			try:
				for i in range(len(algos)):
					# try to get the recommendation list of mapped user and desired algorithm and list length
					rl_obj = Reclist.objects.get(user=mapped_user, algorithm=algos[i], length=study.reclist_length)
					# create and save evaluations for current online user, active study and found recommendation list
					Evaluation.objects.create(study=study, user=user_obj, reclist=rl_obj)
					reclists.add(rl_obj)
			# if recommendation list does not exist: warning message
			except Reclist.DoesNotExist:
				messages.warning(request, 'There seems to be a recommendation list missing. Please inform the study director.'
											' Thank you! Have lists been created for all algorithms of the study?')

		# empty set
		items = set()
		# save all items included in recommendation lists in set (to avoid duplicates)
		for reclist in reclists:
			for item in reclist.reclist_items.all():
				items.add(item.item)
		items_list = []
		# save all ids of items from set in the list
		for item in items:
			items_list.append(item.id)
		# save the list as session variable
		request.session['items_list'] = items_list
		request.session.modified = True

		# context, hand items and list of items over to template
		context = {
			"items":items,
			"items_list": request.session['items_list'],
		}
	return render(request, "study/start.html", context)


def item_rating_view(request, id, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	# user is logged in
	else:
		if request.method=='GET':
			# session variables runs and non_ratings, required no more in current version
			request.session['runs'] = 0
			request.session['non_ratings'] = 0
			# get user by token
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			# get item by id, passed as argument in the request
			item=get_object_or_404(Item, id=id)
			# remove the first element from the list in the session variable
			request.session['items_list'].pop(0)
			request.session.modified = True
			# hand over the updated list to the template, if the list is not empty
			items_list = request.session['items_list']
			if request.session['items_list']:
				# hand items and list of items over to template
				context={
					"item":item,
					"items_list":items_list,
				}
			else:
				# hand items over to template
				context={
					"item":item,
				}
		if request.method=='POST':
			# count up runs
			request.session['runs'] = request.session['runs'] + 1

			# get entries from template form
			user = request.POST.get("user")
			item = request.POST.get("item")
			rating = request.POST.get("rating")

			ruser = User.objects.get(token=Token.objects.get(name=user))
			ritem = Item.objects.get(id=item)

			# valid rating
			if rating != "":
				try:
					# warning message, if rating for user and item already exists
					Rating.objects.get(user=ruser,item=ritem)
					messages.warning(request, 'This item has already been rated by you. Therefore the rating is not saved.')
				except(Rating.DoesNotExist):
					# create and save rating to database
					Rating.objects.create(user=ruser,item=ritem,rating=rating)
			else:
				# don't know option in rating items
				request.session['non_ratings'] = request.session['non_ratings'] + 1

			# get user by token
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			# get item by id, passed as argument in the request
			item = get_object_or_404(Item, id=id)

			if request.session['items_list']:
				# remove the first element from the list in the session variable
				request.session['items_list'].pop(0)
				request.session.modified = True
				# hand over the updated list to the template, if the list is not empty
				items_list = request.session['items_list']

				# hand items and list of items over to template
				context={
					"item":item,
					"items_list":items_list
				}
			else:
				# all items are rated, list in session variable is empty
				all_rated = True
				# hand over to template
				context={
					"item":item,
					"all_rated":all_rated,
				}

		return render(request, "study/rating_detail.html", context)

	return render(request, "study/rating_detail.html", {})


def reclist_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	# user is logged in
	else:
		# get current user by token
		token_obj = Token.objects.get(name=request.user.username)
		user_obj = User.objects.get(token=token_obj)
		# get active study
		study=Study.objects.get(active=True)

		# get evaluation objects of current online user and save them in list
		eval_query = Evaluation.objects.filter(study=study, user=user_obj)
		evaluations = []
		for eval in eval_query:
			evaluations.append(eval)

		# get all recommendation lists and their ids from evaluations and save them in lists
		reclists = []
		reclists_id = []
		for i in range(len(evaluations)):
			reclists.append(evaluations[i].reclist)
			reclists_id.append(evaluations[i].reclist.id)

		# new session variable for recommendation list ids
		request.session['reclists_list'] = reclists_id
		request.session.modified = True

		# hand the lists and ids over to next page (template)
		context = {
			'reclists':reclists,
			'reclists_list':request.session['reclists_list'],
		}
		return render(request, "study/reclist_rating_begin.html", context)

	return render(request, "study/reclist_rating_begin.html", {})


def reclist_rating_view(request, id, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	# user is logged in
	else:
		if request.method=='GET':
			# get current user by token
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			# get active study
			study=Study.objects.get(active=True)
			# get evaluation objects of current online user and save them in list
			eval_query = Evaluation.objects.filter(study=study, user=user_obj)

			# get recommendation list by id, passed as argument in the request
			reclist=get_object_or_404(Reclist, id=id)

			# instantiate empty form in template
			form = EvaluationForm()

			# remove the first element from the list in the session variable
			request.session['reclists_list'].pop(0)
			request.session.modified = True

			# hand over the updated list to the template, if the list is not empty
			reclists_list = request.session['reclists_list']
			if request.session['reclists_list']:
				# context, hand reclists and form over to template
				context={
					"reclist":reclist,
					"reclists_list":reclists_list,
					"form": form,
				}
			else:
				context={
					"reclist":reclist,
				}
		if request.method=='POST':
			# get entries from form in template
			form = EvaluationForm(request.POST)

			# get current user by token
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			# get active study
			study=Study.objects.get(active=True)

			# get entry from template form
			reclist = request.POST.get("reclist")

			# create evaluation, if it doesn't exist already
			try:
				eval = Evaluation.objects.get(study=study, user=user_obj, reclist=reclist)
			except(Evaluation.DoesNotExist):
				eval = Evaluation.objects.create(study=study, user=user_obj, reclist=reclist)

			# get recommendation list of evaluation
			reclist = eval.reclist
			items = []
			# get all items of the recommendation list
			reclistitems = reclist.reclist_items.all()
			for ri in reclistitems:
				items.append(ri.item)

			# get number of actual ratings made by the current online user
			rated_items = Rating.objects.filter(user=user_obj, item__in=items).count()
			# calculate number of "don't know ratings"
			non_rated_items = reclist.length - rated_items

			if form.is_valid():
				# calculate and save accuracy metrics
				eval.accuracy_mae = accuracy_mae(eval)
				eval.accuracy_mse = accuracy_mse(eval)
				eval.accuracy_rmse = accuracy_rmse(eval)
				# get and save entries from template form
				eval.utility = form.cleaned_data['utility']
				eval.serendipity = form.cleaned_data['serendipity']
				eval.novelty = form.cleaned_data['novelty']
				eval.diversity = form.cleaned_data['diversity']
				eval.unexpectedness = form.cleaned_data['unexpectedness']
				# calculate and save the share of "don't know ratings"
				eval.non_rating_rate = float(non_rated_items)/float(reclist.length)
				eval.save()

			# instantiate empty form in template
			form = EvaluationForm()

			# test: get current recommendation list by id
			reclist=get_object_or_404(Reclist, id=id)
			if request.session['reclists_list']:
				# remove the first element from the list in the session variable
				request.session['reclists_list'].pop(0)
				request.session.modified = True

				# hand over the updated list to the template, if the list is not empty
				reclists_list = request.session['reclists_list']

				# context, hand reclists and form over to template
				context={
					"reclist":reclist,
					"reclists_list":reclists_list,
					"form": form,
				}
			else:
				# all items are rated, list in session variable is empty
				all_rated = True
				context={
					"reclist":reclist,
					"all_rated":all_rated,
				}

		return render(request, "study/reclist_rating_detail.html", context)

	return render(request, "study/reclist_rating_detail.html", context)



def stop_view(request, *args, **kwargs):
	# logout user after participation in the study
	if request.user.is_authenticated:
		logout(request)

	return render(request, "study/stop.html", {})
