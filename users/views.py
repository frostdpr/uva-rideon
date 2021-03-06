from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.views import generic
from django import template
from drives.models import Drive, DriverReview, RiderReview
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm, DriverReviewForm, RiderReviewForm

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/register.html'

class ProfileView(generic.DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['driver_avg_rating'] = get_driver_rating(kwargs['object'])
        context['rider_avg_rating'] = get_rider_rating(kwargs['object'])

        context['driver_reviews'] = DriverReview.objects.filter(of=kwargs['object'])
        context['rider_reviews'] = RiderReview.objects.filter(of=kwargs['object'])
        
        context['friends'] = kwargs['object'].friends.all()

        context['is_friend'] = False
        if CustomUser.objects.filter(id=self.request.user.id)[0].friends.filter(id=kwargs['object'].id).exists():
            context['is_friend'] = True

        return context

class EditProfileView(generic.UpdateView):
  
    model = CustomUser
    fields = [ 'username', 'gender', 'phone', 'about', 'profile_pic']
    template_name = 'users/editprofile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


    def get_friends(self, request):
        users = CustomUser.objects.exclude(id=request.user)
        friend = UserFriends.objects.get(current_user=request.user)
        friends = friend.users.all()
 
def get_fields(request,pk):
    if int(request.user.id) != int(pk):
        return redirect('/users/' + str(pk))
    try:
        if request.POST['valid'] == False:
            return redirect('/users/'+ pk)
    except:
        pass
    instance = CustomUser.objects.get(id=pk)
    form = CustomUserChangeForm(request.POST or None, request.FILES, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('/users/'+ pk) # should update these to use reverse
    else:
        request.POST = request.POST.copy()
        request.POST['valid'] = False
        #form = CustomUserChangeForm(instance=instance)
        return redirect('/users/'+ pk + '/edit')

    return render(request, 'users/editprofile.html', {'form': form, 'pk' : pk})  

class MyRidesView(generic.DetailView):
    model = CustomUser
    template_name = 'users/myrides.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['upcoming_rides'] = []
        upcoming_rides = Drive.objects.filter(status="Listed")

        for item in upcoming_rides:
            if item.driver == self.request.user or self.request.user in item.passengers.all():
                context['upcoming_rides'].append(item)

        context['cancelled_rides'] = []
        cancelled_rides = Drive.objects.filter(status="Cancelled")

        for item in cancelled_rides:
            if item.driver == self.request.user or self.request.user in item.passengers.all():
                context['cancelled_rides'].append(item)

        context['completed_rides'] = []
        completed_rides = Drive.objects.filter(status="Completed")

        for item in completed_rides:
            if item.driver == self.request.user or self.request.user in item.passengers.all():
                context['completed_rides'].append(item)
        
        context['riders_to_review_per_drive'] = []
        
        for drive in context['completed_rides']:
            query = Drive.objects.filter(id=drive.id)[0].passengers.all()
            ridersNeedReviews = []
            ridersWithReviewsIds = []
            ridersWithReviews = RiderReview.objects.filter(drive=drive.id, by=self.request.user.id).all()
            
            for item in ridersWithReviews:
                ridersWithReviewsIds.append(item.of)
            
            for person in query:
                if person not in ridersWithReviewsIds:
                    ridersNeedReviews.append(CustomUser.objects.get(id=person.id))

            context['riders_to_review_per_drive'].append( {"id":drive.id, "query":ridersNeedReviews})

        context['drivers_to_review_per_drive'] = []

        counter = 0
        for drive in context['completed_rides']:
            query = Drive.objects.filter(id=drive.id)[0].driver
            context['drivers_to_review_per_drive'].append( {"id":drive.id, "query":[]})

            if DriverReview.objects.filter(drive=drive.id, by=self.request.user.id).count() == 0:
                context['drivers_to_review_per_drive'][counter]['query'].append(query)
            counter += 1
        
        return context

def get_rider_rating(user):
    score = 0
    count = 0
    riderReviews = RiderReview.objects.filter(of=user.id).all()
    for item in riderReviews:
        score += item.rating
        count += 1
    if count == 0:
        return "N/A"
    return "%0.2f" % ((float(score)/count),)

def get_driver_rating(user):
    score = 0
    count = 0
    driverReviews = DriverReview.objects.filter(of=user.id).all()
    for item in driverReviews:
        score += item.rating
        count += 1
    if count == 0:
        return "N/A"
    return "%0.2f" % ((float(score)/count),)

def update_ratings():
    for user in CustomUser.objects.all():
        if get_driver_rating(user) != "N/A":
            CustomUser.objects.filter(id=user.id).update(driver_rating=float(get_driver_rating(user)))
        else:
            CustomUser.objects.filter(id=user.id).update(driver_rating=None)
        if get_rider_rating(user) != "N/A":
            CustomUser.objects.filter(id=user.id).update(rider_rating=float(get_rider_rating(user)))
        else:
            CustomUser.objects.filter(id=user.id).update(rider_rating=None)

def post_new_review(request, pk):
    if request.method == "POST":
        request.POST = request.POST.copy()

        request.POST["by"] = request.user.id
        
        if(request.user.id == Drive.objects.filter(id=request.POST["drive"])[0].driver.id):
            # Driver is reviewing passanger
            
            form = RiderReviewForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                
                update_ratings()
        
                return redirect('/users/' + str(pk) + '/myrides')
            else:
                print(form.errors)
                print("error adding review")
                return redirect('/users/' + str(pk) + '/myrides?error=review')
        else:
            # Rider reviewing driver

            form = DriverReviewForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                
                update_ratings()
                    
                return redirect('/users/' + str(pk) + '/myrides')
            else:
                print(form.errors)
                print("error adding review")
                return redirect('/users/' + str(pk) + '/myrides?error=review')
    else:
        form = RideReviewForm()
        
    update_ratings()
    
    return render(request, 'users/myrides.html')

def post_add_friend(request, pk):
    if request.method == "POST":
        if CustomUser.objects.filter(id=request.POST['tofriend_id']).count() != 0:
            CustomUser.objects.filter(id=request.user.id)[0].friends.add(CustomUser.objects.filter(id=request.POST['tofriend_id'])[0])
            return redirect('/users/' + str(pk))

def post_remove_friend(request, pk):
    if request.method == "POST":
        if CustomUser.objects.filter(id=request.POST['tofriend_id']).count() != 0:
            CustomUser.objects.filter(id=request.user.id)[0].friends.remove(CustomUser.objects.filter(id=request.POST['tofriend_id'])[0])
            return redirect('/users/' + str(pk))
