from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterUserForm
from event.models import UserProfile
from event.models import Square
from event.models import Question
import os
from django.conf import settings


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

			#user_profile = UserProfile.objects.create(user=user,name=user,user_type='regular')


			BASE_DIR2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			dbp1=os.path.join(settings.STATIC_URL, 'isdatabase/is_aa_30_nov2016.fa')
			blastplacestatic=os.path.join(settings.STATIC_URL, 'blastbin')
			resultsplacestatic=os.path.join(settings.STATIC_URL, 'results')
			blast1_resultsplacestatic=os.path.join(settings.STATIC_URL, 'blast1results')
			blast_analysis_placestatic=os.path.join(settings.STATIC_URL, 'blastanalysis')
			analysed_gbfiles_placestatic=os.path.join(settings.STATIC_URL, 'analysed_gb_files/')
			is_list_csv_file_dir_placestatic=os.path.join(settings.STATIC_URL, 'is_list_csv/')
			is_frequency_pic_placestatic=os.path.join(settings.STATIC_URL, 'event/images/')
			current_genome_dir_placestatic=os.path.join(settings.STATIC_URL, 'genomes')
			dbp=BASE_DIR2+dbp1
			blastplace=BASE_DIR2+blastplacestatic+"/"
			resultplace=BASE_DIR2+resultsplacestatic
			blast1_resultplace=BASE_DIR2+blast1_resultsplacestatic
			blast_analysis_resultplace=BASE_DIR2+blast_analysis_placestatic
			analysed_gbfiles_place=BASE_DIR2+analysed_gbfiles_placestatic
			is_list_csv_place=BASE_DIR2+is_list_csv_file_dir_placestatic
			is_frequency_pic_place=BASE_DIR2+is_frequency_pic_placestatic
			current_genome_place=BASE_DIR2+current_genome_dir_placestatic
			
			user_profile = UserProfile.objects.create(user=user,name=user,user_type='regular',transposase_protein_database=dbp,work_files_dir=resultplace,blast_files_dir=blast1_resultplace,blast_analysis_dir=blast_analysis_resultplace,analysed_gb_files_dir=analysed_gbfiles_place,is_list_csv_file_dir=is_list_csv_place,is_frequency_pic_dir=is_frequency_pic_place,current_genome_dir=current_genome_place,blast_directory=blastplace)

			user.userprofile=user_profile

	
			return redirect('home')
	else:
		form = RegisterUserForm()

	return render(request, 'authenticate/register_user.html', {
		'form':form,
		})