from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
from xkcdpass import xkcd_password as xp  # windows의 choleor env activate >


def __get_authenticated_code__():
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=3, max_length=8)
    return xp.generate_xkcdpassword(mywords, acrostic=chr(random.randrange(97, 122)) + chr(random.randrange(97, 122)))


@api_view(['POST'])
def authenticate(request):
    __get_authenticated_code__()
    request.data.get("start_audio_slice_id"), request.data.get("end_audio_slice_id")
    ""
    # 프로세싱
    return Response(0)
