from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import Error
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, parser_classes, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from networkapi.buyersguide.models import Product, BooleanVote, RangeVote
from networkapi.buyersguide.throttle import UserVoteRateThrottle, TestUserVoteRateThrottle

vote_throttle_class = UserVoteRateThrottle if not settings.TESTING else TestUserVoteRateThrottle


# Login required so we can continue to develop this and merge into master without the public seeing it.
# Remove this when we're ready to launch.
@login_required
def buyersguide_home(request):
    products = Product.objects.all()
    return render(request, 'buyersguide_home.html', {'products': products})


@login_required
def product_view(request, productname):
    product = Product.objects.get(name__iexact=productname)
    return render(request, 'product_page.html', {'product': product, 'mediaUrl': settings.MEDIA_URL})


@api_view(['POST'])
@permission_classes((AllowAny,))
@parser_classes((JSONParser,))
@throttle_classes((vote_throttle_class,))
@csrf_protect
def product_vote(request):
    # Grab the request payload data
    product_id = request.data['productID']
    value = request.data['value']

    # validate the data types passed in the request payload
    if not (isinstance(product_id, int) and isinstance(value, (int, bool))):
        return Response('Invalid payload - check data types', status=400, content_type='text/plain')

    try:
        product = Product.objects.get(id=product_id)
        vote_class = RangeVote

        # Check if this vote is a boolean (yes/no) vote, and switch the model if it is
        if isinstance(value, bool):
            vote_class = BooleanVote

        # Build the model instance
        vote = vote_class(
            value=value,
            product=product
        )

        # validate the values are in range (if this is a RangeVote)
        vote.full_clean()

        # persist the vote
        vote.save()

        return Response('Vote recorded', status=201, content_type='text/plain')
    except ObjectDoesNotExist:
        return Response('Invalid product', status=400, content_type='text/plain')
    except ValidationError:
        return Response('Vote value is not valid', status=400, content_type='text/plain')
    except Error:
        return Response('Internal Server Error', status=500, content_type='text/plain')
