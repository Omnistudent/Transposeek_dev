from msilib import sequence
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
#import calendar
#from calendar import HTMLCalendar
#from datetime import datetime
#from .models import Event
from .models import Square
from .models import Beacon
from .models import genomeEntry
#from .models import MyPlayer
from .models import UserProfile
from .models import Question
from .models import Footprint
import random
from random import shuffle
#from django.http import HttpResponse
#from django.http import JsonResponse
#import json
import math
from math import exp
from django.contrib.auth import authenticate, login
import string
#from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.conf import settings
from django.db import models
import os
from .models import ListItem
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Blast import NCBIXML
from Bio.Blast.Applications import NcbiblastxCommandline
from Bio.SeqFeature import SeqFeature, FeatureLocation
import csv
import subprocess
import io
import matplotlib.pyplot as plt
from PIL import Image
#from django.http import HttpResponse



default_genome_dir=""

onerange=['5', '15', '25', '35', '45', '55', '65', '75', '85', '95', '105', '115']
range_list_names_global=['-5_5', '5_15', '15_25', '25_35', '35_45', '45_55', '55_65', '65_75', '75_85', '85_95', '95_105', '105_115']

ishit_headers=["name","start","end","length","id","type","isfamily","isgroup","is_score","is_expected","is_frame","is_perc_of_orf","is_origin"]
finalcsvheaders=["organism","nt covered by is","number of is"]

SEP="\t"

def moveallowed(startx,endx,starty,endy):
    
    p1=[int(startx),int(starty)]
    p2=[int(endx),int(endy)]
    pdist=math.dist(p1,p2)
    
    if pdist<1.5:
        endsquare = Square.objects.get(x=endx, y=endy)
        if 'land' in endsquare.image:
            return False
        return True
    return False


def help(request):
    return render(request,'event/help.html',
        {})

def managegenomes(request):
    dbsquares = genomeEntry.objects.all()

    try:
        currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
    except:
        currendir_listing = []


    if request.method == 'POST':
        sent_action = request.POST.get('command')
        sent_answer = request.POST.get('answer')

        if sent_action == 'deletegenomes':
            print("sent_command deletegenomes")
            sent_answer = request.POST.get('answer').split(",")
            
            for i in sent_answer:
                genObj = genomeEntry.objects.filter(name=i).first()
                if genObj is not None:
                    genObj.delete()
                

            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing})

        
        
        if sent_action == 'addgenomes':
            print("sent_command addgenomes")
            sent_answer = request.POST.get('answer').split(",")
            
            for i in sent_answer:
                print(i)
                existing_entry = genomeEntry.objects.filter(name=i).first()
                

                if not existing_entry:

                    cleanedname=remove_extension(i)

                    if os.path.isdir(request.user.userprofile.current_genome_dir+"/"+i):
                        dirinput="1"
                    else:
                        dirinput="0"

                    my_work_files_dir=request.user.userprofile.work_files_dir+"/"+cleanedname
                    if not os.path.exists(my_work_files_dir):
                        os.makedirs(my_work_files_dir)
                        #print("making dir "+my_work_files_dir)

                    my_blast_files_dir=request.user.userprofile.blast_files_dir+"/"+cleanedname
                    if not os.path.exists(my_blast_files_dir):
                        os.makedirs(my_blast_files_dir)
                        #print("making dir "+my_blast_files_dir)

                    genomeP = genomeEntry.objects.create(name=i, path=request.user.userprofile.current_genome_dir, extra='sea3', is_dir=dirinput,blast_results_file=my_blast_files_dir,work_files_dir=my_work_files_dir)
                    
    
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing})

    
        if sent_action == 'commitDirectory':
            print("sent_command commitdirectory")
            sent_path = request.POST.get('answer')
            print (sent_path)
            if os.path.isdir(sent_path):
                request.user.userprofile.current_genome_dir=sent_path
                currendir_listing = os.listdir(sent_path)
                request.user.userprofile.save()


            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing})
        
    else:
        return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing})

            
               
              
def editSettings(request):
    if request.method == 'POST':
        sent_action = request.POST.get('command')
        print("sent --------------------------action")
        print(sent_action)

        for key in request.POST:
            
            if key not in ['command', 'csrfmiddlewaretoken']:  # Exclude these
                value = request.POST.get(key)
                print(f"Received setting: {key} with value: {value}")
                if hasattr(request.user.userprofile, key):
                    setattr(request.user.userprofile, key, value)
                    print("it had attrirböeöölldd")
                    request.user.userprofile.save()
               



    return render(request,'event/editSettings.html',{})

def home(request):
    #load_questions_from_file()
    if not request.user.is_authenticated:

            # Generate a random username and password
        username10 = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

        # Create a new user with the generated username and password
        user = User.objects.create_user(username=username10, password=password)
        question = Question.objects.filter(name='Correct_1').order_by('?').first()

   
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



        print(dbp)
        user_profile = UserProfile.objects.create(user=user,name=user,x='0',y='0',xpos=5,ypos=5,pending_xpos=0,
                                                  pending_ypos=0,correct_answers=0,wrong_answers=0,question=question,user_type='temp',mode='move',
                                                  transposase_protein_database=dbp,
                                                  work_files_dir=resultplace,
                                                  blast_files_dir=blast1_resultplace,
                                                  blast_analysis_dir=blast_analysis_resultplace,
                                                  analysed_gb_files_dir=analysed_gbfiles_place,
                                                  is_list_csv_file_dir=is_list_csv_place,
                                                  is_frequency_pic_dir=is_frequency_pic_place,
                                                  current_genome_dir=current_genome_place,
                                                  blast_directory=blastplace)

        user.userprofile=user_profile


 
   


        # Authenticate and log in the user
        user = authenticate(request, username=username10, password=password)

        # Set square to be occupied by user

        login(request, user)

    user=request.user

    currendir_listing=[]

    try:
        question = user.userprofile.question
    except:
        question = Question.objects.exclude(area1='utility').filter(difficulty__lte=3).order_by('?').first()

    

    if request.method == 'POST':
        sent_action = request.POST.get('command')
        sent_answer = request.POST.get('answer')

        print("sent action")
        print(sent_action)


       

       

        

        if sent_action == 'analyzefile':
            print("sent_command analyzefile")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            genomeFullPath=genObj.path+"/"+genObj.name
            contigs=getGenomeInfo(genomeFullPath)
            print(contigs[0])
            print(contigs[1])
            genObj.contigs_num=int(contigs[0])
            genObj.genome_size=int(contigs[1])
            genObj.save()
            answers = []
            dbsquares=getDatabaseAndView()
            
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})



        if sent_action == 'prepare':
            print("sent_command prepare")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            genomeFullPath=genObj.path+"/"+genObj.name
            contigs=prepareGenomeForBlast(genomeFullPath,genObj,sent_answer,user)
            print(contigs[0])
            print(contigs[1])
            genObj.contigs_num=contigs[0]
            genObj.genome_size=contigs[1]
            genObj.save()

            answers = []
            dbsquares=getDatabaseAndView()
            
            sent_path=user.userprofile.current_genome_dir
            checkButtons()

            return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})


        if sent_action == 'blast':
            print("sent_command blast")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            genomeFullPath=genObj.path+"/"+genObj.name
            doblast(genomeFullPath,genObj,sent_answer,user)

            answers = []
            dbsquares=getDatabaseAndView()
          
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})

        if sent_action == 'analyseblast':
            print("sent_command analyse blast")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            #genomeFullPath=genObj.path+"/"+genObj.name
            analyseblast(genObj,sent_answer,user)

            answers = []
            dbsquares=getDatabaseAndView()
        
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})
      
        if sent_action == 'make_footprint':
            print("sent_command make_footprint")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            #genomeFullPath=genObj.path+"/"+genObj.name
            analyse_footprints(genObj,sent_answer,user)

            answers = []
            dbsquares=getDatabaseAndView()
     
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})


        if sent_action == 'analyse_results':
            print("sent_command analyse_results")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            #genomeFullPath=genObj.path+"/"+genObj.name
            analyse_results(genObj,sent_answer,user)

            answers = []
            dbsquares=getDatabaseAndView()
        
            sent_path=user.userprofile.current_genome_dir
            
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})



        file_list = ["test1","testt2"]#os.listdir(directory_path)
    
        items = []
        for file_name in file_list:
            item = ListItem(name=file_name)
            items.append(item)
            print(file_name)






        dbsquares=getDatabaseAndView()
        
        sent_path=user.userprofile.current_genome_dir
        return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})
    # end of if request was post


    else: # if request method was not post

        dbsquares=getDatabaseAndView()


        file_list = ["test1","testt2"]#os.listdir(directory_path)
    
        items = []
        for file_name in file_list:
            item = ListItem(name=file_name)
            items.append(item)


        checkButtons()

        #items = ListItem.objects.all()
        try:
            sent_path=user.userprofile.current_genome_dir
        except:
            sent_path=""

        #return render(request,'event/home.html',{'myrange_x':myrange_x,'myrange_y':myrange_y,'squaredb':dbsquares,'question':question,'answers':answers,'overlays':overlays,'currentdir':sent_path,'currentdir_listing':currendir_listing})
        return render(request,'event/home.html',{'squaredb':dbsquares,'currentdir':sent_path,'currentdir_listing':currendir_listing})


def checkButtons():
    genomeentrylist=genomeEntry.objects.all()
    for genomme in genomeentrylist:

        if is_valid_file(genomme.path+"/"+genomme.name):
            genomme.button_analyse_isok="green"
            genomme.button_prepare_isok="green"
            genomme.save()
        if is_valid_concat_file(genomme.concat_fasta_file):
            genomme.button_blast_isok="green"
            genomme.save() 
        if is_valid_blastresults_file(genomme.blast_results_file):
            genomme.button_blastanal_isok="green"
            genomme.save()
        if genomme.footprints.all().exists():
            genomme.button_footprints_isok="green"
            #button_blast_isok
            genomme.save()
        if is_valid_analysed_gb_file(genomme.analysed_gb_files):
            genomme.button_analyse_results_isok="green"
            genomme.save()
    return()
    

def is_valid_file(path):
    return os.path.isfile(path) and path.lower().endswith(('.gb', '.fa', '.fasta','.gbk', '.gbff', '.fna'))

def is_valid_concat_file(path):
    return os.path.isfile(path) and path.lower().endswith(('_conc.fa'))

def is_valid_blastresults_file(path):
    return os.path.isfile(path) and path.lower().endswith(('_blast1results.xml'))

def is_valid_analysed_gb_file(path):
    return os.path.isfile(path) and path.lower().endswith(('.gb'))

def remove_extension(s):
    extensions = ('.gb', '.fa', '.fasta', '.gbk', '.gbff', '.fna')
    for ext in extensions:
        if s.endswith(ext):
            return s[:-len(ext)]
    return s

def create_bar_diagram(data, filename):
    # Extract data
    categories = list(data.keys())
    frequencies = list(data.values())
    
    # Plotting the bar chart
    fig, ax = plt.subplots(figsize=(1.2, 0.5))  # Set the figure size in inches (width=1.2in, height=0.5in)
    ax.bar(categories, frequencies, color='blue')
    
    # Remove x and y axis labels and title
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("")
    
    # Set the display limits
    ax.axis('off')
    
    # Save the figure to a file
    plt.tight_layout()
    plt.savefig(filename, dpi=100, bbox_inches='tight', transparent=True)

def getGenomeInfo(genomeFullPath):
    #remove_extension(s)
    file_end=genomeFullPath.split(".")[-1]
    genbank_endings= ["gbk", "gb","gbff"]
    fasta_endings= ["fa", "fasta","fna"]
    genomeFullPath_fh=open(genomeFullPath,"r")
    print(file_end)
    if file_end in genbank_endings:
        parsed_genbank=list(SeqIO.parse(genomeFullPath_fh,"genbank"))
        print("genbank")
    elif file_end in fasta_endings:
        print("fasta")
        parsed_genbank=list(SeqIO.parse(genomeFullPath_fh,"fasta"))
    else:
        print("error")

    genomeFullPath_fh.close()
    numcontigs=len(parsed_genbank)
    totalgenomesize=0
    for record in parsed_genbank:
        seq= str(record.seq)
        seqlen=len(seq)
        totalgenomesize+=seqlen

    print(dir(parsed_genbank))
    return(numcontigs,totalgenomesize)


def analyse_results(genObj,sent_answer,user):
    #genObj,sent_answer,user
    #remove_extension(s)
    #def remove_footprints_from_gb_file(sentpath,store):
    genomename=remove_extension(sent_answer)
    
    # initialize rangedic
    is_fraction_counts={}
    rangedic={}
    for r in onerange:
        rangedic[r]=0
        is_fraction_counts[r]=0
    
    # parse sent genbank
    fh=open(genObj.analysed_gb_files,"r")
    internalparsed_genbank=list(SeqIO.parse(fh,"genbank"))
    fh.close()

    if len(internalparsed_genbank)>1:
        print("more than one record in remove_footprint_from_gb_file, length:",str(len(internalparsed_genbank)))

    rec=internalparsed_genbank[0]
    allfeats=[]



    hit_csv_string=""
    for header in ishit_headers: 
        hit_csv_string+=header+SEP

    for ik in onerange:
        hit_csv_string+=str(int(ik)-10)+"tolessthan"+str(ik)+SEP


    for feat in rec.features:

        perc_of_orf="unknown"

        hit_qualifiers= ["is_name","family","group","score","expected","frame","perc_of_orf","origin","numorfs"]

        hit_csv_string+=str(feat.type)+SEP
        hit_csv_string+=str(feat.location.start)+SEP
        hit_csv_string+=str(feat.location.end)+SEP
        hit_csv_string+=str(1+abs(int(feat.location.start)-int(feat.location.end)))+SEP #length
        hit_csv_string+=str(feat.id)+SEP
        for hit_qual in hit_qualifiers:
            if hit_qual in feat.qualifiers.keys():
                hit_csv_string+=str(feat.qualifiers[hit_qual][0])+SEP
                if hit_qual=="perc_of_orf":
                    perc_of_orf= feat.qualifiers[hit_qual][0]
            else:
                hit_csv_string+="unknown"+SEP

        if perc_of_orf!="unknown":
            for upperlimit in onerange:
                if float(perc_of_orf)<float(upperlimit)*0.01:
                    uppernum=str(upperlimit)
                    lowernum=str(int(upperlimit)-10)
                    is_fraction_counts[upperlimit]+=1
                    break

        for uppervar in onerange:
            hit_csv_string+=str(is_fraction_counts[uppervar])+SEP
            print(uppervar+":"+str(is_fraction_counts[uppervar]))

        for hit_qual in feat.qualifiers.keys():
            hit_csv_string+=str(hit_qual)+":"+str(feat.qualifiers[hit_qual][0])+SEP

        hit_csv_string+="\n"

    pic_dir=user.userprofile.is_frequency_pic_dir
    pic_file=pic_dir+genomename+".png"

    blank_file=pic_dir+"blank.png"
    #create_blank_image(120, 50, blank_file)
      
    create_bar_diagram(is_fraction_counts,pic_file)


    genObj.is_frequency_pic=genomename+".png"
    genObj.save()

    file_start=remove_extension(genomename)
    my_blast_files_dir=user.userprofile.blast_files_dir+"/"+file_start



    csv_dir=user.userprofile.is_list_csv_file_dir+"/"+genomename+"/"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    csv_file=csv_dir+genomename+".csv"

    fho3=open(csv_file,"w")
    fho3.write(hit_csv_string)
    fho3.close()
    return()

def prepareGenomeForBlast(genomeFullPath,genObj,genomename,user):
    file_end=genomename.split(".")[-1]
    file_start=genomename.split(".")[0]
    file_start=remove_extension(genomename)
    genbank_endings= ["gbk", "gb","gbff"]
    fasta_endings= ["fa", "fasta","fna"]
    genomeFullPath_fh=open(genomeFullPath,"r")
    full_file_start=genomename.split(".")[0]
    concatFastaFilename=file_start+"_conc.fa"
    my_work_files_dir=user.userprofile.work_files_dir+"/"+file_start
    print(my_work_files_dir)
    if not os.path.exists(my_work_files_dir):
        os.makedirs(my_work_files_dir)
    print(file_end)
    if file_end in genbank_endings:
        parsed_genbank=list(SeqIO.parse(genomeFullPath_fh,"genbank"))
        print("genbank")
    elif file_end in fasta_endings:
        print("fasta")
        parsed_genbank=list(SeqIO.parse(genomeFullPath_fh,"fasta"))
    else:
        print("error")
    numcontigs=len(parsed_genbank)
    totalgenomesize=0
    concatenated_sequence = sum(parsed_genbank, Seq(""))
    tempstring=""
    
    for record in parsed_genbank:
        seq= str(record.seq)
        tempstring+=seq
        seqlen=len(seq)
        totalgenomesize+=seqlen

    atta= Seq(tempstring)
    concatenated_record = SeqRecord(atta, id=file_start, description=file_start)
    genomeFullPath_fh.close()
    
    outputdir=my_work_files_dir
    outputname=outputdir+"/"+concatFastaFilename
    genObj.work_files_dir=my_work_files_dir

    genObj.concat_fasta_file=outputname

    genObj.save() 
    
    output_fh=open(outputname,"w")

    output_filename = outputname
    SeqIO.write(concatenated_record, output_fh, "fasta")
    output_fh.close()
    
    return(numcontigs,totalgenomesize)

def analyse_footprints(genObj,sent_answer,user):

    file_start=sent_answer.split(".")[0]
    genomename=remove_extension(sent_answer)
    genomeseqfh=open(genObj.concat_fasta_file,"r")
    records=SeqIO.parse(genomeseqfh, "fasta")
    genomesequence=""
    for parse in records:
        genomesequence = str(parse.seq)

    starts_and_ends=genObj.footprints.all()
  
    gbhitslist=[]

    for res in starts_and_ends:
        msequence = str(res.sequence)
       
        firstsearch=[res.sequence,1,len(res.sequence)]
        footprintseq=res.sequence
        remainsearches=[firstsearch]
        while len(remainsearches)>0:
            currentsearch=remainsearches.pop()
            currentseq=currentsearch[0]
            oldstart=currentsearch[1]
            oldend=currentsearch[2]
            if len(currentseq)>4:
                doblast_results=doblast2(currentseq,res.start,sent_answer,user)
            else:
                doblast_results=None

            if (doblast_results==None) or (float(doblast_results["expected"])>float(user.userprofile.second_e_cutoff)):
                pass
            else:
                blast_hitstart=min(int(doblast_results["query_start"]),int(doblast_results["query_end"]))
                blast_hitend=max(int(doblast_results["query_start"]),int(doblast_results["query_end"]))
                recorded_blast_hitstart=blast_hitstart+oldstart-1
                recorded_blast_hitend=blast_hitend+oldstart-1
                listToAppend=[recorded_blast_hitstart+res.start,recorded_blast_hitend+res.start,doblast_results["hit_def"],doblast_results,res.start]
                gbhitslist.append(listToAppend)
                if not blast_hitstart==1:
                    leftstart=oldstart
                    leftend=oldstart+blast_hitstart-2
                    leftremains_list=[getseq(leftstart,leftend,footprintseq),leftstart,leftend]
                    remainsearches.append(leftremains_list)
                if not blast_hitend==len(currentseq):
                    rightstart=oldstart+blast_hitend
                    rightend=oldend
                    rightremains_list=[getseq(rightstart,rightend,footprintseq),rightstart,rightend]
                    remainsearches.append(rightremains_list)

        # It shouldn't matter if these hits are sorted or not
    sortedhits=sorted(gbhitslist,key=lambda x: x[3]["score"], reverse=True)


    
    gblist=makeGeneBankFeatures(sortedhits,genomesequence,sent_answer,user,genObj)
    return()

def getseq(start,end,seq):
    return seq[start-1:end]

def doblast(isseq,genObj,genomename,user):
    #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #print("dddddddddddddddd")
    #print(BASE_DIR)
    file_start=genomename.split(".")[0]
    file_start=remove_extension(genomename)
    my_blast_files_dir=user.userprofile.blast_files_dir+"/"+file_start
    if not os.path.exists(my_blast_files_dir):
        os.makedirs(my_blast_files_dir)
        print("made dir "+my_blast_files_dir)

    resultsfilepath=my_blast_files_dir+"/"+file_start+"_blast1results.xml"
    genObj.blast_results_file=resultsfilepath
    genObj.save()
    blastx_cline2 = NcbiblastxCommandline(query=genObj.concat_fasta_file, db=user.userprofile.transposase_protein_database, evalue=user.userprofile.first_e_cutoff, outfmt=5, out=resultsfilepath,max_target_seqs=10000,num_threads=4,query_gencode=11)

    blastline=user.userprofile.blast_directory+"blastx -db "+user.userprofile.transposase_protein_database+" -out "+resultsfilepath+" -query "+genObj.concat_fasta_file+" -query_gencode 11 -num_threads 4 -outfmt 5 -evalue "+ user.userprofile.first_e_cutoff
    print("lll")
    print(user.userprofile.blast_directory+str(blastx_cline2))
    os.system(user.userprofile.blast_directory+str(blastx_cline2)) 
    return()

def doblast2(isseq,offset,genomename,user):
    #(isseq,offset)

    file_start=genomename.split(".")[0]
    my_blast_files_dir=user.userprofile.blast_files_dir+"/"+file_start
    if not os.path.exists(my_blast_files_dir):
        os.makedirs(my_blast_files_dir)
        print("made dir "+my_blast_files_dir)

    msequence=">sequence1\n"+str(isseq)
    result = subprocess.run([user.userprofile.blast_directory+"blastx", "-db", user.userprofile.transposase_protein_database, "-query", "-","-query_gencode","11","-outfmt","5","-evalue",user.userprofile.first_e_cutoff], input=msequence, text=True, capture_output=True)
    blast_output = io.StringIO(result.stdout)
    blast_records = list(NCBIXML.parse(blast_output))

    
    hsps=[]
    for record in blast_records:
        for alg in record.alignments:
            for hsp in alg.hsps:
                # Collect hit info in dictionary
                dic={}
                dic["hit_def"]=str(alg.hit_def)
                dic["sbjct_start"]=hsp.sbjct_start
                dic["match"]=hsp.match
                dic["identities"]=hsp.identities
                dic["positives"]=hsp.positives
                dic["sbjct_end"]=hsp.sbjct_end
                dic["expected"]=str(hsp.expect)
                dic["frame"]=hsp.frame
                dic["bits"]=hsp.bits
                dic["query"]=str(hsp.query)
                dic["mod_query_end"]=hsp.query_end+offset-1
                dic["mod_query_start"]=hsp.query_start+offset-1
                dic["query_end"]=hsp.query_end
                dic["query_start"]=hsp.query_start
                dic["sbjct"]=str(hsp.sbjct)
                dic["score"]=hsp.score
                dic["align_length"]=hsp.align_length
                dic["query_length"]=record.query_length
                dic["queried_seq"]=isseq
                dic["hit_seq"]=getseq(int(min(int(hsp.query_start),int(hsp.query_end))),int(max(int(hsp.query_start),int(hsp.query_end))),isseq)
                hsps.append(dic)
    # Sort collected list by score
    mysortedhsps=sorted(hsps,key=lambda x: x["score"], reverse=True)
    if len(mysortedhsps)>0:
        # Return the hit with the hightest score, if any
        return mysortedhsps[0]
    else:
        return None


    #sequence = ">sequence1\nATGTCACTGACTGACTGACGTCA"
    #result = subprocess.run([user.userprofile.blast_directory+"blastx", "-db", "your_database", "-query", "-","-query_gencode","11","-outfmt","5","-evalue",user.userprofile.first_e_cutoff], input=sequence, text=True, capture_output=True)

    #print(result.stdout)


    #resultsfilepath=my_blast_files_dir+"/"+file_start+"_blast1results.xml"
    #genObj.blast_results_file=resultsfilepath
    #genObj.save()
    #blastx_cline2 = NcbiblastxCommandline(query=genObj.concat_fasta_file, db=user.userprofile.transposase_protein_database, evalue=user.userprofile.first_e_cutoff, outfmt=5, out=resultsfilepath,max_target_seqs=10000,num_threads=4,query_gencode=11)

    #blastline=user.userprofile.blast_directory+"blastx -db "+user.userprofile.transposase_protein_database+" -out "+resultsfilepath+" -query "+genObj.concat_fasta_file+" -query_gencode 11 -num_threads 4 -outfmt 5 -evalue "+ user.userprofile.first_e_cutoff
    #print(blastx_cline2)
    #os.system(user.userprofile.blast_directory+str(blastx_cline2)) 


def analyseblast(genObj,genomename,user):
    file_start=genomename.split(".")[0]
    file_start=remove_extension(genomename)
    my_blast_analysis_dir=user.userprofile.blast_analysis_dir+"/"+file_start

    gb_analysis_rec=parse_xml_file(genObj.blast_results_file,file_start,genObj,user)
    print("done parsing")

    
    if not os.path.exists(my_blast_analysis_dir):
        os.makedirs(my_blast_analysis_dir)

    analysed_gb_file=my_blast_analysis_dir+"/"+file_start+"_blast1analysis.gb"

    genbank_output2=open(analysed_gb_file,"w")
    gb_analysis_rec[0].annotations["molecule_type"] = "DNA"
    genObj.footprint_size=int(gb_analysis_rec[1])
    genObj.save()
    SeqIO.write([gb_analysis_rec[0]],genbank_output2,"genbank")
    return()


def makeGeneBankFeatures(sortedhits,genomesequence,genomename,user,genob):

    s=Seq(str(genomesequence))
    newrec=SeqRecord(s)
    newrec.id= genomename
    newrec.annotations["molecule_type"] = "DNA"
    #newrec.id= str(rec.query).split(" ",1)[0]
    #if len(str(newrec.id))>15:
    #    newrec.id= str(rec.query)[0:16]
    #if len(str(rec.query).split(" "))>1:
    #    newrec.description= str(rec.query).split(" ",1)[1]
    #else:
    #    newrec.description= rec.query
    newrec.description=genomename
    allfeatures=[]
    for hit in sortedhits:		
            if hit[3]["frame"][0]>=1:
                hitstrand=1
            if hit[3]["frame"][0]<0:
                hitstrand=-1
            splitname=hit[2].split("__")
            orflength=splitname[6].replace("orflength:","")
            subjstart=int(hit[3]["sbjct_start"])
            subjend=int(hit[3]["sbjct_end"])
            aahitlen=1+max(subjstart,subjend)-min(subjstart,subjend)
            perc_of_orf=round(aahitlen/float(orflength),3)
            minorf=min(subjstart,subjend)
            maxorf=max(subjstart,subjend)
            orftype="IS"

            
            complete_cutoff=0.95
            whole_cutoff=0.8
            isstart_start_cutoff=0.3
            isstart_end_cutoff=0.5
            isend_start_cutoff=0.7
            ismiddle_end_cutoff=0.7
            ismiddle_start_cutoff=0.3
            #if detailed_orfnames:
            if True:
                if perc_of_orf>=complete_cutoff: 
                #if perc_of_orf>=complete_cutoff: 
                    orftype="completeIS"+"_"+str(complete_cutoff)
                elif perc_of_orf>=0.8: 
                    orftype="wholeIS"+"_"+str(whole_cutoff)
                elif minorf<=float(orflength)*isstart_start_cutoff and maxorf<=float(orflength)*isstart_end_cutoff:
                    orftype="ISstart"
                elif minorf>=float(orflength)*isend_start_cutoff:
                    orftype="ISend"
                elif minorf>=float(orflength)*ismiddle_start_cutoff and maxorf<=float(orflength)*ismiddle_end_cutoff:
                    orftype="ISmiddle"

            feature = SeqFeature(FeatureLocation(int(hit[0]),int(hit[1])), strand=hitstrand,type=orftype)
            feature.id=hit[3]["hit_def"]
            family=splitname[1].replace("family:","")
            group=splitname[2].replace("group:","")
            origin=splitname[3].replace("origin:","")
            accession=splitname[4].replace("accession:","")
            ntlength=splitname[5].replace("ntlength:","")
            isnumorfs=splitname[7].replace("isnumorfs","")
            feature.qualifiers["is_name"]=splitname[0]

            feature.qualifiers["original_orf"]=str(orflength)
            feature.qualifiers["original_aa_length"]=str(aahitlen)

            feature.qualifiers["family"]=family
            feature.qualifiers["group"]=group
            feature.qualifiers["origin"]=origin
            feature.qualifiers["ntlength"]=ntlength
            feature.qualifiers["orflength"]=orflength
            feature.qualifiers["numorfs"]=isnumorfs
            feature.qualifiers["sbjct_start"]=str(hit[3]["sbjct_start"])
            feature.qualifiers["sbjct_end"]=str(hit[3]["sbjct_end"])
            feature.qualifiers["expected"]=str(hit[3]["expected"])
            feature.qualifiers["score"]=str(hit[3]["score"])
            feature.qualifiers["query_length"]=str(hit[3]["query_length"])
            #feature.qualifiers["match"]=str(hit[3]["match"])
            feature.qualifiers["query_start"]=str(hit[3]["query_start"])
            feature.qualifiers["identities"]=str(hit[3]["identities"])
            feature.qualifiers["align_length"]=str(hit[3]["align_length"])
            feature.qualifiers["positives"]=str(hit[3]["positives"])
            #feature.qualifiers["query"]=str(hit[3]["query"])
            #feature.qualifiers["queried_seq"]=str(hit[3]["queried_seq"])
            feature.qualifiers["query_end"]=str(hit[3]["query_end"])
            feature.qualifiers["frame"]=str(hit[3]["frame"])
            feature.qualifiers["bits"]=str(hit[3]["bits"])
            #feature.qualifiers["sbjct"]=str(hit[3]["sbjct"])
            feature.qualifiers["mod_query_start"]=str(hit[3]["mod_query_start"])
            feature.qualifiers["mod_query_end"]=str(hit[3]["mod_query_end"])
            feature.qualifiers["perc_of_orf"]=str(perc_of_orf)
            allfeatures.append(feature)
    newrec.features=allfeatures
        
        # Return the genome searhed (hit name), a genbank record, and empty string and filename(samplename) 
    #replies.append([hit_name,newrec,mycsvstring,samplename])
    #return replies


    curatedfilename_dir=user.userprofile.analysed_gb_files_dir+"/"+genomename
                

    if not os.path.exists(curatedfilename_dir):
        os.makedirs(curatedfilename_dir)
    gbfilenameout=curatedfilename_dir+"/"+remove_extension(genomename)+"_curated.gb"
                
    genbank_output2=open(gbfilenameout,"w")
    SeqIO.write([newrec],genbank_output2,"genbank")
    genbank_output2.close()

    genob.analysed_gb_files=gbfilenameout
    genob.save()
    return newrec   

def parse_xml_file(sample,samplename,genObj,user):
    total_footprint_nucleotides=0
    xmlfh=open(sample,"r")
    try:
        blast_records = list(NCBIXML.parse(xmlfh))	
    except:
        print("no file")
    xmlfh.close()
    print("opened reuslts")
    if len(list(blast_records))<1:
        print("no records")
    if len(list(blast_records))>1:
        print("more than one records")
    parseitrecordcounter=0
    for rec in blast_records:
        print("record")
        #print(rec.query)
        parseitrecordcounter+=1
        hit_def="NONE"
        mycsvstring=""
        gbhitslist=[]
        if (len(rec.alignments))<1:
            print("parseit: no algs for "+samplename)
            #continue
        hit_name=((str(rec.query)).split(" "))[0]
        print(hit_name)
        fastafh=open(genObj.concat_fasta_file,"r")

        queryseq=None
        with open(genObj.concat_fasta_file, "r") as handle:
            for record in SeqIO.parse(handle, "fasta"):
                queryseq = record.seq
        
        #print(queryseq)

        # make genbank record
        #s=Seq(str(queryseq),IUPAC.IUPACUnambiguousDNA())
        s=Seq(str(queryseq))
        newrec=SeqRecord(s)
        newrec.id= str(rec.query).split(" ",1)[0]
        if len(str(newrec.id))>15:
            newrec.id= str(rec.query)[0:16]
        if len(str(rec.query).split(" "))>1:
            newrec.description= str(rec.query).split(" ",1)[1]
        else:
            newrec.description= rec.query
        allfeatures=[]
        querylist=[0]*rec.query_length
        algs=rec.alignments
        # Get coverage of hits (mark them on a string of "0" representing the genome)
        for alg in algs:
            for hsp in alg.hsps:

                if float(hsp.expect)<float(user.userprofile.first_e_cutoff):
                    querystart=min(hsp.query_start,hsp.query_end)
                    queryend=max(hsp.query_start,hsp.query_end)
                    querylist[querystart-1:queryend]=(1+queryend-querystart)*[1]
                    #feature = SeqFeature(FeatureLocation(hsp.query_start,hsp.query_end), strand=int(hsp.frame[1]),type="firsthit")
                    feature = SeqFeature(FeatureLocation(hsp.query_start,hsp.query_end), type="firsthit")
                    feature.id=alg.hit_id
                    feature.qualifiers["hit"]=alg.hit_def
                    allfeatures.append(feature)
                    


        starts_and_ends=find_starts_ends(querylist)
        for st_end in starts_and_ends: 
        
            feature = SeqFeature(FeatureLocation(st_end[0],st_end[1]), type="footprint")
            total_footprint_nucleotides+=len(feature.location)
            allfeatures.append(feature)
            footprintseq=queryseq[st_end[0]:st_end[1]]
            footprint = Footprint.objects.create(start=int(st_end[0]), end=int(st_end[1]),sequence=footprintseq)
            genObj.footprints.add(footprint)
            genObj.save()

        newrec.features=allfeatures

        
        # Return the genome searhed (hit name), a genbank record, and empty string and filename(samplename) 

    return(newrec,total_footprint_nucleotides)


def find_starts_ends(querylist):
    lookingfor="start"
    results=[]
    fcounter=1
    currentstart=-1
    for i in querylist:
        if lookingfor=="start":
            if i==1:
                currentstart=fcounter
                lookingfor="end"
                fcounter+=1
                continue
        if lookingfor=="end":
            if i==0:
                results.append([currentstart,fcounter-1])
                lookingfor="start"
        fcounter+=1
    if lookingfor=="end":
        results.append([currentstart,len(querylist)])
    return results

def delete_inactive_temp_users():
    threshold = timezone.now() - timedelta(minutes=10)
    inactive_users = User.objects.filter(userprofile__user_type='temp', userprofile__last_active_time__lt=threshold)
    inactive_users.delete()

def getDatabaseAndView():
    dbsquares = genomeEntry.objects.all()
    return (dbsquares)






