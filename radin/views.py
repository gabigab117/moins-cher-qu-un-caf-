from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .models import Confession
from .forms import ConfessionForm


@ratelimit(key='ip', rate='2/m', method='POST', block=False)
def index(request):
    confession_list = Confession.objects.all().order_by('-created_at')
    
    paginator = Paginator(confession_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = ConfessionForm()  # Initialisation par défaut

    if request.method == 'POST':
        if getattr(request, 'limited', False):
            if request.headers.get('HX-Request'):
                response = HttpResponse(
                    '<div class="alert alert-warning mb-3">⏱️ Wow, doucement ! Attendez un peu entre chaque confession.</div>'
                )
                response['HX-Retarget'] = '#form-errors'
                response['HX-Reswap'] = 'innerHTML'
                return response
            
            form = ConfessionForm(request.POST)
            form.add_error(None, "Vous envoyez trop de messages. Attendez une minute.")
        
        else:
            form = ConfessionForm(request.POST)
            if form.is_valid():
                confession = form.save()
                
                if request.headers.get('HX-Request'):
                    return render(request, 'radin/partials/confession_item.html', {
                        'conf': confession
                    })
                return redirect('index')

    return render(request, 'radin/index.html', {'page_obj': page_obj, 'form': form})


@require_POST
def vote(request, pk, vote_type):
    """ Gestion des votes sans recharger la page (HTMX) """
    confession = get_object_or_404(Confession, pk=pk)
    
    voted_cookie = request.COOKIES.get(f'voted_{pk}')
    
    if voted_cookie:
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

    response = render(request, 'radin/partials/vote_buttons.html', {
        'conf': confession,
        'voted': True
    })
    
    response.set_cookie(f'voted_{pk}', 'true', max_age=31536000)
    return response
