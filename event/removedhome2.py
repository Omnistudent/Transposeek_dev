def home2(request):
    #delete_inactive_temp_users()
    if not request.user.is_authenticated:

            # Generate a random username and password
        username10 = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

        # Create a new user with the generated username and password
        user = User.objects.create_user(username=username10, password=password)
        question = Question.objects.filter(name='Correct_1').order_by('?').first()
        user_profile = UserProfile.objects.create(user=user,name=user,x='0',y='0',xpos=5,ypos=5,pending_xpos=0,pending_ypos=0,correct_answers=0,wrong_answers=0,question=question,user_type='temp',mode='move')
        user.userprofile=user_profile

        # Authenticate and log in the user
        user = authenticate(request, username=username10, password=password)

        # Set square to be occupied by user
        beginsquare = Square.objects.get(x=5, y=5)
        beginsquare.occupants3.add(user.userprofile)
        beginsquare.save()
        login(request, user)

    if request.method == 'POST':
        grid_size_x = 11
        grid_size_y = 11
        square_size = 30
        grid_extend=5
    
        user=request.user

        myrange_x=range(0,grid_size_x)
        myrange_y=range(0,grid_size_y)

        square_str = request.POST.get('square')
        dropdown_str = request.POST.get('dropdown_value')
        square_str2 = request.POST.get('square2')

        # Get x y of square, or mode
        x, y = square_str.split('*')
        print('y: '+ str(x))
        print('x: '+ str(y))

        if x=='answer':
            print("answer")
            print(y)
            print(user.userprofile.question.answer1_swedish)
            right_answer=user.userprofile.question.answer1_swedish
            ############################
            # Correct answer
            ############################
            if right_answer == y:

                # increment right answers
                user.userprofile.correct_answers+=1

                # delete from starting square
                startsquare = Square.objects.get(y=str(user.userprofile.ypos),x=str(user.userprofile.xpos))
                startsquare.occupants3.remove(user.userprofile)
                startsquare.save()

                # add userprofile to end square
                endsquare = Square.objects.get(x=user.userprofile.pending_xpos, y=user.userprofile.pending_ypos)
                endsquare.occupants3.add(user.userprofile)
                endsquare.save()
                
                # get moved direction
                movedy,movedx=getmovedir(user.userprofile.xpos,user.userprofile.ypos,user.userprofile.pending_xpos,user.userprofile.pending_ypos)

                # set new userprofile coordinates
                user.userprofile.xpos=user.userprofile.pending_xpos
                user.userprofile.ypos=user.userprofile.pending_ypos
                user.userprofile.pending_xpos=0
                user.userprofile.pending_ypos=0
                user.userprofile.save()

                # adjust view
                #x seems to react on move y
                if movedx==1:
                    temp=user.userprofile.x
                    user.userprofile.x=temp+1
                    user.userprofile.save()
                if movedx==-1:
                    temp=user.userprofile.x
                    user.userprofile.x=temp-1
                    user.userprofile.save()
                if movedy==-1:
                    temp=user.userprofile.y
                    user.userprofile.y=temp-1
                    user.userprofile.save()
                if movedy==1:
                    temp=user.userprofile.y
                    user.userprofile.y=temp+1
                    user.userprofile.save()

                # get squares between view and view+grid_size
                myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
                myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
                #squares=get_squares(myrange_x,myrange_y)

                # compute the same things as above?
                startx = int(user.userprofile.x)
                stopx = int(user.userprofile.x)+grid_size_x
                starty = int(user.userprofile.y)
                stopy = int(user.userprofile.y)+grid_size_y

                charsx = [str(i) for i in range(startx, stopx)]
                charsy = [str(i) for i in range(starty, stopy)]
                #charsx = [str(i) for i in myrange_x]
                #charsy = [str(i) for i in myrange_y]
                #dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
                dbsquares = Square.objects.filter(y__in=charsx,x__in=charsy)
                #dbsquares = Square.objects.all()
                #square_dict = {f"{square.x}*{square.y}": square for square in dbsquares}
                
                question = Question.objects.filter(name='Correct_1').order_by('?').first()
                user.userprofile.question=question
                user.userprofile.save()
                #question = Question.objects.filter(difficulty__gte=0).order_by('?').first()
                answers = [question.answer1_swedish, question.answer2_swedish, question.answer3_swedish, question.answer4_swedish]
                shuffle(answers)  # shuffles the answers randomly
                return render(request, 'event/home2.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'dbsquares':dbsquares, 'square_size': square_size,'question':question,'answers':answers})


            else:
                print('wrong')
                user.userprofile.wrong_answers+=1
                user.userprofile.save()

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
                dbsquares = Square.objects.filter(y__in=charsx,x__in=charsy)
                #dbsquares = Square.objects.all()
                #square_dict = {f"{square.x}*{square.y}": square for square in dbsquares}
                question = Question.objects.filter(name='Wrong_1').order_by('?').first()
                user.userprofile.question=question
                user.userprofile.save()
                answers = [question.answer1_swedish, question.answer2_swedish, question.answer3_swedish, question.answer4_swedish]
                return render(request, 'event/home2.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'dbsquares':dbsquares, 'square_size': square_size,'question':question,'answers':answers})

        if user.userprofile.mode=="move":
            question = Question.objects.filter(difficulty__lte=2,area1='general').order_by('?').first()

            ###############
            # Qustions set
            ###############
            if moveallowed(user.userprofile.xpos,x,user.userprofile.ypos,y):
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

                #charsx = [str(i) for i in range(startx-grid_extend, stopx+grid_extend)]
                #charsy = [str(i) for i in range(starty-grid_extend, stopy+grid_extend)]

                charsx = [str(i) for i in range(startx, stopx)]
                charsy = [str(i) for i in range(starty, stopy)]
                #dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
                dbsquares = Square.objects.filter(y__in=charsx,x__in=charsy)
                #dbsquares = Square.objects.all()
                #square_dict = {f"{square.x}*{square.y}": square for square in dbsquares}
                    #################
                    # Question made
                    #################
                #question = Question.objects.filter(difficulty__lte=1).order_by('?').first()
                question = Question.objects.exclude(area1='utility').filter(difficulty__lte=3).order_by('?').first()
                answers = [question.answer1_swedish, question.answer2_swedish, question.answer3_swedish, question.answer4_swedish]
                shuffle(answers)  # shuffles the answers randomly
                user.userprofile.question=question
                user.userprofile.save()

                return render(request, 'event/home2.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'dbsquares':dbsquares, 'square_size': square_size,'question':question,'answers':answers})


    grid_size_x = 11
    grid_size_y = 11
    square_size = 30
    user_profile = request.user.userprofile
    user_profile.last_active_time = timezone.now()
    user_profile.save()
    grid_extend=5
    
    
    myrange_x=range(0,grid_size_x)
    myrange_y=range(0,grid_size_y)
    user = request.user
    myrange_x=range(user.userprofile.x,int(user.userprofile.x)+grid_size_x)
    myrange_y=range(user.userprofile.y,int(user.userprofile.y)+grid_size_y)
    squares=get_squares(myrange_x,myrange_y)
       
    startx = int(user.userprofile.x)
    stopx = int(user.userprofile.x)+grid_size_x
    starty = int(user.userprofile.y)
    stopy = int(user.userprofile.y)+grid_size_y

    charsx = [str(i) for i in range(startx, stopx+grid_extend)]
    charsy = [str(i) for i in range(starty, stopy+grid_extend)]

    charsx = [str(i) for i in range(startx-grid_extend, stopx+grid_extend)]
    charsy = [str(i) for i in range(starty-grid_extend, stopy+grid_extend)]
    #dbsquares = Square.objects.filter(x__in=charsx,y__in=charsy)
    dbsquares = Square.objects.filter(y__in=charsx,x__in=charsy)
    #dbsquares = Square.objects.all()
    #square_dict = {f"{int(square.y)}-{int(square.x)}": square for square in dbsquares}

    try:
        question = user.userprofile.question
    except:
        question = Question.objects.exclude(area1='utility').filter(difficulty__lte=3).order_by('?').first()
    answers = [question.answer1_swedish, question.answer2_swedish, question.answer3_swedish, question.answer4_swedish]
    return render(request, 'event/home2.html', {'myrange_x':myrange_x,'myrange_y':myrange_y,'dbsquares':dbsquares, 'square_size': square_size,'question':question,'answers':answers})