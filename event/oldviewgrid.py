def grid(request):

    grid_size_x = 21
    grid_size_y = 21
    square_size = 30
    grid_extend=10
    
    user=request.user

    myrange=range(0,21)
    myrange_x=range(0,21)
    myrange_y=range(0,21)
    
    if request.method == 'POST':
        
        square_str = request.POST.get('square')
        dropdown_str = request.POST.get('dropdown_value')
        square_str2 = request.POST.get('square2')

        # Get x y of square, or mode
        x, y = square_str.split('*')
        print('y'+str(x))
        print('x'+str(y))
        if x=='answer':
            pass

        elif x=='changemode':
 
            user.userprofile.mode=dropdown_str
            user.userprofile.save()

        elif x=='nav':

            if y=='x+1':
                temp=user.userprofile.x
                user.userprofile.x=temp+1
                user.userprofile.save()
                myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
                myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
            if y=='x-1':
                temp=user.userprofile.x
                user.userprofile.x=temp-1
                user.userprofile.save()
                myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
                myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
            if y=='y+1':
                temp=user.userprofile.y
                user.userprofile.y=temp+1
                user.userprofile.save()
                myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
                myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
            if y=='y-1':
                temp=user.userprofile.y
                user.userprofile.y=temp-1
                user.userprofile.save()
                myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
                myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)                    

            startx = int(user.userprofile.x)
            stopx = int(user.userprofile.x)+grid_size_x
            starty = int(user.userprofile.y)
            stopy = int(user.userprofile.y)+grid_size_y

            charsx = [str(i) for i in range(startx, stopx)]
            charsy = [str(i) for i in range(starty, stopy)]
            #dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
            dbsquares = Square.objects.filter(y__in=charsx,x__in=charsy)
            #dbsquares = Square.objects.all()
       
            #question = Question.objects.filter(difficulty__lte=1).order_by('?').first()
            question = Question.objects.filter(name='Correct_1').order_by('?').first()
            answers = [question.answer1_swedish, question.answer2_swedish, question.answer3_swedish, question.answer4_swedish]
            shuffle(answers)  # shuffles the answers randomly
            return render(request, 'event/grid.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'dbsquares':dbsquares, 'square_size': square_size,'question':question,'answers':answers}) 
       

        else:
            #########################
            #  wants to move
            #########################
            if user.userprofile.mode=="move":
                question = Question.objects.filter(name='Correct_1').order_by('?').first()
                #question = Question.objects.filter(difficulty__lte=2,area1='general').order_by('?').first()

                ###############
                # Qustions set - shouldnt be in grid
                ###############
                #if moveallowed(user.userprofile.xpos,x,user.userprofile.ypos,y):
                if False:

                    user.userprofile.pending_xpos=x
                    user.userprofile.pending_ypos=y
                    user.userprofile.question=question
                    user.userprofile.save()

                    myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
                    myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
                    squares=get_squares(myrange_x,myrange_y)

                    startx = int(user.userprofile.x)
                    stopx = int(user.userprofile.x)+grid_size_x
                    starty = int(user.userprofile.y)
                    stopy = int(user.userprofile.y)+grid_size_y

                    charsx = [str(i) for i in range(startx-3, stopx+2)]
                    charsy = [str(i) for i in range(starty-3, stopy+2)]
                    #dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
                    dbsquares = Square.objects.all()
                    #square_dict = {f"{square.x}*{square.y}": square for square in dbsquares}
                    #################
                    # Question made
                    #################
                    question = user.userprofile.question
                    answers = [question.answer1_swedish, question.answer2_swedish, question.answer3_swedish, question.answer4_swedish]
                    shuffle(answers)  # shuffles the answers randomly
                    user.userprofile.question=question
                    user.userprofile.save()

                    return render(request, 'event/home.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'myrange':myrange,'dbsquares':dbsquares,'squares': squares, 'square_size': square_size,'question':question,'answers':answers})





            elif user.userprofile.mode=='paint sea':
                try:
                    square = Square.objects.get(x=x, y=y)
                except Square.DoesNotExist:
                    square = Square.objects.create(x=x, y=y, name='sea4', image='sea.png',)

            elif user.userprofile.mode=='paint land':
                try:
                    square = Square.objects.get(x=x, y=y)
                except Square.DoesNotExist:
                    square = Square.objects.create(x=x, y=y, name='land1', image='land.png',)

            elif user.userprofile.mode=='delete':
                try:
                    square = Square.objects.get(x=x, y=y)
                    square.delete()
                except Square.DoesNotExist:
                    print('no square at there')

            myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
            myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
            squares=get_squares(myrange_x,myrange_y)

            startx = int(user.userprofile.x)
            stopx = int(user.userprofile.x)+grid_size_x
            starty = int(user.userprofile.y)
            stopy = int(user.userprofile.y)+grid_size_y

            charsx = [str(i) for i in range(startx, stopx)]
            charsy = [str(i) for i in range(starty, stopy)]
            #dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
            dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
            #dbsquares = Square.objects.all()

        return redirect('grid')
    

    else:

        user = request.user
        myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
        myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
        squares=get_squares(myrange_x,myrange_y)
       
        startx = int(user.userprofile.x)
        stopx = int(user.userprofile.x)+grid_size_x
        starty = int(user.userprofile.y)
        stopy = int(user.userprofile.y)+grid_size_y

        charsx = [str(i) for i in range(startx, stopx)]
        charsy = [str(i) for i in range(starty, stopy)]
        dbsquares = Square.objects.filter(y__in=charsx,x__in=charsy)
        #dbsquares = Square.objects.all()
        #square_dict = {f"{int(square.y)}-{int(square.x)}": square for square in dbsquares}
        
      
        #question = Question.objects.filter(difficulty__gte=0).order_by('?').first()
        question = Question.objects.filter(name='Correct_1').order_by('?').first()
        return render(request, 'event/grid.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'dbsquares':dbsquares,'square_size': square_size,'question':question}) 
        #return render(request, 'event/grid.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'myrange':myrange,'dbsquares':dbsquares,'squares': squares, 'square_size': square_size,'dbdic':square_dict}) 
