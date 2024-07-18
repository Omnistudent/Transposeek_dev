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




	
class UserProfile(models.Model):

	last_active_time = models.DateTimeField(null=True, blank=True)
	name=models.CharField('User Name',max_length=120,default='0')
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_type=models.CharField('user_type',max_length=120,default='regular')
	
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
	

class Footprint(models.Model):
	start=models.IntegerField('start',default=-1)
	end=models.IntegerField('end',default=-1)
	sequence=models.CharField('sequence',max_length=5000,default="-1")

	def __str__(self):
		return "footprint"
		
class genomeEntry(models.Model):
    name=models.CharField('name',max_length=120)
    nick=models.CharField('nick',max_length=120,default="-")
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


