from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterUserForm
from event.models import UserProfile
from event.models import Square
from event.models import Question


def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.success(request, ("There Was An Error Logging In, Try Again..."))	
			return redirect('login')

	else:
		return render(request, 'authenticate/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ("You Were Logged Out!"))
	return redirect('home')


def register_user(request):
	if request.method == "POST":
		form = RegisterUserForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)		
			messages.success(request, ("Registration Successful!"))

			question = Question.objects.filter(name='Correct_1').order_by('?').first()

			user_profile = UserProfile.objects.create(user=user,name=user,x='0',y='0',xpos=5,ypos=5,pending_xpos=0,pending_ypos=0,correct_answers=0,wrong_answers=0,question=question,user_type='regular',mode='move')
			user.userprofile=user_profile
			currentsquare=Square.objects.get(x=5, y=5)
			currentsquare.occupants3.add(user.userprofile)
			currentsquare.save()
	
			return redirect('home')
	else:
		form = RegisterUserForm()

	return render(request, 'authenticate/register_user.html', {
		'form':form,
		})