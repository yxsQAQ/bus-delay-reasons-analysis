"""
Custom pagination component. If you want to use this pagination component in the future, you need to do the following:

In the view function:
    def pretty_list(request):

        1. Filter data based on your own conditions.
        queryset = models.PrettyNum.objects.filter(**data_dict).order_by('-level')

        2. Instantiate the pagination object.
        page_object = Pagination(request, queryset)

        context = {
            'search_data': search_data,
            'queryset': page_object.page_queryset,  # Paginated data
            'page_string': page_object.html()       # Generate pagination links
        }

        return render(request, '.html', context)

In HTML:
    {% for obj in queryset %}
        {{ obj.xx }}
    {% endfor %}

    <ul class='pagination'>
        {{ page_string }}
    </ul>
"""


from django.utils.safestring import mark_safe
import copy


class Pagination(object):

    def __init__(self, request, queryset, page_size=10, plus=5, page_param='page'):
        """
        :param request: Request object
        :param queryset: Data that meets the conditions (used for pagination)
        :param page_size: Number of data entries to display per page
        :param plus: Number of pages to display before and after the current page
        :param page_param: Parameter to obtain the current page from the URL, e.g., http://127.0.0.1:8000/pretty/list/?page=4
        """

        get_query_dict = copy.deepcopy(request.GET)
        get_query_dict._mutable = True
        self.get_query_dict = get_query_dict
        self.page_param = page_param

        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size

        self.start = (page - 1) * page_size
        self.end = page * page_size

        self.page_queryset = queryset[self.start:self.end]

        # Total number of data entries
        total_count = queryset.count()

        # Total number of pages
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1

        self.total_page_count = total_page_count
        self.plus = plus


    def html(self):
        # Calculate the pages to display before and after the current page
        if self.total_page_count <= 2 * self.plus + 1:
            # There are fewer data entries in the database, less than 11 pages
            start_page = 1
            end_page = self.total_page_count
        else:
            # If the current page is less than 5
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        # Pagination links
        page_str_list = []

        self.get_query_dict.setlist(self.page_param, [1])

        # First page
        page_str_list.append('<li><a href="?{}">First</a></li>'.format(self.get_query_dict.urlencode()))

        # Previous page
        if self.page > 1:
            self.get_query_dict.setlist(self.page_param, [self.page - 1])
            prev = '<li><a href="?{}">Previous</a></li>'.format(self.get_query_dict.urlencode())
        else:
            self.get_query_dict.setlist(self.page_param, [1])
            prev = '<li><a href="?{}">Previous</a></li>'.format(self.get_query_dict.urlencode())
        page_str_list.append(prev)

        for i in range(start_page, end_page + 1):
            self.get_query_dict.setlist(self.page_param, [i])
            if i == self.page:
                ele = '<li class="active"><a href="?{}">{}</a></li>'.format(self.get_query_dict.urlencode(), i)
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(self.get_query_dict.urlencode(), i)
            page_str_list.append(ele)

        # Next page
        if self.page < self.total_page_count:
            self.get_query_dict.setlist(self.page_param, [self.page + 1])
            next_page = '<li><a href="?{}">Next</a></li>'.format(self.get_query_dict.urlencode())
        else:
            self.get_query_dict.setlist(self.page_param, [self.total_page_count])
            next_page = '<li><a href="?{}">Next</a></li>'.format(self.get_query_dict.urlencode())
        page_str_list.append(next_page)

        # Last page
        self.get_query_dict.setlist(self.page_param, [self.total_page_count])
        page_str_list.append('<li><a href="?{}">Last</a></li>'.format(self.get_query_dict.urlencode()))

        search_string = '''
        <form method="get" style='float:right'>
            <div class="input-group" style="width: 200px">
                <input type="text" name='page' class="form-control" placeholder="Page">
                <span class="input-group-btn">
                    <button class="btn btn-primary" type="submit">Jump</button>
                </span>
            </div>
        </form>
        '''

        page_str_list.append(search_string)

        page_string = mark_safe(''.join(page_str_list))

        return page_string
