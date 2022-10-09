from django.core.paginator import Paginator

COUNT_POSTS: int = 10


def paginator(queryset, request):
    paginator = Paginator(queryset, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
