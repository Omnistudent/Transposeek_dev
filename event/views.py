from django.shortcuts import render,redirect
from django.contrib.auth.models import User

from .models import genomeEntry

from .models import UserProfile
from .models import NCBIentry
from .models import NCBISubentry
from .models import Footprint
import random

import time
from django.contrib.auth import authenticate, login
import string
#from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta

from django.conf import settings

import os
from .models import ListItem
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Blast import NCBIXML
from Bio.Blast.Applications import NcbiblastxCommandline
from Bio.SeqFeature import SeqFeature, FeatureLocation

import subprocess
import io
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import gzip
import shutil
from itertools import zip_longest

#from django.http import HttpResponse



default_genome_dir=""

onerange=['5', '15', '25', '35', '45', '55', '65', '75', '85', '95', '105', '115']
range_list_names_global=['-5_5', '5_15', '15_25', '25_35', '35_45', '45_55', '55_65', '65_75', '75_85', '85_95', '95_105', '105_115']

ishit_headers=["name","start","end","length","id","type","isfamily","isgroup","is_score","is_expected","is_frame","is_perc_of_orf","is_origin"]
finalcsvheaders=["organism","nt covered by is","number of is"]

SEP="\t"




def help(request):
    return render(request,'event/help.html',
        {})

def managegenomes(request):
    user=request.user
    dbsquares = genomeEntry.objects.all()
    #ncbigenomes = NCBIentry.objects.all()
    #ncbigenomes = NCBIentry.objects.filter(contig_count="1")
    #ncbigenomes = NCBIentry.objects.filter(has_representative="YES", contig_count="1")
    #ncbigenomes = NCBIentry.objects.filter(has_representative="YES")
    
    try:
        currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
    except:
        currendir_listing = []





    currendir_listing_filt=filter_filenames(currendir_listing)
    ncbigenomes = NCBIentry.objects.filter(has_representative="YES").exclude(name__in=currendir_listing_filt)


    if request.method == 'POST':
        sent_action = request.POST.get('command')
        sent_answer = request.POST.get('answer')

        if sent_action == 'deletegenomes':
            print("sent_command deletegenomes")
            
            sent_answer = request.POST.get('answer').split(",")
            print(sent_answer)
            
            for i in sent_answer:
                genObj = genomeEntry.objects.filter(name=i).first()
                if genObj is not None:
                    genObj.delete()
                
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})

        
        # adds genome from the genome folder to the invesitgated_genomes
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

                    my_blast_files_dir=request.user.userprofile.blast_files_dir+"/"+cleanedname
                    if not os.path.exists(my_blast_files_dir):
                        os.makedirs(my_blast_files_dir)

                    genomeP = genomeEntry.objects.create(name=i, path=request.user.userprofile.current_genome_dir, extra='-', is_dir=dirinput,blast_results_file=my_blast_files_dir,work_files_dir=my_work_files_dir)
                    
            #returns the investigated_genomes database, the directory for the genome dir,the ncbi available datbse and the current genome directory
            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            currendir_listing_filt=filter_filenames(currendir_listing)
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})

        # Sets a new genome directory
        if sent_action == 'commitDirectory':
            print("sent_command commitdirectory")
            sent_path = request.POST.get('answer')
            print (sent_path)
            if os.path.isdir(sent_path):
                request.user.userprofile.current_genome_dir=sent_path
                currendir_listing = os.listdir(sent_path)
                request.user.userprofile.save()
            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})


        if sent_action == 'updateDatabaseInfo':
            print("sent_command updateDatabaseInfo")
            download_files_for_gc_minus_one(2000)
            """
            if os.path.isdir(sent_path):
                request.user.userprofile.current_genome_dir=sent_path
                currendir_listing = os.listdir(sent_path)
                request.user.userprofile.save()

            subentries = NCBISubentry.objects.filter(gc_percent=-1)
            """
           # ncbithing = NCBIentry.objects.filter(name=i).first()

            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            currendir_listing_filt=filter_filenames(currendir_listing)
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})



        if sent_action == 'download_genomes':
            print("sent_command download_genomes")
            #download_files_for_gc_minus_one(30000)
            print("_________________________________________")
            sent_path = request.POST.get('answer')
            sent_answer = request.POST.get('answer').split(",")

            for i in sent_answer:
                downloadRepresentativeGenome(i,request.user.userprofile.current_genome_dir)


            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            currendir_listing_filt=filter_filenames(currendir_listing)
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})
           
        #This part is not used, rebuilding for downloadandtreat
        if sent_action == 'dl_and_treat':
            sent_path = request.POST.get('answer')
            sent_answer = request.POST.get('answer').split(",")

            for i in sent_answer:
                downloadRepresentativeGenome(i,request.user.userprofile.current_genome_dir)
                
                cleanedname=remove_extension(i)
                cleanedname2=(i.replace("/",""))+".gb"
                existing_entry = genomeEntry.objects.filter(name=cleanedname2).first()
                

                if not existing_entry:
                    if os.path.isdir(request.user.userprofile.current_genome_dir+i):
                        dirinput="1"
                    else:
                        dirinput="0"
                    cleanedname=remove_extension(i)
                    my_work_files_dir=request.user.userprofile.work_files_dir+"/"+i.replace("/","")
                    if not os.path.exists(my_work_files_dir):
                        os.makedirs(my_work_files_dir)

                    my_blast_files_dir=request.user.userprofile.blast_files_dir+"/"+i.replace("/","")
                    if not os.path.exists(my_blast_files_dir):
                        os.makedirs(my_blast_files_dir)

                    genomeP = genomeEntry.objects.create(name=cleanedname2, path=request.user.userprofile.current_genome_dir, extra='-', is_dir=dirinput,blast_results_file=my_blast_files_dir,work_files_dir=my_work_files_dir)




                genObj = genomeEntry.objects.filter(name=cleanedname2).first()
               
                genomeFullPath=genObj.path+"/"+genObj.name
                print(genomeFullPath)


                contigs=prepareGenomeForBlast(genomeFullPath,genObj,cleanedname2,user)
                contigs=getGenomeInfo(genomeFullPath)

                genObj.contigs_num=contigs[0]
                genObj.genome_size=contigs[1]
                genObj.save()

                doblast(genomeFullPath,genObj,cleanedname2,user)

                dbsquares=getDatabaseAndView()
                analyseblast(genObj,cleanedname2,user)
                analyse_footprints(genObj,cleanedname2,user)
                analyse_results(genObj,cleanedname2,user)
            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            currendir_listing_filt=filter_filenames(currendir_listing)
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})


        if sent_action == 'updateDatabase':
            print("sent_command updatedatabase")
            sent_path = request.POST.get('answer')
    
            htmlfileloc = 'c:/Users/Eris/Documents/g/transposeek2/static/genomes_refseq_bacteria.html'

        # Read the HTML file
            NCBIentry.objects.all().delete()
            with open(htmlfileloc, 'r', encoding='utf-8') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')

                 #Find all the <a> tags
                a_tags = soup.find_all('a')

                # Extract the name and href attributes
                entries = []
                for a_tag in a_tags:
                    name = a_tag.text
                    link = a_tag['href']
                    entries.append((name, link))

                # Print the extracted entries
                for name, link in entries:
                    print(name)


                    entry = NCBIentry.objects.get_or_create(name=name, link=link,database="refseq")

            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            currendir_listing_filt=filter_filenames(currendir_listing)
            ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
            #return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbigenomes})
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})
    


    
    else:
        currendir_listing_filt=filter_filenames(currendir_listing)

        ncbi_exl_have=filter_genomes_view(currendir_listing_filt)
        #return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currentdir_listing_filt,'ncbigenomes':ncbigenomes})
        return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing_filt,'ncbigenomes':ncbi_exl_have,'genomedir':request.user.userprofile.current_genome_dir})

            
               
              
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
                    request.user.userprofile.save()
               

def downloadRepresentativeGenome(i,current_genome_dir):
    ncbithing = NCBIentry.objects.filter(name=i).first()
    response = requests.get(ncbithing.link+"/representative")
    response.raise_for_status() 
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    directory_listing = []
    for link in links:
        href = link.get('href')
        if href and not href.startswith('?'):
            directory_listing.append((link.text, href))
             
    if len(directory_listing)!=3:
        print("more than one file in representative dir")           

    for d in directory_listing:
      
        listingname=(d[0])
        if listingname=="Parent Directory":
            continue
        if listingname=="HHS Vulnerability Disclosure":
            continue

        url=ncbithing.link+"representative/"+listingname.replace("/","")+"/"+listingname.replace("/","")+"_genomic.fna.gz"
        tempdirname=current_genome_dir+"/temp/"+ncbithing.name+"/"
        if not os.path.exists(tempdirname):
            os.makedirs(tempdirname)

        local_filename = tempdirname+ncbithing.name.replace("/","")+"_genomic.fna.gz"
        download_and_ungzip_file(url, local_filename, local_filename)
        local_filename2 = tempdirname+ncbithing.name.replace("/","")+"_genomic.fna"
        numcontigs=concatenate_fasta_sequences(local_filename2, tempdirname+ncbithing.name.replace("/","")+".gb", tempdirname+ncbithing.name.replace("/","")+"_genomic2.fa")

        shutil.copy(tempdirname+ncbithing.name.replace("/","")+".gb", current_genome_dir+"/"+ncbithing.name.replace("/","")+".gb")
        shutil.rmtree(current_genome_dir+"/temp/")

    return numcontigs

def home(request):
    #load_questions_from_file()
    if not request.user.is_authenticated:

            # Generate a random username and password
        username10 = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

        # Create a new user with the generated username and password
        user = User.objects.create_user(username=username10, password=password)


   
        BASE_DIR2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        dbp1=os.path.join(settings.STATIC_URL, 'isdatabase/is_aa_30_nov2016.fa')
        blastplacestatic=os.path.join(settings.STATIC_URL, 'blastbin')
        resultsplacestatic=os.path.join(settings.STATIC_URL, 'results')
        
        blast1_resultsplacestatic=os.path.join(settings.STATIC_URL, 'blast1results')
        blast_analysis_placestatic=os.path.join(settings.STATIC_URL, 'blastanalysis/')
        analysed_gbfiles_placestatic=os.path.join(settings.STATIC_URL, 'final_results/')
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
        user_profile = UserProfile.objects.create(user=user,name=user,user_type='temp',
                                                  transposase_protein_database=dbp,
                                                  work_files_dir=resultplace,
                                                  blast_files_dir=blast1_resultplace,
                                                  blast_analysis_dir=blast_analysis_resultplace,
                                                  final_results_dir=analysed_gbfiles_place,
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




    if request.method == 'POST':
        sent_action = request.POST.get('command')
        sent_answer = request.POST.get('answer')

        print("sent action")
        print(sent_action)



        # Get the genome size and the number of contigs
        if sent_action == 'analyzefile':
            sent_answer = request.POST.get('answer')
            genObj = genomeEntry.objects.filter(name=sent_answer).first()           
            genomeFullPath=genObj.path+"/"+genObj.name
            contigs=getGenomeInfo(genomeFullPath)
            genObj.contigs_num=int(contigs[0])
            genObj.genome_size=int(contigs[1])
            genObj.save()
            contigs=prepareGenomeForBlast(genomeFullPath,genObj,sent_answer,user)
            genObj.contigs_num=contigs[0]
            genObj.genome_size=contigs[1]
            genObj.save()

            dbsquares=getDatabaseAndView()
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares})



        if sent_action == 'prepare':
            sent_answer = request.POST.get('answer')
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
            genomeFullPath=genObj.path+"/"+genObj.name
            contigs=prepareGenomeForBlast(genomeFullPath,genObj,sent_answer,user)
            genObj.contigs_num=contigs[0]
            genObj.genome_size=contigs[1]
            genObj.save()
            dbsquares=getDatabaseAndView()
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares})


        if sent_action == 'blast':
            print("sent_command blast")
            sent_answer = request.POST.get('answer')

            

         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            genomeFullPath=genObj.path+"/"+genObj.name



            contigs=prepareGenomeForBlast(genomeFullPath,genObj,sent_answer,user)
            contigs=getGenomeInfo(genomeFullPath)

            genObj.contigs_num=contigs[0]
            genObj.genome_size=contigs[1]
            genObj.save()

            doblast(genomeFullPath,genObj,sent_answer,user)

            dbsquares=getDatabaseAndView()
            analyseblast(genObj,sent_answer,user)
            analyse_footprints(genObj,sent_answer,user)
            analyse_results(genObj,sent_answer,user)
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares})

        if sent_action == 'analyseblast':
            print("sent_command analyse blast")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            #genomeFullPath=genObj.path+"/"+genObj.name
            analyseblast(genObj,sent_answer,user)

            dbsquares=getDatabaseAndView()
        
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares})
      
        if sent_action == 'make_footprint':
            print("sent_command make_footprint")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           
            analyse_footprints(genObj,sent_answer,user)
 
            dbsquares=getDatabaseAndView()
     
            sent_path=user.userprofile.current_genome_dir
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares})


        if sent_action == 'analyse_results':
            print("sent_command analyse_results")
            sent_answer = request.POST.get('answer')
         
            genObj = genomeEntry.objects.filter(name=sent_answer).first()
           

            analyse_results(genObj,sent_answer,user)


            dbsquares=getDatabaseAndView()
        
            sent_path=user.userprofile.current_genome_dir
            
            checkButtons()
            return render(request,'event/home.html',{'squaredb':dbsquares})



        file_list = ["test1","testt2"]#os.listdir(directory_path)
    
        items = []
        for file_name in file_list:
            item = ListItem(name=file_name)
            items.append(item)



        dbsquares=getDatabaseAndView()
        
        sent_path=user.userprofile.current_genome_dir
        return render(request,'event/home.html',{'squaredb':dbsquares})
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

        return render(request,'event/home.html',{'squaredb':dbsquares})



def download_file(url, local_filename):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Open a local file in write-binary mode
    with open(local_filename, 'wb') as file:
        # Iterate over the response in chunks
        for chunk in response.iter_content(chunk_size=8192):
            # Write the chunk to the file
            file.write(chunk)
    
    print(f"File downloaded: {local_filename}")

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

def create_bar_diagram(data, filename,large):
    # Extract data
    categories = list(data.keys())
    frequencies = list(data.values())
    
    # Plotting the bar chart
    fig, ax = plt.subplots(figsize=(1.2, 0.5))  # Set the figure size in inches (width=1.2in, height=0.5in)
    ax.bar(categories, frequencies, color='blue')
    
    # Remove x and y axis labels and title
    #ax.set_xticks([])
    #ax.set_yticks([])
    #ax.set_xlabel("")
    #ax.set_ylabel("")
    #ax.set_title("")
    
    if large==False:
        ax.axis('off')
    # Save the figure to a file
        plt.tight_layout()
        plt.savefig(filename+".png", dpi=100, bbox_inches='tight', transparent=True)
    if large==True:
        fig2,ax2=plt.subplots(figsize=(4, 2))  # Set the figure size in inches (width=1.2in, height=0.5in)
        ax2.bar(categories, frequencies, color='blue')
        # Save the figure to a file
        plt.tight_layout()
        ax2.axis('on')
        plt.savefig(filename+"_large.png", dpi=500, bbox_inches='tight', transparent=False)

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


def filter_genomes_view(dld_genomes):
    
    # Normalize filenames
    normalized_files = [normalize_name(filename) for filename in dld_genomes]
    
    # Retrieve all NCBIentry names and normalize them
    all_entries = NCBIentry.objects.all()
    normalized_entries = [normalize_name(entry.name) for entry in all_entries]

    # Filter genomes with has_representative="YES" and exclude normalized names
    ncbigenomes = NCBIentry.objects.filter(has_representative="YES").exclude(name__in=[entry.name for entry in all_entries if normalize_name(entry.name) in normalized_files])
    

    
    return ncbigenomes

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

    #Regular csv dir place, csvs are also placed in finalresults folder
    csv_dir=user.userprofile.is_list_csv_file_dir+"/"+genomename+"/"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    hit_csv_string=""
    for header in ishit_headers: 
        hit_csv_string+=header+SEP

    hit_csv_string+="\n" # Headers written, start writing data for contigs
    number_of_hits=0
    total_is_covered=0
    for feat in rec.features:
        number_of_hits+=1

        perc_of_orf="unknown"

        hit_qualifiers= ["is_name","family","group","score","expected","frame","perc_of_orf","origin","numorfs"]

        hit_csv_string+=str(feat.type)+SEP
        hit_csv_string+=str(feat.location.start)+SEP
        hit_csv_string+=str(feat.location.end)+SEP
        hit_csv_string+=str(1+abs(int(feat.location.start)-int(feat.location.end)))+SEP #length
        total_is_covered+=1+abs(int(feat.location.start)-int(feat.location.end))
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



        for hit_qual in feat.qualifiers.keys():
            hit_csv_string+=str(hit_qual)+":"+str(feat.qualifiers[hit_qual][0])+SEP

        hit_csv_string+="\n"


    # Headers for the summary csv
    total_csv_string="Genomesize,Contigs,total_is_hits,total_is_coverage,percentage_is_coverage"+SEP


    for ik in onerange:
        total_csv_string+=str(int(ik)-10)+"tolessthan"+str(ik)+SEP

    total_csv_string+="\n"

    total_csv_string+=str(genObj.genome_size)+SEP
    total_csv_string+=str(genObj.contigs_num)+SEP
    total_csv_string+=str(number_of_hits)+SEP
    total_csv_string+=str(total_is_covered)+SEP
    calc1=float(total_is_covered)/float(genObj.genome_size)
    total_csv_string+=str(round(calc1,2))+SEP

    # write data for IS lengths
    for uppervar in onerange:
        total_csv_string+=str(is_fraction_counts[uppervar])+SEP

    # make file name for files in csv dir
    csv_summary_dir=user.userprofile.is_list_csv_file_dir+"/"+genomename+"/"
    csv_summary_file=csv_summary_dir+genomename+"_summary.csv"

    # make file name for files in results dir
    csv_summary_results_dir=user.userprofile.final_results_dir+"/"+genomename
    csv_summary_results_file=csv_summary_results_dir+"/"+genomename+"_summary.csv"

    # write summary file to csv dir
    fh_csv_summary=open(csv_summary_file,"w")
    fh_csv_summary.write(total_csv_string)
    fh_csv_summary.close()

    # write summary file to csv dir
    fh_csv_summary=open(csv_summary_results_file,"w")
    fh_csv_summary.write(total_csv_string)
    fh_csv_summary.close()

    # write computed data to database genobject
    genObj.footprint_size=int(total_is_covered)
    genObj.footprint_perc=round(calc1,2)
    genObj.save()

    # make directory for final genbank file
    curatedfilename_dir=user.userprofile.final_results_dir+"/"+genomename
                

    if not os.path.exists(curatedfilename_dir):
        os.makedirs(curatedfilename_dir)

    gbfilenameout=curatedfilename_dir+"/"+remove_extension(genomename)+"_curated.gb"

    pic_dir=user.userprofile.is_frequency_pic_dir
    pic_file=pic_dir+"/"+genomename
    pic_file2=curatedfilename_dir+"/"+genomename


    blank_file=pic_dir+"blank.png"
    #create_blank_image(120, 50, blank_file)
      
    create_bar_diagram(is_fraction_counts,pic_file,False)
    create_bar_diagram(is_fraction_counts,pic_file2,True)


    genObj.is_frequency_pic=genomename+".png"
    genObj.save()

    file_start=remove_extension(genomename)
    my_blast_files_dir=user.userprofile.blast_files_dir+"/"+file_start



    csv_dir=user.userprofile.is_list_csv_file_dir+"/"+genomename+"/"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)


    csv_file=csv_dir+"/"+genomename+".csv"
    csv_file2=curatedfilename_dir+"/"+genomename+".csv"

    fho3=open(csv_file,"w")
    fho3.write(hit_csv_string)
    fho3.close()

    fho4=open(csv_file2,"w")
    fho4.write(hit_csv_string)
    fho4.close()
    return()

# Opens genome file in fasta or gb format, concatenates all record and writes a file _conc.fa to the workfiles directory
def prepareGenomeForBlast(genomeFullPath,genObj,genomename,user):
    file_end=genomename.split(".")[-1]
    file_start=genomename.split(".")[0]
    file_start=remove_extension(genomename)
    genbank_endings= ["gbk", "gb","gbff"]
    fasta_endings= ["fa", "fasta","fna"]
    genomeFullPath_fh=open(genomeFullPath,"r")
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

def normalize_name(name):
    """
    Normalize the name by removing trailing slashes and ".gb" extensions.
    """
    if name.endswith('/'):
        name = name.rstrip('/')
    if name.endswith('.gb'):
        name = name[:-3]
    return name

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


    curatedfilename_dir=user.userprofile.final_results_dir+"/"+genomename
                

    if not os.path.exists(remove_extension(curatedfilename_dir)):
        os.makedirs(remove_extension(curatedfilename_dir))
    gbfilenameout=remove_extension(curatedfilename_dir)+"/"+remove_extension(genomename)+"_cleaned.gb"
                
    genbank_output2=open(gbfilenameout,"w")
    SeqIO.write([newrec],genbank_output2,"genbank")
    genbank_output2.close()

    #register the location of the gb file in the database
    genob.analysed_gb_files=gbfilenameout
    genob.save()
    return newrec   

def parse_xml_file(sample,samplename,genObj,user):

    genObj.footprints.clear()
    total_footprint_nucleotides=0
    xmlfh=open(sample,"r")
    try:
        blast_records = list(NCBIXML.parse(xmlfh))	
    except:
        print("no file")
    xmlfh.close()
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

def download_and_ungzip_file(url, local_filename, output_folder):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Download the file in chunks and save it locally
    gz_file_path = os.path.join(output_folder, local_filename)
    with open(gz_file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    # Path for the decompressed file
    decompressed_file_path = os.path.join(output_folder, os.path.splitext(local_filename)[0])
    
    # Decompress the file
    with gzip.open(gz_file_path, 'rb') as f_in:
        with open(decompressed_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Optionally, remove the gzipped file after decompression
    #os.remove(gz_file_path)
    
    print(f"File downloaded and decompressed to: {decompressed_file_path}")




def download_file_as_bytes(url):
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    
    # Read the content directly into bytes
    file_content = response.content.decode('utf-8')
    
    return file_content

def check_directory_exists(url, directory_name):
    # Fetch the directory listing
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all the <a> tags (which represent directory and file links)
    links = soup.find_all('a')
    
    # Check if the specified directory exists in the links
    for link in links:
        if link.get('href') == directory_name:
            return True
    return False

def concatenate_fasta_sequences(fasta_file, output_genbank_file, output_fasta_file):
    concatenated_sequence = ""
    contig_count = 0
    record_id = None
    record_description = None

    # Parse the input FASTA file and concatenate sequences
    with open(fasta_file, "r") as fa_file:
        for record in SeqIO.parse(fa_file, "fasta"):
            concatenated_sequence += str(record.seq)
            contig_count += 1
            if record_id is None:
                record_id = record.id
                record_description = record.description

    # Create a new SeqRecord for the concatenated sequence with necessary annotations
    concatenated_record = SeqRecord(
        Seq(concatenated_sequence),
        id=record_id,
        description="Concatenated contigs",
        annotations={"molecule_type": "DNA"}
    )

    # Write the concatenated sequence to a new GenBank file
    with open(output_genbank_file, "w") as gb_output:
        SeqIO.write(concatenated_record, gb_output, "genbank")

    # Write the concatenated sequence to a new FASTA file
    with open(output_fasta_file, "w") as fasta_output:
        SeqIO.write(concatenated_record, fasta_output, "fasta")
    print("concatenated "+str(contig_count)+" contigs")
    return contig_count

def downloadgenomes(request):
    dbsquares = genomeEntry.objects.all()
    #ncbigenomes = NCBIentry.objects.all()
    #ncbigenomes = NCBIentry.objects.exclude(gc_percent="-1")
    ncbigenomes = NCBIentry.objects.filter(contig_count="1")
    try:
        currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
    except:
        currendir_listing = []


    if request.method == 'POST':
        sent_action = request.POST.get('command')
        sent_answer = request.POST.get('answer')

        if sent_action == 'deletegenomes':
            print("sent_command deletegenomes")
            print("sent answer:"+str(sent_answer))
            sent_answer = request.POST.get('answer').split(",")
            
            for i in sent_answer:
                genObj = genomeEntry.objects.filter(name=i).first()
                if genObj is not None:
                    genObj.delete()
                

            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})

        
        
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
                    
    
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})

        if sent_action == 'commitDirectory':
            print("sent_command commitdirectory")
            sent_path = request.POST.get('answer')
            print (sent_path)
            if os.path.isdir(sent_path):
                request.user.userprofile.current_genome_dir=sent_path
                currendir_listing = os.listdir(sent_path)
                request.user.userprofile.save()


            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})
        
        if sent_action == 'download_genomes':
            print("sent_command download_genomes")
            sent_path = request.POST.get('answer')
            sent_answer = request.POST.get('answer').split(",")

            for i in sent_answer:
                ncbithing = NCBIentry.objects.filter(name=i).first()
                response = requests.get(ncbithing.link+"/representative")
                response.raise_for_status() 
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a')
                directory_listing = []
                for link in links:
                    href = link.get('href')
                    if href and not href.startswith('?'):
                        directory_listing.append((link.text, href))

                ncbithing.subentries.all().delete()
                ncbithing.save()
                for d in directory_listing:
                    listingname=(d[0])
                    if listingname=="Parent Directory":
                        continue
                    if listingname=="HHS Vulnerability Disclosure":
                        continue
                    #print(listingname)

                    subentry= NCBISubentry.objects.create(name=d[0], link=d[1])
                    ncbithing.subentries.add(subentry)
                    ncbithing.save()

                for l in ncbithing.subentries.all():
                    print(l.name)  
                    tempdirname=request.user.userprofile.current_genome_dir+"/temp/"+ncbithing.name+l.name
                    if not os.path.exists(tempdirname):
                        os.makedirs(tempdirname)
                    url=ncbithing.link+"representative/"+l.link+l.name.replace("/","")+"_genomic.fna.gz"



                # Local filename to save the downloaded file
                    local_filename = tempdirname+l.name.replace("/","")+"_genomic.fna.gz"

                # Call the function to download the file
                    print("local")
                    print(local_filename)
                    #download_file(url, local_filename)
                    lastfilename=(ncbithing.name.replace("/",""))
                    print(lastfilename)
                    print("lastfilename------------------------")
                    print(tempdirname+lastfilename)
                    download_and_ungzip_file(url, local_filename, local_filename)
                    local_filename2 = tempdirname+l.name.replace("/","")+"_genomic.fna"
                    numcontigs=concatenate_fasta_sequences(local_filename2, tempdirname+lastfilename+".gb", tempdirname+l.name.replace("/","")+"_genomic2.fa")
                    #numcontigs=concatenate_contigs(local_filename, tempdirname+l.name.replace("/","")+"_genomic2.gb", tempdirname+l.name.replace("/","")+"_genomic2.fa")
                    print(numcontigs)
                    print("numcontigs")
                    print(tempdirname+lastfilename+".gb")
                    print(request.user.userprofile.current_genome_dir+lastfilename+".gb")
                    shutil.copy(tempdirname+lastfilename+".gb", request.user.userprofile.current_genome_dir+"/"+lastfilename+".gb")
                    #copy to request.user.userprofile.current_genome_dir)
            """
                    print(request.user.userprofile.current_genome_dir)
            """
            print (sent_path)
            if os.path.isdir(sent_path):
                request.user.userprofile.current_genome_dir=sent_path
                currendir_listing = os.listdir(sent_path)
                request.user.userprofile.save()

            response = requests.get(ncbithing.link+"/representative")
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a')
            directory_listing = []
            for link in links:
                href = link.get('href')
                if href and not href.startswith('?'):
                    directory_listing.append((link.text, href))
            for d in directory_listing:
                listingname=(d[0])
                if listingname=="Parent Directory":
                    continue
                if listingname=="HHS Vulnerability Disclosure":
                    continue
                #print(listingname)

                subentry= NCBISubentry.objects.create(name=d[0], link=d[1])
                ncbithing.subentries.add(subentry)
                ncbithing.save()
            for l in ncbithing.subentries.all():
                print(l.name)  
                url=ncbithing.link+"latest_assembly_versions/"+l.link+l.name.replace("/","")+"_genomic.fna.gz"

                print("fffffffffffffff")
                tempdirname=request.user.userprofile.current_genome_dir+"/temp/"+ncbithing.name+l.name
                if not os.path.exists(tempdirname):
                    os.makedirs(tempdirname)


                # Local filename to save the downloaded file
                local_filename = tempdirname+l.name.replace("/","")+"_genomic.fna.gz"

                # Call the function to download the file
                print("local")
                print(local_filename)
                download_file(url, local_filename)

                download_and_ungzip_file(url, local_filename, local_filename+"x")

            """
            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})
        
        if sent_action == 'updateDatabase':
            print("sent_command commitdirectory")
            sent_path = request.POST.get('answer')
    
            htmlfileloc = 'c:/Users/Eris/Documents/g/transposeek2/static/genomes_genbank_bacteria.html'

        # Read the HTML file
            NCBIentry.objects.all().delete()
            with open(htmlfileloc, 'r', encoding='utf-8') as file:
                html_content = file.read()
                


                soup = BeautifulSoup(html_content, 'html.parser')

                 #Find all the <a> tags
                a_tags = soup.find_all('a')

                # Extract the name and href attributes
                entries = []
                for a_tag in a_tags:
                    name = a_tag.text
                    link = a_tag['href']
                    entries.append((name, link))

                # Print the extracted entries
                for name, link in entries:
                    #print(name)
                    entry = NCBIentry.objects.get_or_create(name=name, link=link)###"""

            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})
    


            #currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            #return render(request,'event/managegenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})
        if sent_action == 'dl_genomes':
            sent_answer = request.POST.get('answer').split(",")
            print (sent_answer)
            print ("sent_answer")
            for i in sent_answer:
                print(i)
                sent_path = request.POST.get('answer')
                print("dlgenomes")
                print (sent_path)
             
                ncbithing = NCBIentry.objects.filter(name=i).first()
                print(ncbithing.name)
                print("-------------------------")
                #ncbithing.subentries.all().delete()
                ncbithing.save()
                print(ncbithing.link)

                info=str(download_file_as_bytes(ncbithing.link+"/assembly_summary.txt"))
                headlines=info.split("\n")[1]
                headlines2=headlines.split("\t")
                info=info.split("\n")[2]
                info2=info.split("\t")

                dictionary = {key: value for key, value in zip_longest(headlines2, info2, fillvalue=None)}
                print(dictionary)


                ncbithing.assembly_accession=dictionary['#assembly_accession']
                ncbithing.organism_name=dictionary['organism_name']
                ncbithing.genome_rep=dictionary['genome_rep']
                ncbithing.assembly_level=dictionary['assembly_level']
                ncbithing.asm_name=dictionary['asm_name']
                ncbithing.gbrs_paired_asm=dictionary['gbrs_paired_asm']
                ncbithing.ftp_path=dictionary['ftp_path']
                ncbithing.assembly_type=dictionary['assembly_type']
                ncbithing.genome_size=dictionary['genome_size']
                ncbithing.gc_percent=dictionary['gc_percent']
                ncbithing.genome_size_ungapped=dictionary['genome_size_ungapped']
                ncbithing.replicon_count=dictionary['replicon_count']
                ncbithing.scaffold_count=dictionary['scaffold_count']
                ncbithing.contig_count=dictionary['contig_count']
                ncbithing.seq_rel_date=dictionary['seq_rel_date']

                ncbithing.save()
                
                has_representative=check_directory_exists(ncbithing.link, 'representative/')
                if (has_representative):
                    ncbithing.has_representative="YES"
                else:
                    ncbithing.has_representative="NO"

                ncbithing.save()

                #for genome in sent_path:
                    #response = requests.get(genome)
                #    print (genome)
                #    ncbithing = NCBIentry.objects.filter(name=genome).first()  
                    #response.raise_for_status() 
                    #soup = BeautifulSoup(response.content, 'html.parser')
                    #links = soup.find_all('a')

                """
            #htmlfileloc=os.path.join(settings.STATIC_URL, 'Index of_genomes_genbank_bacteria.html')
            htmlfileloc = 'c:/Users/Eris/Documents/g/transposeek2/static/genomes_genbank_bacteria.html'

        # Read the HTML file
            NCBIentry.objects.all().delete()
            with open(htmlfileloc, 'r', encoding='utf-8') as file:
                html_content = file.read()
                


                soup = BeautifulSoup(html_content, 'html.parser')

                 #Find all the <a> tags
                a_tags = soup.find_all('a')

                # Extract the name and href attributes
                entries = []
                for a_tag in a_tags:
                    name = a_tag.text
                    link = a_tag['href']
                    entries.append((name, link))

                # Print the extracted entries
                for name, link in entries:
                    #print(name)
                    entry = NCBIentry.objects.get_or_create(name=name, link=link)###"""

            currendir_listing = os.listdir(request.user.userprofile.current_genome_dir)
            return render(request,'event/downloadgenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})
    
    else:
        
        return render(request,'event/downloadgenomes.html',{'squaredb':dbsquares,'currentdir_listing':currendir_listing,'ncbigenomes':ncbigenomes})



#{'#assembly_accession': 'GCF_027716165.1', 'bioproject': 'PRJNA224116', 'biosample': 'SAMN32411437', 'wgs_master': 'JAQFUK000000000.1', 'refseq_category': 'na', 'taxid': '3018118', 'species_taxid': '3018118', 'organism_name': 'Bacillus cereus group sp. Bc032', 'infraspecific_name': 'strain=Bc032', 'isolate': 'na', 'version_status': 'latest', 'assembly_level': 'Contig', 'release_type': 'Major', 'genome_rep': 'Full', 'seq_rel_date': '2023/01/10', 'asm_name': 'ASM2771616v1', 'asm_submitter': 'City University of Hong Kong Shenzhen Research Institute', 'gbrs_paired_asm': 'GCA_027716165.1', 'paired_asm_comp': 'identical', 'ftp_path': 'https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/027/716/165/GCF_027716165.1_ASM2771616v1', 'excluded_from_refseq': 'na', 'relation_to_type_material': 'na', 'asm_not_live_date': 'na', 'assembly_type': 'haploid', 'group': 'bacteria', 'genome_size': '5581965', 'genome_size_ungapped': '5581965', 'gc_percent': '35.000000', 'replicon_count': '0', 'scaffold_count': '249', 'contig_count': '249', 'annotation_provider': 'NCBI RefSeq', 'annotation_name': 'NCBI Prokaryotic Genome Annotation Pipeline (PGAP)', 'annotation_date': '2024/02/23', 'total_gene_count': '5837', 'protein_coding_gene_count': '5431', 'non_coding_gene_count': '63', 'pubmed_id': 'na'}


def filter_filenames(filenames):
    # Retrieve all existing geneitem names from the database
    existing_names = genomeEntry.objects.values_list('name', flat=True)
    # Filter the filenames to exclude those present in the database
    #filtered_filenames = [filename for filename in filenames if filename not in existing_names]
    filtered_filenames = [filename for filename in filenames if filename not in existing_names and filename != "temp"]
    
    return filtered_filenames


#Only downloads the summary file
def download_files_for_gc_minus_one(duration_minutes=5):
    start_time = time.time()
    count=0
    max_duration = duration_minutes * 60  # Convert minutes to seconds
            #subentries = NCBISubentry.objects.filter(gc_percent=-1)
    subentries = NCBIentry.objects.filter(gc_percent="-1")
    #subentries = NCBIentry.objects.all()
    # Get all NCBISubentry instances with gc_percent == -1
    #subentries = NCBISubentry.objects.filter(gc_percent=-1)

    for subentry in subentries:
        # Check if the maximum duration has been reached
        if time.time() - start_time > max_duration:
            print("Time limit reached. Stopping the download process.")
            break

        try:

            info=str(download_file_as_bytes(subentry.link+"/assembly_summary.txt"))
            headlines=info.split("\n")[1]
            headlines2=headlines.split("\t")
            info=info.split("\n")[2]
            info2=info.split("\t")

            dictionary = {key: value for key, value in zip_longest(headlines2, info2, fillvalue=None)}
            #print(dictionary)
            count+=1

            subentry.assembly_accession=dictionary['#assembly_accession']
            subentry.organism_name=dictionary['organism_name']
            subentry.genome_rep=dictionary['genome_rep']
            subentry.assembly_level=dictionary['assembly_level']
            subentry.asm_name=dictionary['asm_name']
            subentry.gbrs_paired_asm=dictionary['gbrs_paired_asm']
            subentry.ftp_path=dictionary['ftp_path']
            subentry.assembly_type=dictionary['assembly_type']
            subentry.genome_size=dictionary['genome_size']
            subentry.gc_percent=dictionary['gc_percent']
            subentry.genome_size_ungapped=dictionary['genome_size_ungapped']
            subentry.replicon_count=dictionary['replicon_count']
            subentry.scaffold_count=dictionary['scaffold_count']
            subentry.contig_count=dictionary['contig_count']
            subentry.seq_rel_date=dictionary['seq_rel_date']
            subentry.refseq_category=dictionary['refseq_category']
            subentry.taxid=dictionary['taxid']
            subentry.species_taxid=dictionary['species_taxid']
            subentry.infraspecific_name=dictionary['infraspecific_name']
            subentry.isolate=dictionary['isolate']
            subentry.version_status=dictionary['version_status']
            subentry.release_type=dictionary['release_type']
            subentry.asm_submitter=dictionary['asm_submitter']
            subentry.gbrs_paired_asm=dictionary['gbrs_paired_asm']
            subentry.paired_asm_comp=dictionary['paired_asm_comp']
            subentry.excluded_from_refseq=dictionary['excluded_from_refseq']
            subentry.relation_to_type_material=dictionary['relation_to_type_material']
            subentry.group=dictionary['group']
            subentry.asm_not_live_date=dictionary['asm_not_live_date']
            subentry.relation_to_type_material=dictionary['relation_to_type_material']
            subentry.genome_size_ungapped=dictionary['genome_size_ungapped']
            subentry.annotation_provider=dictionary['annotation_provider']
            subentry.annotation_name=dictionary['annotation_name']
            subentry.annotation_date=dictionary['annotation_date']
            subentry.total_gene_count=dictionary['total_gene_count']
            subentry.protein_coding_gene_count=dictionary['protein_coding_gene_count']
            subentry.non_coding_gene_count=dictionary['non_coding_gene_count']
            subentry.pubmed_id=dictionary['pubmed_id']

            subentry.save()
            
            has_representative=check_directory_exists(subentry.link, 'representative/')
            if (has_representative):
                subentry.has_representative="YES"
            else:
                subentry.has_representative="NO"

            subentry.save()
            #response = requests.get(subentry.link, stream=True)
            #response.raise_for_status()  # Ensure the request was successful

            # Extract filename from URL
            #filename = subentry.link.split('/')[-1]

            # Save the file
            #with open(filename, 'wb') as file:
             #   for chunk in response.iter_content(chunk_size=8192):
            #        file.write(chunk)
            
            print(f"Successfully downloaded from {subentry.link}")

        except requests.RequestException as e:
            print(f"Failed to download {subentry.link}: {e}")
    print(count)
               