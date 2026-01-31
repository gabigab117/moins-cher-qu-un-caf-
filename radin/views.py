from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Confession
from .forms import ConfessionForm


def index(request):
    confession_list = Confession.objects.all()
    
    paginator = Paginator(confession_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ConfessionForm(request.POST)
        if form.is_valid():
            confession = form.save()
            # Si requête HTMX, on renvoie juste le nouvel item
            if request.headers.get('HX-Request'):
                return render(request, 'radin/partials/confession_item.html', {
                    'conf': confession
                })
            return redirect('index')
    else:
        form = ConfessionForm()

    return render(request, 'radin/index.html', {'page_obj': page_obj, 'form': form})


@require_POST
def vote(request, pk, vote_type):
    """ Gestion des votes sans recharger la page (HTMX) """
    confession = get_object_or_404(Confession, pk=pk)
    
    # Protection basique : on utilise les cookies pour éviter le spam
    voted_cookie = request.COOKIES.get(f'voted_{pk}')
    
    if voted_cookie:
        # Renvoie un message d'erreur en HTML
        response = HttpResponse(
            '<small class="text-danger">Vous avez déjà voté !</small>',
            status=200
        )
        return response

    if vote_type == 'genie':
        confession.votes_genie += 1
    elif vote_type == 'rat':
        confession.votes_rat += 1
    
    confession.save()

    # Renvoie le fragment HTML mis à jour
    response = render(request, 'radin/partials/vote_buttons.html', {
        'conf': confession,
        'voted': True
    })
    
    # On pose un cookie qui expire dans 1 an
    response.set_cookie(f'voted_{pk}', 'true', max_age=31536000)
    return response
