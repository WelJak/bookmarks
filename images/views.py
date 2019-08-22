from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action


# Create your views here.

@login_required
def image_create(request):
    if request.method == 'POST':
        #formularz wyslany
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            #formularz prawidlowy
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            #przypisanie biezacego uzytkownika do nowego elemetnu
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'dodał obraz', new_item)
            messages.success(request, 'Obraz został dodany')
            #przekierowanie do widoku szcegolwego nowego elementu
            return redirect(new_item.get_absolute_url())
    else:
        #utworzenie formularza na podstawie danych dostarczonych przez bookmarklet w zadaniu GET
        form = ImageCreateForm(data=request.GET)

    return render(request, 'images/image/create.html',
                  {'section': 'images',
                   'form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request,
                  'images/image/detail.html',
                  {'section': 'images',
                   'image': image})


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'polubił', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ok'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 4)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #jesli nr storny nie jest liczba calkowita rpzechodzi do peirwszje storny wynikow
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            #jesli wystapi zadanie ajax i page ma wartosc spoza zakresu wyswietli pusta strone
            return HttpResponse('')
        #jesli page > nr ostatniej storny ---> wyswietla ostatnia strone
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images', 'images': images})