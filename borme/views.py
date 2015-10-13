from mongogeneric.list import ListView
from mongogeneric.detail import DetailView
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Company, Person, Anuncio, Config, Borme

from random import randint


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['total_companies'] = Company.objects.count()
        context['total_persons'] = Person.objects.count()
        context['total_anuncios'] = Anuncio.objects.count()
        context['random_companies'] = Company.objects.filter().limit(10).skip(randint(0, context['total_companies']))
        context['random_persons'] = Person.objects.filter().limit(10).skip(randint(0, context['total_persons']))
        context['last_modified'] = Config.objects.first().last_modified
        return context


class BusquedaView(TemplateView):
    template_name = "busqueda.html"

    def get_context_data(self, **kwargs):
        context = super(BusquedaView, self).get_context_data(**kwargs)
        if 'q' in self.request.GET:
            page = self.request.GET.get('page', 1)
            q_companies = Company.objects.filter(name__icontains=self.request.GET['q'])
            companies = Paginator(q_companies, 25)
            q_persons = Person.objects.filter(name__icontains=self.request.GET['q'])
            persons = Paginator(q_persons, 25)

            context['num_persons'] = persons.count
            context['num_companies'] = companies.count
            context['page'] = page
            context['query'] = self.request.GET['q']

            try:
                pg_companies = companies.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                pg_companies = companies.page(1)
                context['page'] = 1
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                pg_companies = companies.page(companies.num_pages)
            finally:
                context['companies'] = pg_companies
                pagerange = companies.page_range[:3] + companies.page_range[-3:]
                pagerange.append(pg_companies.number)
                pagerange = list(set(pagerange))
                pagerange.sort()
                if len(pagerange) == 1:
                    pagerange = []
                context['companies'].myrange = pagerange

            try:
                pg_persons = persons.page(page)
            except PageNotAnInteger:
                pg_persons = persons.page(1)
                context['page'] = 1
            except EmptyPage:
                pg_persons = persons.page(persons.num_pages)
            finally:
                context['persons'] = pg_persons
                pagerange = persons.page_range[:3] + persons.page_range[-3:]
                pagerange.append(pg_persons.number)
                pagerange = list(set(pagerange))
                pagerange.sort()
                if len(pagerange) == 1:
                    pagerange = []
                context['persons'].myrange = pagerange

        else:
            context['num_companies'] = 0
            context['num_persons'] = 0
            context['companies'] = []
            context['persons'] = []
            context['page'] = 1

        return context


class AnuncioView(DetailView):
    model = Anuncio
    context_object_name = 'anuncio'

    def get_object(self):
        self.anuncio = Anuncio.objects.get_or_404(id_anuncio=self.kwargs['id'])
        return self.anuncio

    """
    def get_context_data(self, **kwargs):
        context = super(AnuncioView, self).get_context_data(**kwargs)
        return context
    """


class BormeView(DetailView):
    model = Borme
    context_object_name = 'borme'

    def get_object(self):
        self.borme = Borme.objects.get_or_404(cve=self.kwargs['cve'])
        return self.borme

    def get_context_data(self, **kwargs):
        context = super(BormeView, self).get_context_data(**kwargs)

        context['total_anuncios'] = self.borme.until_reg - self.borme.from_reg + 1
        context['bormes_dia'] = Borme.objects.filter(date=self.borme.date).order_by('cve')
        bormes_dia = list(context['bormes_dia'])
        bormes_dia.remove(self.borme)
        context['bormes_dia'] = bormes_dia
        return context


class CompanyView(DetailView):
    model = Company
    context_object_name = 'company'

    def get_object(self):
        self.company = Company.objects.get_or_404(slug=self.kwargs['slug'])
        return self.company

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)

        context['anuncios'] = Anuncio.objects.filter(company=self.company).order_by('-id_anuncio')
        bormes = [r.borme for r in context['anuncios']]
        context['bormes'] = {b.cve: b for b in bormes}
        context['persons'] = Person.objects.filter(in_companies__contains=self.company)

        return context


class PersonView(DetailView):
    model = Person
    context_object_name = 'person'

    def get_object(self):
        self.person = Person.objects.get_or_404(slug=self.kwargs['slug'])
        #self.person = get_document_or_404(Person, slug=self.kwargs['slug'])
        return self.person

    """
    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)

        context['bormes'] = [b.cve for b in self.person.in_bormes]
        return context
    """

class PersonListView(ListView):
    model = Person
    context_object_name = 'people'
    queryset = Person.objects.all()[:100]


class CompanyListView(ListView):
    model = Company
    context_object_name = 'companies'
    queryset = Company.objects.all()[:100]


class CompanyProvinceListView(ListView):
    #model = Company
    context_object_name = 'companies'
    #queryset = Book.objects.filter(province==X).order_by('-name')
