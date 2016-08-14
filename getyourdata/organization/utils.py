from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_objects_paginator(page, contents, per_page):
    """
    Returns pagination content that is shown on page inside pagination
    """
    p = Paginator(
        contents,
        per_page)

    try:
        return p.page(page)
    except PageNotAnInteger:
        return p.page(1)
    except EmptyPage:  # Reached an empty page: redirect to last page
        return p.page(p.num_pages)
