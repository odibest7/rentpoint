def is_item_owner_request(request):
    # Keep role authorization consistent across owner-only views.
    return request.user.is_authenticated and request.user.is_item_owner
