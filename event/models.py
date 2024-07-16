from msilib import sequence
from django.db import models
from django.contrib.auth.models import User

import os
from django.conf import settings



#class UserXc(AbstractUser):
  #  x = models.IntegerField(null=True, blank=True)
  #  y = models.IntegerField(null=True, blank=True)

class ListItem(models.Model):
    name = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=False)
    size=models.IntegerField("size",default=-1)
    # Add other fields as needed

class Venue(models.Model):
	name=models.CharField('Venue Name',max_length=120)
	adress=models.CharField('Adress',max_length=120)
	zip_code=models.CharField('Zip Code',max_length=120)
	phone=models.CharField('Contact Phone',max_length=120)
	description=models.TextField(blank=True)

	def __str__(self):
		return self.name
	
class Question(models.Model):
    name=models.CharField('Question_name',max_length=120,default='question_name')
    
    question_swedish=models.CharField('question_swedish',max_length=300,default='swedish_question')
    answer1_swedish=models.CharField('answer1_swedish',max_length=300,default='swedish_answer1')
    answer2_swedish=models.CharField('answer2_swedish',max_length=300,default='swedish_answer2')
    answer3_swedish=models.CharField('answer3_swedish',max_length=300,default='swedish_answer3')
    answer4_swedish=models.CharField('answer4_swedish',max_length=300,default='swedish_answer4')
    
    question_english=models.CharField('question_english',max_length=300,default='english_question')
    answer1_english=models.CharField('answer1_english',max_length=300,default='english_answer1')
    answer2_english=models.CharField('answer2_english',max_length=300,default='english_answer2')
    answer3_english=models.CharField('answer3_english',max_length=300,default='english_answer3')
    answer4_english=models.CharField('answer4_english',max_length=300,default='english_answer4')
    correct_answer=models.IntegerField('correct_answer',default=0)

    difficulty=models.FloatField('difficulty',max_length=20,default='0.0')
    area1=models.CharField('area1',max_length=300,default='general')
    area2=models.CharField('area2',max_length=300,default='area2')
    area3=models.CharField('area3',max_length=300,default='area3')
    area4=models.CharField('area4',max_length=300,default='area4')
    area5=models.CharField('area5',max_length=300,default='area5')

    def __str__(self):
	    return self.name


class Environment(models.Model):
	name=models.CharField('Square Name',max_length=120)
	x=models.CharField('X',max_length=120)
	y=models.CharField('Y',max_length=120)
	z=models.CharField('Z',max_length=120)
	description=models.TextField(blank=True)

	def __str__(self):
		return self.name

class MyPlayer(models.Model):
	name=models.CharField('Square Name',max_length=120)
	x=models.CharField('X',max_length=120)
	y=models.CharField('Y',max_length=120)
	z=models.CharField('Z',max_length=120)
	description=models.TextField(blank=True)
	environment=models.ForeignKey(Environment, blank=True,null=True,on_delete=models.CASCADE)
	email=models.EmailField('User Email')

	def __str__(self):
		return self.name
	
class UserProfile(models.Model):

	last_active_time = models.DateTimeField(null=True, blank=True)
	name=models.CharField('User Name',max_length=120,default='0')
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_type=models.CharField('user_type',max_length=120,default='regular')
	x = models.IntegerField("x",default=0)
	y = models.IntegerField("y",default=0)
	xpos = models.IntegerField("xpos",default=0)
	ypos = models.IntegerField("ypos",default=0)
	pending_xpos = models.IntegerField("pending_xpos",default=0)
	pending_ypos = models.IntegerField("pending_ypos",default=0)
	#mapsquare = models.ForeignKey(Mapsquare,on_delete=models.DO_NOTHING)
	mode = models.CharField('mode',max_length=30,blank=True)
	question=models.ForeignKey(Question, blank=True,null=True,on_delete=models.SET_NULL)
	correct_answers = models.IntegerField("correct_answers",default=0)
	wrong_answers = models.IntegerField("wrong_answers",default=0)
	temp_label_holder=models.CharField('temp_label_holder',max_length=120,default='x')
	temp_question_holder=models.CharField('temp_question_holder',max_length=120,default='x')
	temp_question_area_holder=models.CharField('temp_question_area_holder',max_length=120,default='x')
	temp_question_area_strength_holder=models.CharField('temp_question_area_strength_holder',max_length=120,default='0')
	current_genome_dir=models.CharField('user_current_genome_dir',max_length=120,default='')
	blast_directory=models.CharField('blast_directory',max_length=120,default='')
	#blast_directory=models.CharField('blast_directory',max_length=120,default='c:/NCBI/blast-BLAST_VERSION+/bin/')
	first_e_cutoff=models.CharField('first_e_cutoff',max_length=120,default='1e-6')
	second_e_cutoff=models.CharField('second_e_cutoff',max_length=120,default='1e-6')
	transposase_protein_database=models.CharField('transposase_protein_database',max_length=120,default='C:/Users/Eris/Documents/scripts/autothink/is_aa_30_nov2016.fa')

	blast_files_dir=models.CharField('blast_files_dir',max_length=120,default="D:/blastresults/")
	blast_analysis_dir=models.CharField('blast_analysis_dir',max_length=120,default="D:/blastanalysis/")
	analysed_gb_files_dir=models.CharField('analysed_gb_files',max_length=120,default="D:/analysed_gb_files/")
	work_files_dir=models.CharField('work_files_dir',max_length=120,default="D:/workfiles/")
	is_list_csv_file_dir=models.CharField('is_list_csv_file_dir',max_length=120,default="D:/is_csvs/")
	is_frequency_pic_dir=models.CharField('is_frequency_pic_dir',max_length=120,default="c:/Users/Eris/Documents/visualAutothink/visapp_proj/static/event/images/")


	

	def __str__(self):
		return str(self.user)
	
class UserProfile2(models.Model):
	name=models.CharField('User Name',max_length=120,default='0')
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	x = models.IntegerField("x",default=0)
	y = models.IntegerField("y",default=0)
	xpos = models.IntegerField("xpos",default=0)
	ypos = models.IntegerField("ypos",default=0)
	def __str__(self):
		return str(self.name)




class Beacon(models.Model):
	name=models.CharField('Beacon Name',max_length=120)
	x=models.IntegerField('X',default=0)
	y=models.IntegerField('Y',default=0)
	z=models.IntegerField('Z',default=0)
	description=models.TextField(blank=True)

	image = models.CharField(max_length=100,default='null.png')
	territory = models.TextField(blank=True)
	map_label=models.CharField('map_label',max_length=120,blank=True)
	question_area1=models.CharField('questionarea1',max_length=120,blank=True)
	question_area1_strength=models.IntegerField('questionarea1_strength',default=0)
	question_area2=models.CharField('questionarea2',max_length=120,blank=True)
	question_area3=models.CharField('questionarea3',max_length=120,blank=True)
	question_area4=models.CharField('questionarea4',max_length=120,blank=True)
	buffer=models.IntegerField('buffer',default=0)
	def __str__(self):
		return self.name




class Square(models.Model):
	name=models.CharField('Square Name',max_length=120)
	x=models.CharField('X',max_length=120)
	y=models.CharField('Y',max_length=120)
	z=models.CharField('Z',max_length=120)
	description=models.TextField(blank=True)
	environment=models.ForeignKey(Environment, blank=True,null=True,on_delete=models.CASCADE)
	occupants=models.ManyToManyField(MyPlayer,blank=True)
	
	#occupants3 is used most
	occupants3 = models.ManyToManyField(UserProfile, blank=True, default=[])
	occupants4 = models.ManyToManyField(UserProfile2, blank=True, default=[])

	image = models.CharField(max_length=100,default='null.png')
	original_image=models.CharField(max_length=100,default='null.png')
	#image = models.CharField(max_length=100, default='null.png')
	territory = models.TextField(blank=True)
	map_label=models.CharField('map_label',max_length=120,blank=True)
	question_area1=models.CharField('question1',max_length=120,blank=True)
	
	def __str__(self):
		return self.name




class MyClubUser(models.Model):
	first_name=models.CharField('First Name',max_length=120)
	last_name=models.CharField('Last Name',max_length=120)
	y=models.CharField('Y',max_length=120)
	z=models.CharField('Z',max_length=120)
	description=models.TextField(blank=True)
	environment=models.ForeignKey(Environment, blank=True,null=True,on_delete=models.CASCADE)
	email=models.EmailField('User Email')

	def __str__(self):
		return self.first_name+' '+self.last_name

class Event(models.Model):
    name=models.CharField('Event Name',max_length=120)
    event_date=models.DateTimeField('Event Date')
    avenue=models.CharField('Avenue',max_length=120)
    manager=models.CharField('Manager',max_length=120)
    description=models.TextField(blank=True)
    attendees=models.ManyToManyField(MyClubUser,blank=True)

    def __str__(self):
	    return self.name
class Footprint(models.Model):
	start=models.IntegerField('start',default=-1)
	end=models.IntegerField('end',default=-1)
	sequence=models.CharField('sequence',max_length=5000,default="-1")

	def __str__(self):
		return "foorprint"
		
class genomeEntry(models.Model):
    name=models.CharField('name',max_length=120)
    path=models.CharField('path',max_length=120,default="-1")
    extra=models.CharField('extra',max_length=120)
    is_dir=models.CharField('is_dir',max_length=120,default=-1)
    description=models.TextField(blank=True)
    contigs_num=models.IntegerField('contigs_num',default=-1)
    genome_size=models.IntegerField('genome_size',default=-1)
    footprint_size=models.IntegerField('footprint_size',default=-1)
    button_analyse_isok=models.TextField('button_analyse_isok',default="red")
    button_prepare_isok=models.TextField('button_prepare_isok',default="red")
    button_blast_isok=models.TextField('button_blast_isok',default="red")
    button_blastanal_isok=models.TextField('button_blastanal_isok',default="red")
    button_footprints_isok=models.TextField('button_footprints_isok',default="red")
    button_analyse_results_isok=models.TextField('button_analyse_results_isok',default="red")


    files_num=models.IntegerField('files_num',default=-1)
    footprints=models.ManyToManyField(Footprint,blank=True)

    work_files_dir=models.CharField('work_files_dir',max_length=120,default="D:/workfiles/")
    concat_fasta_file=models.CharField('concat_fasta_file',max_length=120,default="")
    blast_results_file=models.CharField('blast_results_file',max_length=120,default="")
    blast_analysis_file=models.CharField('blast_analysis_file',max_length=120,default="")
    analysed_gb_files=models.CharField('analysed_gb_files',max_length=120,default="")
    is_list_csv_file=models.CharField('is_list_csv_file',max_length=120,default="")
    is_frequency_pic=models.CharField('is_frequency_pic',max_length=120,default="")

    def __str__(self):
	    return self.name


