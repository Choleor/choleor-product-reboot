from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
from xkcdpass import xkcd_password as xp  # windows의 choleor env activate >
import re
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.http import FileResponse, StreamingHttpResponse


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


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


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


def stream_video(request):
    os.chdir('/mnt/c/Users/Jihee/choleor-media/product/')
    token = request.GET.get('token')
    path = token + ".mkv"
    # http://127.0.0.1:8000/product/token?=HkujLO17Ez8.mkv 로 요청하면 받음
    # client에게 부여된 token 값으로 교차편집 진행, streaming으로 보내줌
    # path = 'HkujLO17Ez8.mkv'
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length),
                                     status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp
