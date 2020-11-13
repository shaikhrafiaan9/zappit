from django.shortcuts import render
from rest_framework import generics , permissions , mixins , status
from rest_framework.exceptions import ValidationError
from .models import Post , Vote
from .serializers import PostSerializer , VoteSerializer
from rest_framework.response import Response

# Create your views here.

class PostList(generics.ListCreateAPIView):                                     #ListAPIView will only list with a GET Request whereas ListCreateAPIView will create Post with POST request
    queryset = Post.objects.all()                                               #what we are expecting to fetch
    serializer_class = PostSerializer                                           #Which Serializer we will be using
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]                #who has permission hto call this API

    def perform_create(self,serializer):                                        #to save data into the database
        serializer.save(poster=self.request.user)


class PostRetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self,request,*args,**kwargs):
        post = Post.objects.filter(pk=kwargs['pk'],poster=self.request.user)

        if post.exists():
            return self.destroy(request,*args,**kwargs)
        else:
            raise ValidationError(f"This Post Doesn't belong to {self.request.user}")                    


class VoteCreate(generics.CreateAPIView,mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user =self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user,post=post)

    def perform_create(self,serializer):
        if self.get_queryset().exists():
            raise ValidationError('You have Already voted for this post :)')      #to chect whether a user dont vote for same post twice
        serializer.save(voter=self.request.user,post=Post.objects.get(pk=self.kwargs['pk']))

    def delete(self,request,*args,**kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You have never voted for this Post")
