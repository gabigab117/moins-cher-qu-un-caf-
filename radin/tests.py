from django.test import TestCase, Client
from django.urls import reverse
from .models import Confession


class ConfessionModelTest(TestCase):
    def test_create_confession(self):
        """
        Given: Aucune confession n'existe
        When: Je crée une nouvelle confession
        Then: La confession est créée avec 0 votes et une date de création
        """
        conf = Confession.objects.create(
            body="J'ai réutilisé un sachet de thé 3 fois"
        )
        self.assertEqual(conf.votes_genie, 0)
        self.assertEqual(conf.votes_rat, 0)
        self.assertTrue(conf.created_at)

    def test_confession_ordering(self):
        """
        Given: Deux confessions créées à des moments différents
        When: Je récupère toutes les confessions
        Then: La plus récente est en première position
        """
        conf1 = Confession.objects.create(body="Première confession")
        conf2 = Confession.objects.create(body="Deuxième confession")
        
        confessions = Confession.objects.all()
        self.assertEqual(confessions[0], conf2)  # La plus récente en premier


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Créer des confessions de test
        for i in range(25):
            Confession.objects.create(body=f"Confession {i}")

    def test_index_page_loads(self):
        """
        Given: L'application est lancée
        When: J'accède à la page d'accueil
        Then: La page charge avec le statut 200 et le bon template
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'radin/index.html')

    def test_pagination(self):
        """
        Given: 25 confessions existent dans la base de données
        When: J'accède à la page 1 et à la page 2
        Then: La page 1 contient 20 confessions et la page 2 en contient 5
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['page_obj']), 20)
        
        # Vérifier qu'il y a une page 2
        response_page2 = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(response_page2.status_code, 200)
        self.assertEqual(len(response_page2.context['page_obj']), 5)

    def test_create_confession_post(self):
        """
        Given: Un nombre initial de confessions
        When: Je soumets le formulaire avec une nouvelle confession
        Then: Une nouvelle confession est créée et je suis redirigé
        """
        initial_count = Confession.objects.count()
        response = self.client.post(reverse('index'), {
            'body': 'Je réutilise les sacs en plastique'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertEqual(Confession.objects.count(), initial_count + 1)


class VoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.confession = Confession.objects.create(
            body="Test confession"
        )

    def test_vote_genie(self):
        """
        Given: Une confession sans vote
        When: Je vote GÉNIE pour cette confession
        Then: Le compteur votes_genie est incrémenté de 1
        """
        url = reverse('vote', kwargs={'pk': self.confession.pk, 'vote_type': 'genie'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.confession.refresh_from_db()
        self.assertEqual(self.confession.votes_genie, 1)
        self.assertEqual(self.confession.votes_rat, 0)

    def test_vote_rat(self):
        """
        Given: Une confession sans vote
        When: Je vote RAT pour cette confession
        Then: Le compteur votes_rat est incrémenté de 1
        """
        url = reverse('vote', kwargs={'pk': self.confession.pk, 'vote_type': 'rat'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.confession.refresh_from_db()
        self.assertEqual(self.confession.votes_rat, 1)
        self.assertEqual(self.confession.votes_genie, 0)

    def test_vote_cookie_protection(self):
        """
        Given: J'ai déjà voté pour une confession
        When: J'essaie de voter une deuxième fois
        Then: Mon vote n'est pas comptabilisé et un message m'indique que j'ai déjà voté
        """
        url = reverse('vote', kwargs={'pk': self.confession.pk, 'vote_type': 'genie'})
        self.client.cookies.load({})  # Clear cookies to simulate a new client
        # Premier vote
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième vote avec le cookie
        response2 = self.client.post(url)
        self.assertContains(response2, 'déjà voté', status_code=200)
        
        # Vérifier qu'on n'a compté qu'un seul vote
        self.confession.refresh_from_db()
        self.assertEqual(self.confession.votes_genie, 1)

    def test_vote_invalid_type(self):
        """
        Given: Une confession sans vote
        When: Je tente de voter avec un type invalide
        Then: Aucun vote n'est comptabilisé
        """
        url = reverse('vote', kwargs={'pk': self.confession.pk, 'vote_type': 'invalid'})
        response = self.client.post(url)
        
        self.confession.refresh_from_db()
        self.assertEqual(self.confession.votes_genie, 0)
        self.assertEqual(self.confession.votes_rat, 0)