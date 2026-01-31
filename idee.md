🐀 Projet : Radin Anonyme (MVP)
Domaine : moins-cher-qu-un-cafe.fr Stack : Django + SQLite (Mode WAL) + HTML/CSS "Ticket de caisse". + Bootstrap et HTMX

1. La Base de Données (models.py)
On stocke l'anecdote et les votes. C'est tout.

Python
# app/models.py
from django.db import models

class Confession(models.Model):
    body = models.CharField(max_length=280, verbose_name="Ta radinerie")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Compteurs de votes
    votes_genie = models.PositiveIntegerField(default=0)
    votes_rat = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.body[:50]
2. Le Formulaire (forms.py)
Crée ce fichier dans ton dossier d'application si tu ne l'as pas.

Python
# app/forms.py
from django import forms
from .models import Confession

class ConfessionForm(forms.ModelForm):
    class Meta:
        model = Confession
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-input', 
                'placeholder': 'J\'ai réutilisé un filtre à café en le séchant...',
                'rows': 3,
                'maxlength': 280
            }),
        }
3. La Logique & Protection RAM (views.py)
Ici, on gère l'affichage avec pagination (vital pour la RAM) et le système de vote en HTMX.

Python
# app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Confession
from .forms import ConfessionForm

def index(request):
    # On récupère les confessions
    confession_list = Confession.objects.all()
    
    # PAGINATION : Vital pour 1Go de RAM. On affiche 20 items max par page.
    paginator = Paginator(confession_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Gestion du formulaire d'ajout
    if request.method == 'POST':
        form = ConfessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ConfessionForm()

    return render(request, 'index.html', {'page_obj': page_obj, 'form': form})

@require_POST
def vote(request, pk, vote_type):
    """ Gestion des votes sans recharger la page (AJAX) """
    confession = get_object_or_404(Confession, pk=pk)
    
    # Protection basique : on utilise les cookies pour éviter le spam
    voted_cookie = request.COOKIES.get(f'voted_{pk}')
    
    if voted_cookie:
        return JsonResponse({'status': 'error', 'message': 'Déjà voté !'}, status=403)

    if vote_type == 'genie':
        confession.votes_genie += 1
    elif vote_type == 'rat':
        confession.votes_rat += 1
    
    confession.save()

    response = JsonResponse({
        'status': 'ok', 
        'genie': confession.votes_genie, 
        'rat': confession.votes_rat
    })
    
    # On pose un cookie qui expire dans 1 an
    response.set_cookie(f'voted_{pk}', 'true', max_age=31536000)
    return response
4. Les Routes (urls.py)
Python
# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vote/<int:pk>/<str:vote_type>/', views.vote, name='vote'),
]
5. Le Design "Ticket de Caisse" (templates/index.html)
Tout est dans un seul fichier pour simplifier. Le CSS imite un ticket de caisse froissé.

HTML
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moins cher qu'un café - Radin Anonyme</title>
    <style>
        /* DESIGN TICKET DE CAISSE */
        body {
            background-color: #e0e0e0;
            font-family: 'Courier New', Courier, monospace; /* Police Ticket */
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            max_width: 600px;
            margin: 0 auto;
        }
        .ticket {
            background: #fff;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-top: 1px dashed #ccc; /* Effet déchirure */
            border-bottom: 1px dashed #ccc;
            position: relative;
        }
        /* Effet dentelé haut et bas du ticket (Optionnel mais joli) */
        .ticket::before, .ticket::after {
            content: "";
            position: absolute;
            left: 0;
            width: 100%;
            height: 5px;
            background-size: 10px 10px;
        }
        
        h1 { text-align: center; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 10px; }
        .slogan { text-align: center; font-size: 0.9em; margin-bottom: 30px; }
        
        /* FORMULAIRE */
        .form-box { background: #ffffcc; padding: 15px; margin-bottom: 30px; border: 1px solid #e0e0aa; }
        .form-input { width: 95%; padding: 10px; border: none; background: transparent; font-family: inherit; resize: none; outline: none; }
        .btn-submit { width: 100%; background: #000; color: #fff; padding: 10px; border: none; font-family: inherit; cursor: pointer; font-weight: bold; text-transform: uppercase;}
        
        /* CARTE CONFESSION */
        .confession-body { font-size: 1.1em; margin-bottom: 15px; line-height: 1.4; }
        .meta { font-size: 0.8em; color: #777; margin-bottom: 10px; display: block; }
        .actions { display: flex; justify-content: space-between; gap: 10px; margin-top: 15px; border-top: 1px dotted #ccc; padding-top: 10px; }
        
        button.vote-btn {
            flex: 1; padding: 8px; border: 1px solid #333; background: #fff; cursor: pointer; font-family: inherit; font-weight: bold;
        }
        button.vote-btn:hover { background: #eee; }
        .genie { color: #28a745; }
        .rat { color: #dc3545; }
        
        .pagination { text-align: center; margin-top: 20px; }
    </style>
</head>
<body>

<div class="container">
    <div class="ticket">
        <h1>MOINS CHER QU'UN CAFE</h1>
        <div class="slogan">**** TICKET DE RATS ****<br>17/04/2024 - 10:42</div>

        <div class="form-box">
            <form method="post">
                {% csrf_token %}
                {{ form.body }}
                <button type="submit" class="btn-submit">IMPRIMER MA RADINERIE</button>
            </form>
        </div>

        {% for conf in page_obj %}
        <div class="ticket item" id="conf-{{ conf.id }}">
            <span class="meta">{{ conf.created_at|date:"d/m/Y H:i" }}</span>
            <div class="confession-body">
                {{ conf.body }}
            </div>
            
            <div class="actions">
                <button class="vote-btn" onclick="vote({{ conf.id }}, 'genie')">
                    🧠 GÉNIE (<span id="count-genie-{{ conf.id }}">{{ conf.votes_genie }}</span>)
                </button>
                <button class="vote-btn" onclick="vote({{ conf.id }}, 'rat')">
                    🐀 RAT (<span id="count-rat-{{ conf.id }}">{{ conf.votes_rat }}</span>)
                </button>
            </div>
        </div>
        {% endfor %}

        <div class="pagination">
            {% if page_obj.has_previous %}
                <a href="?page={{ page_obj.previous_page_number }}">&lt; PRÉCÉDENT</a>
            {% endif %}
            <span> PAGE {{ page_obj.number }} / {{ page_obj.paginator.num_pages }} </span>
            {% if page_obj.has_next %}
                <a href="?page={{ page_obj.next_page_number }}">SUIVANT &gt;</a>
            {% endif %}
        </div>
        
        <br><center>MERCI DE VOTRE VISITE<br>GARDEZ VOTRE MONNAIE</center>
    </div>
</div>


</body>
</html>
Ne pas utiliser du css custom mais Bootstrap pour aller plus vite, ici c'est juste une idée. Ou juste un peu de css inline basique. Utiliser HTMX