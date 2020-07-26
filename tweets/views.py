import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse,Http404,JsonResponse
from django.utils.http import is_safe_url
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Tweet
from .forms import TweetForm
from .serializers import (
        TweetSerializer,
        TweetCreateSerializer,
        TweetActionSerializer,
        )
ALLOWED_HOSTS = settings.ALLOWED_HOSTS

def home_view(request, *args,**kwargs):
    # return HttpResponse("<h1>Hey There </h1>")
    return render(request,
                    template_name='pages/home.html',
                    context={},
                    status=200)

@api_view(['POST']) # reuquest that client sent is post is interpreted by this.
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetCreateSerializer(data = request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response({}, status = 400)

@api_view(['GET']) #get request qpi view decorator
def tweet_detail_view(request,tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)

@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request,tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    qs = qs.filter(user=request.user)
    if not qs.exists():
        return Response({'message':'You cannot delete this tweet'}, status=401)
    obj = qs.first()
    obj.delete()
    return Response({'message':'Tweet delete successfully'},status=200)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def tweet_action_view(request,*args, **kwargs):
#     '''
#     Action option include like, unlike, retweet
#     id is a required field
#     '''
#     serializer = TweetActionSerializer(data = request.data)
#     if serializer.is_valid(raise_exception=True):
#         data = serializer.validated_data
#         tweet_id = data.get("id")
#         action = data.get("action")
#         qs = Tweet.objects.filter(id=tweet_id)
#         if not qs.exists():
#             return Response({}, status=404)
#         obj = qs.fisrt()
#         if action == "like":
#             obj.likes.add(request.user)
#             serializer = TweetSerializer(obj)
#             return Response(serializer.data, status=200)

#         elif action == "unlike":
#             obj.likes.remove(request.user)
#         else:
#             pass
   
#     return Response({'message':action},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    '''
    id is required.
    Action options are: like, unlike, retweet
    '''
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get("id")
        action = data.get("action")
        content = data.get("content")
        qs = Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({}, status=404)
        obj = qs.first()
        if action == "like":
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == "unlike":
            obj.likes.remove(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == "retweet":
            print(content)
            new_tweet = Tweet.objects.create(
                user = request.user,
                parent = obj,
                content = content,
            )
            serializer = TweetSerializer(new_tweet)
            return Response(serializer.data, status=201)
    return Response({}, status=200)


@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs, many=True)
    return Response(serializer.data, status=200)


def tweet_create_view_pure_django(request,*args, **kwargs):
    """
    REST API CREATE VIEW
    """
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    next_url = request.POST.get('next')
    # print('ajax',request.is_ajax())
    if form.is_valid():
        obj = form.save(commit=False)
        # other form logic here
        # after authentication also remember to associate(Foreign Key)
        obj.user = user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201) # 201 == created forms
        if next_url != None and is_safe_url(next_url,ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm() # reinitialised blank form
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
    return render(request,'components/form.html', context={'form':form})

def tweet_list_view_pure_django(request, *args,**kwargs):
    """
    REST API VIEW
    return json data
    """
    qs = Tweet.objects.all()
    tweet_list = [x.serialize() for x in qs]

    data = {
        'isuser':False,
        'response' : tweet_list,
    }

    return JsonResponse(data)

def tweet_detail_view_pure_django(request, tweet_id, *args,**kwargs):
    """
    REST API VIEW
    return json data
    """
    data = {
       'id':tweet_id,
    }
    status = 200
    try:
      obj = Tweet.objects.get(id=tweet_id)
      data['content'] = obj.content
    except:
        data['message'] = 'Not found'
        status = 404
    return JsonResponse(data,status=status)
