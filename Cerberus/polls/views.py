from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
#from django.template import RequestContext, loader
from models import Choice, Poll


# generic views
#   ListView(): view object for displaying a list of objects.
#   DetailView(): view object for displaying a detail page for a particular type of object.
#   Each generic view needs to know what model it will be acting upon, using the 'model'
#       attribute.
#   The 'template_name" attribute is used to tell Django to use a specific template name
#       instead of the auto-generated default template name.
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        """
        Return the last five published polls (not including those set to be
        published in the future.
        """
        # pub_date__lte filters to objects less than or equal to timezone.now().
        return Poll.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Poll.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

# manual views
def index(request):
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]

    # long-hand example of loading template, setting context, and returning
    #template = loader.get_template('polls/index.html')
    #context = RequestContext(request, {
    #    'latest_poll_list': latest_poll_list,
    #})
    #return HttpResponse(template.render(context))

    # short hand example of loading template, setting context, and returning using render()
    #   render(): takes the request object as its first argument, a template name as the
    #       second argument, and a dictionary as its optional third argument. It returns
    #       an HttpResponse object of the given template rendered with the given context.
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'polls/index.html', context)


def detail(request, poll_id):
    # long-hand example to check if poll exists and raise HTTP 404 error if not
    #try:
    #    poll = Poll.objects.get(pk=poll_id)
    #except Poll.DoesNotExist:
    #    raise Http404

    # shorthand example to check if poll exists and raise HTTP 404 error if not
    #   get_object_or_404(): takes a Django model as its first argument and an arbitrary
    #       number of keywords arguments, which it passes to the get() function of the
    #       model's manager. It raises Http404 if the object doesn't exist.
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/results.html', {'poll': poll})


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # redisplay the poll voting form
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing with POST data.
        #   This prevents data from being posted twice if a user hits the Back button.
        #   HttpResponseRedirect() takes one argument: the URL to which the user will be
        #   redirected.
        # The reverse() function used helps avoid having to hardcode a URL in the view
        #   function. This reverse() call will return a string like '/polls/3/results/'
        #   where '3' is the value of p.id. The redirected URL will then call the 'results'
        #   view to display the final page.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))