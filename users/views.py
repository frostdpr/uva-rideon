from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.views import generic

from .models import CustomUser
from drives.models import Drive, DriverReview, RiderReview

from .forms import CustomUserCreationForm, RideReviewForm

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/register.html'

class ProfileView(generic.DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['avg_rating'] = DriverReview.objects.filter(of=kwargs['object'].id).rating
        context['driver_avg_rating'] = 3
        context['rider_avg_rating'] = 4
        return context

class EditProfileView(generic.DetailView):
    model = CustomUser
    template_name = 'users/editprofile.html'

class MyRidesView(generic.DetailView):
    model = CustomUser
    template_name = 'users/myrides.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_rides'] = Drive.objects.filter(status="Listed")
        context['completed_rides'] = Drive.objects.filter(status="Completed")
        context['cancelled_rides'] = Drive.objects.filter(status="Cancelled")
        return context

def post_new_review(request, pk):
    if request.method == "POST":
        request.POST = request.POST.copy()
        request.POST["by"] = request.user.id
        request.POST["of"] = 1
        form = RideReviewForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return HttpResponseRedirect(reverse_lazy('myrides', args=(pk,)))
    else:
        form = RideReviewForm()
        
    return render(request, 'users/myrides.html')
