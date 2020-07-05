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




################### Klasse MAPPING ####################

class Most_rated_neighbours():
	def __init__(self, online_user, nr_ratings = None, nr_users = None, dataset = None, mapped_user = None):
		self.online_user = online_user
		self.nr_ratings = nr_ratings
		self.nr_users = nr_users
		self.dataset = Study.objects.get(active=True).dataset
		self.mapped_user = mapped_user
		'''
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
			sum_user = User.objects.filter(dataset=self.dataset).count()
			if (sum_user) > 0:
				random_user_id = random.randrange(sum_user)
				self.mapped_user = User.objects.get(dataset=self.dataset, user_id=random_user_id)
		return self.mapped_user
		'''
	def sortSecond(val):
		return val[1]

	def most_rated_items_raters(self):
		items = Item.objects.filter(dataset=self.dataset)
		most_rated = items.order_by("-amount_ratings")[:self.nr_ratings]
		my_list = []
		for user in User.objects.filter(dataset=self.dataset):
			i = 0
			for item in most_rated:
				try:
					Rating.objects.get(user=user, item=item)
					i = i + 1
					my_tuple = (user, i)
				except(Rating.DoesNotExist):
					pass

			my_list.append(my_tuple)
		my_list.sort(key = sortSecond, reverse = True)
		user_list = [user[0] for user in my_list[:self.nr_users]]
		self.mapped_user = random.choice(user_list)
		return self.mapped_user

class Mapping(Most_rated_neighbours):
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
			sum_user = User.objects.filter(dataset=self.dataset).count()
			if (sum_user) > 0:
				random_user_id = random.randrange(sum_user)
				self.mapped_user = User.objects.get(dataset=self.dataset, user_id=random_user_id)
		return self.mapped_user


#################################################################


def home_view(request, *args, **kwargs):
	study = Study.objects.get(active=True)
	context = {
		'study': study,
	}
	return render(request, "study/home.html", context)


def login_view(request, *args, **kwargs):
	form = UserLoginForm()
	if request.method == "POST":
		form = UserLoginForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data['token'])
			new_token = form.cleaned_data['token']
			obj_token = get_object_or_404(Token, name=new_token)
			obj_token.valid = False
			obj_token.save()
			obj = str(obj_token)
			print(obj)
			User.objects.create(token=obj_token,online_user=True)
			object = DjUser.objects.create(username=obj)
			login(request, object)

			return redirect("study:start")
	else:
		form = UserLoginForm()
	return render(request, 'study/login.html', {'form': form})


def start_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	else:
		token_obj = Token.objects.get(name=request.user.username)
		user_obj = User.objects.get(token=token_obj)
		reclists = set()
		algos = []
		study = Study.objects.get(active=True)
		algo_query = study.algorithms.all()
		for a in algo_query:
			algos.append(a)
		print(algos)
		evals = Evaluation.objects.filter(study=study, user=user_obj)
		# evals: Evaluationen des Users / algos: Liste der Algorithmen in Studie
		# wenn Anzahl gleich existiert User bereits
		if (len(evals) == len(algos)):
			for eval in evals:
				reclists.add(eval.reclist)
		else:
			mapping = Mapping(user_obj)
			# Mapping Variante I
			mapped_user = mapping.random()

			# Mapping Variante II
			#mapping.nr_ratings = 30
			#mapping.nr_users = 30
			#mapped_user = mapping.most_rated_items_raters()

			try:
				for i in range(len(algos)):
					rl_obj = Reclist.objects.get(user=mapped_user, algorithm=algos[i], length=study.reclist_length)
					Evaluation.objects.create(study=study, user=user_obj, reclist=rl_obj)
					reclists.add(rl_obj)
			except Reclist.DoesNotExist:
				messages.warning(request, 'There seems to be a recommendation list missing. Please inform the study director.'
											' Thank you! Have lists been created for all algorithms of the study?')

		items = set()
		items_list = []
		for reclist in reclists:
			for item in reclist.reclist_items.all():
				items.add(item.item)
		items_list = []
		for item in items:
			items_list.append(item.id)
		request.session['items_list'] = items_list
		request.session.modified = True

		context = {
			"items":items,
			"items_list": request.session['items_list'],
		}
	return render(request, "study/start.html", context)


def item_rating_view(request, id, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	else:
		if request.method=='GET':
			request.session['runs'] = 0
			request.session['non_ratings'] = 0
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			item=get_object_or_404(Item, id=id)
			request.session['items_list'].pop(0)
			request.session.modified = True
			items_list = request.session['items_list']
			if request.session['items_list']:
				context={
					"item":item,
					"items_list":items_list,
				}
			else:
				context={
					"item":item,
				}
		if request.method=='POST':
			request.session['runs'] = request.session['runs'] + 1

			user = request.POST.get("user")
			item = request.POST.get("item")
			rating = request.POST.get("rating")

			ruser = User.objects.get(token=Token.objects.get(name=user))
			ritem = Item.objects.get(id=item)
			if rating != "":
				try:
					Rating.objects.get(user=ruser,item=ritem)
					messages.warning(request, 'This item has already been rated by you. Therefore the rating is not saved.')
				except(Rating.DoesNotExist):
					Rating.objects.create(user=ruser,item=ritem,rating=rating)
			else:
				request.session['non_ratings'] = request.session['non_ratings'] + 1

			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			item=get_object_or_404(Item, id=id)
			if request.session['items_list']:
				request.session['items_list'].pop(0)
				request.session.modified = True
				items_list = request.session['items_list']
				#print(request.session['items_list'])
				context={
					"item":item,
					"items_list":items_list
				}
			else:
				all_rated = True
				context={
					"item":item,
					"all_rated":all_rated,
				}
			#print('runs')
			#print(request.session['runs'])
			#print('non_ratings')
			#print(request.session['non_ratings'])

		return render(request, "study/rating_detail.html", context)

	return render(request, "study/rating_detail.html", {})



# get mapped reclists of user in evaluations, reclists bewerten, in evaluations speichern (+ accuracy berechnen)
def reclist_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	else:
		token_obj = Token.objects.get(name=request.user.username)
		user_obj = User.objects.get(token=token_obj)
		study=Study.objects.get(active=True)
		#print(study)
		eval_query = Evaluation.objects.filter(study=study, user=user_obj)
		evaluations = []
		for eval in eval_query:
			evaluations.append(eval)
		reclists = []
		reclists_id = []
		for i in range(len(evaluations)):
			reclists.append(evaluations[i].reclist)
			reclists_id.append(evaluations[i].reclist.id)

		request.session['reclists_list'] = reclists_id
		request.session.modified = True
		#print(request.session['reclists_list'])
		#print(reclists)
		context = {
			'reclists':reclists,
			'reclists_list':request.session['reclists_list'],
		}
		return render(request, "study/reclist_rating_begin.html", context)
		'''
		if request.method == "POST":
			form = EvaluationForm(request.POST)
			if form.is_valid():
				for i in range(len(evaluations)):
					if str(reclists[i].id) in request.POST:
						print(str(reclists[i].id))
						eval = evaluations[i]

						eval.accuracy_mae = accuracy_mae(eval)
						eval.accuracy_mse = accuracy_mse(eval)
						eval.accuracy_rmse = accuracy_rmse(eval)
						eval.utility = form.cleaned_data['utility']
						eval.serendipity = form.cleaned_data['serendipity']
						eval.novelty = form.cleaned_data['novelty']
						eval.diversity = form.cleaned_data['diversity']
						eval.unexpectedness = form.cleaned_data['unexpectedness']
						eval.save()
		'''
	return render(request, "study/reclist_rating_begin.html", {})


def reclist_rating_view(request, id, **kwargs):
	if not request.user.is_authenticated:
		messages.warning(request, 'You need to be authenticated.')
		return redirect('study:login')
	else:
		if request.method=='GET':
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			study=Study.objects.get(active=True)
			eval_query = Evaluation.objects.filter(study=study, user=user_obj)

			reclist=get_object_or_404(Reclist, id=id)
			form = EvaluationForm()
			request.session['reclists_list'].pop(0)
			request.session.modified = True
			reclists_list = request.session['reclists_list']
			if request.session['reclists_list']:
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
			form = EvaluationForm(request.POST)
			token_obj = Token.objects.get(name=request.user.username)
			user_obj = User.objects.get(token=token_obj)
			study=Study.objects.get(active=True)
			reclist = request.POST.get("reclist")

			try:
				eval = Evaluation.objects.get(study=study, user=user_obj, reclist=reclist)
			except(Evaluation.DoesNotExist):
				eval = Evaluation.objects.create(study=study, user=user_obj, reclist=reclist)

			reclist = eval.reclist
			items = []
			reclistitems = reclist.reclist_items.all()
			for ri in reclistitems:
				items.append(ri.item)
			rated_items = Rating.objects.filter(user=user_obj, item__in=items).count()
			non_rated_items = reclist.length - rated_items

			if form.is_valid():
				eval.accuracy_mae = accuracy_mae(eval)
				eval.accuracy_mse = accuracy_mse(eval)
				eval.accuracy_rmse = accuracy_rmse(eval)
				eval.utility = form.cleaned_data['utility']
				eval.serendipity = form.cleaned_data['serendipity']
				eval.novelty = form.cleaned_data['novelty']
				eval.diversity = form.cleaned_data['diversity']
				eval.unexpectedness = form.cleaned_data['unexpectedness']
				eval.non_rating_rate = float(non_rated_items)/float(reclist.length)
				eval.save()
			form = EvaluationForm()
			reclist=get_object_or_404(Reclist, id=id)
			if request.session['reclists_list']:
				request.session['reclists_list'].pop(0)
				request.session.modified = True
				reclists_list = request.session['reclists_list']
				print(request.session['reclists_list'])
				context={
					"reclist":reclist,
					"reclists_list":reclists_list,
					"form": form,
				}
			else:
				all_rated = True
				context={
					"reclist":reclist,
					"all_rated":all_rated,
				}

		return render(request, "study/reclist_rating_detail.html", context)

	return render(request, "study/reclist_rating_detail.html", context)



def stop_view(request, *args, **kwargs):
	if request.user.is_authenticated:
		logout(request)

	return render(request, "study/stop.html", {})


######################## ACCURACY FUNCTIONS START ##############################

# mean absolute error
def accuracy_mae(evaluation):
	reclist = evaluation.reclist
	user = evaluation.user
	print("MAE")
	sum = 0
	i = 0
	mae = 0
	for ri in reclist.reclist_items.all():
		print(ri)
		print(ri.item.id)
		print(ri.prediction)
		try:
			user_rating = Rating.objects.get(user=user,item=ri.item).rating
			print(user_rating)
			diff = abs(user_rating - ri.prediction)
			print(diff)
			sum = sum + diff
			i = i+1
		except (Rating.DoesNotExist):
			print("Rating does not exist")
	mae = sum/i
	return mae

# mean squared error
def accuracy_mse(evaluation):
	reclist = evaluation.reclist
	user = evaluation.user
	print("MSE")
	sum = 0
	i = 0
	mse = 0
	for ri in reclist.reclist_items.all():
		print(ri)
		print(ri.item.id)
		print(ri.prediction)
		try:
			user_rating = Rating.objects.get(user=user,item=ri.item).rating
			print(user_rating)
			diff = abs(user_rating - ri.prediction)
			sq_diff = math.pow(diff,2)
			print(sq_diff)
			sum = sum + sq_diff
			i = i+1
		except (Rating.DoesNotExist):
			print("Rating does not exist")
	mse = sum/i
	return mse

# root mean squared error
def accuracy_rmse(evaluation):
	return math.sqrt(accuracy_mse(evaluation))


######################## ACCURACY FUNCTIONS END ##############################
