from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.views import generic
from django.views.generic.list import ListView

from django.urls import reverse
from django.utils import timezone

from drives.models import Drive, create_drive, Location, RideApplication
from drives.forms import DriveCreationForm
from users.models import CustomUser

'''
Called when a waypoint is updated
'''
def submit_waypoint(request, driveId):
    if request.method == "POST":
        waypoint_x = request.POST['waypoint_x'] 
        waypoint_y = request.POST['waypoint_y'] 
        location_name  = request.POST['location'] 
        application_id = request.POST['application']
        
        print(request.POST)

        application = RideApplication.objects.get(id=application_id)
        application.waypoint = Location.objects.create(location=location_name, coordinates_x=waypoint_x, coordinates_y=waypoint_y)
        application.save()
        
        return HttpResponseRedirect(reverse('drives:post_details', args=(driveId,)))

'''
Called when a user clicks 'Join Ride'
Adds them to the list of requested passengers so the 
driver can decide to let them join or not
'''
def passenger_request(request, driveId):
    if request.method == "POST":
        # Make sure the user being added is the logged in user
        id = request.POST['userId']        
        logged_in_user = request.user.id
        if int(id) != int(logged_in_user):
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        # Make sure the user isn't already on the requestlist or the passenger list
        if Drive.objects.get(id=driveId).passengers.filter(id=id).count() != 0 or Drive.objects.get(id=driveId).requestList.filter(user__id=id).count() != 0:
            return HttpResponseRedirect(reverse('insuficient_permission'))

        Drive.objects.get(id=driveId).add_passenger_to_requestlist(CustomUser.objects.get(id=id))
        return HttpResponseRedirect(reverse('drives:post_details', args=(driveId,)))
        
'''
Called when a Passenger leaves a ride
'''
def leave_ride(request, driveId):
    if request.method == "POST":
        # Make sure the user leaving is the logged in user
        id = request.POST['passengerId']        
        logged_in_user = request.user.id
        if int(id) != int(logged_in_user):
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        # Make sure the user is actually on the passenger list
        if Drive.objects.get(id=driveId).passengers.filter(id=id).count() != 1:
            return HttpResponseRedirect(reverse('insuficient_permission'))
    
        Drive.objects.get(id=driveId).passengers.remove(CustomUser.objects.get(id=id))
        return HttpResponseRedirect(reverse('drives:post_details', args=(driveId,)))
        
'''
Called when a Driver removes a passenger
'''
def passenger_remove(request, driveId):
    if request.method == "POST":
        # Make sure the logged in user is the drive owner
        id = request.POST['passengerId']
        owner_id = Drive.objects.get(id=driveId).driver.id        
        logged_in_user = request.user.id
        if int(owner_id) != int(logged_in_user):
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        # Make sure the user is actually on the passenger list
        if Drive.objects.get(id=driveId).passengers.filter(id=id).count() != 1:
            return HttpResponseRedirect(reverse('insuficient_permission'))
    
        Drive.objects.get(id=driveId).passengers.remove(CustomUser.objects.get(id=id))
        return HttpResponseRedirect(reverse('drives:post_details', args=(driveId,)))
        
'''
Called when a Driver approves a passenger request
'''
def approve_request(request, driveId):
    if request.method == "POST":
        # Make sure the logged in user is the drive owner
        id = request.POST['passengerId']
        owner_id = Drive.objects.get(id=driveId).driver.id        
        logged_in_user = request.user.id
        if int(owner_id) != int(logged_in_user):
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        # Make sure the user is on the requestList and not on the passengerList
        if Drive.objects.get(id=driveId).passengers.filter(id=id).count() != 0 and Drive.objects.get(id=driveId).requestList.filter(id=id).count() != 1:
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        Drive.objects.get(id=driveId).passengers.add(CustomUser.objects.get(id=id))
        requestList = Drive.objects.get(id=driveId).requestList
        request = requestList.get(user__id=id)
        
        # Add waypoint to drive and remove request from list
        requestList.remove(request)
        if request.waypoint:
            Drive.objects.get(id=driveId).waypointList.add(request.waypoint)
        request.delete()
        
        return HttpResponseRedirect(reverse('drives:post_details', args=(driveId,)))
        
'''
Called when a Driver rejects a passenger request
'''
def reject_request(request, driveId):
    if request.method == "POST":
        # Make sure the logged in user is the drive owner
        id = request.POST['passengerId']
        owner_id = Drive.objects.get(id=driveId).driver.id        
        logged_in_user = request.user.id
        if int(owner_id) != int(logged_in_user):
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        # Make sure the user is on the requestList
        if not Drive.objects.get(id=driveId).requestList.get(user=CustomUser.objects.get(id=id)):
            return HttpResponseRedirect(reverse('insuficient_permission'))
            
        id = request.POST['passengerId']
        requestList = Drive.objects.get(id=driveId).requestList
        request = requestList.get(user__id=id)
        
        if request.waypoint:
            request.waypoint.delete()
        requestList.remove(request)
        request.delete()
        return HttpResponseRedirect(reverse('drives:post_details', args=(driveId,)))

class DriveView(generic.DetailView):
    model = Drive
    template_name = "drives/posting.html"
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        
        # Mark if there are open spaces in the car
        # so we can render a button to apply to the ride
        if kwargs['object'].max_passengers - kwargs['object'].passengers.count() > 0:
            context['empty_passenger_slots'] = True
        
        context['waitlistIds'] = []
        for application in kwargs['object'].requestList.all():
            context['waitlistIds'].append(application.user.id)
        context['passengerIds'] = []
        for passenger in kwargs['object'].passengers.all():
            context['passengerIds'].append(passenger.id)
            
        context['requestList'] = kwargs['object'].requestList.all()
        
        return context

'''
View function for the home page of the drive module
Shows a summary of all Drives in a convenient list format
'''
class RideList(ListView):
    model = Drive


def post_new(request):
    if request.method == "POST":
        # re-format time data to use 24 hour scale for Django
        if request.POST['time']:
            request.POST = request.POST.copy()
            if 'am' in request.POST['time']:
                request.POST['time'] = request.POST['time'].replace('am', '')
            elif 'pm' in request.POST['time']:
                request.POST['time'] = request.POST['time'].replace('pm', '')
                hours,minutes = request.POST['time'].split(":")
                request.POST['time'] = str(int(hours) + 12) + ":" + minutes

        form = DriveCreationForm(request.POST)

        if form.is_valid():

            start_location = Location.objects.create(
                coordinates_x=request.POST["start_coordinates_x"],
                coordinates_y=request.POST["start_coordinates_y"], 
				location=request.POST["start_location"])

            end_location = Location.objects.create(
                coordinates_x=request.POST["end_coordinates_x"],
                coordinates_y=request.POST["end_coordinates_y"],
				location=request.POST["end_location"])

            start_location.save()
            end_location.save()

            post = form.save(commit=False)
            post.start_location = start_location
            post.end_location = end_location
            post.save()
            return HttpResponseRedirect(reverse('drives:post_details', args=(post.pk,)))
        else:
            print(form.errors)
    else:
        form = DriveCreationForm()

    return render(request, 'drives/new_drive.html', {'form': form})
