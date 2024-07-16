from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event
from .models import Square
import random
from django.http import HttpResponse

def grid(request):
    grid_size = 20
    square_size = 30
    myrange=range(0,20)
    #squares = [(i, j) for i in range(grid_size) for j in range(grid_size)]
    squares=get_squares()
    dbsquares = Square.objects.filter(image="event/image.png")
    dbsquares = Square.objects.all()
    if request.method == 'POST':
        #square_id = request.POST.get('square_id')
        startnum=int(request.POST.get('x'))
        x=str(int(startnum/grid_size))
        x = str(request.POST.get('x'))
        y = str(startnum%grid_size)
        #x=10
        
        #Square.objects.create(x=x, y=y)
        
        Square.objects.create(x=x,y=y,name='sea2',image="event/image.png")

    return render(request, 'event/grid.html', {'myrange':myrange,'dbsquares':dbsquares,'squares': squares, 'square_size': square_size}) 

def get_squares():
    squares = []
    for x in range(20):
        row = []
        for y in range(20):
            try:
                square = Square.objects.get(x=x, y=y)
                image_name = square.image
            except Square.DoesNotExist:
                image_name = 'event/null.png'
            squares.append(image_name)
            #row.append(image_name)
        #squares.append(row)
        #print(squares)
    print(squares)
    return squares


def grid2(request):
    # Retrieve all Square objects from the database
    squares = Square.objects.all()

    # Pass the squares to the template
    return render(request, 'event/grid.html', {'squares': squares})

def click(request):
    if request.method == 'POST':
        x = '2'
        y = '2'
        Square.objects.create(x=x, y=y)
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error'})
     

def all_events(request):
    event_list=Event.objects.all()
    return render(request,'event/event_list.html',
        {'event_list':event_list})


def home(request,year=datetime.now().year,month="March"):
    name="Theo"
    month=month.title()
    month_number=list(calendar.month_name).index(month)
    month_number=int(month_number)

    cal=HTMLCalendar().formatmonth(
        year,
        month_number)

    #now=datetime.now()
    #current_year=now.year

    return render(request,
    'event/home.html',{
        "name":name,
        "year":year,
        "month":month,
        "month_number":month_number,
        "cal":cal,
    })