from rest_framework import pagination
from rest_framework.response import Response
class customPagination(pagination.PageNumberPagination):
    page_size=3
    page_size_query_param='page_size'
    max_page_size=6
    page_query_param='page'

    def get_paginated_response(self, data):
        return Response({
            'links':{
                'NEXT':self.get_next_link(),
                'PREVIOUS':self.get_previous_link()

            },
            'COUNT':self.page.paginator.count,
            'RESULTS':data
        })
    