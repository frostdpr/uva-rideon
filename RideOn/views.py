from django.shortcuts import render

'''
View function for the home page of the website
'''
def index(request):
    return render(request, 'RideOn/index.html')