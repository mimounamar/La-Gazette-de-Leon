import json

from django.contrib.auth import login
from rest_framework import permissions, status
from rest_framework import views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from gazette_backend import serializers
from gazette_backend.models import LostPasswordToken, Edition, Article
from gazette_backend.serializers import UserSerializer, LostPasswordTokenSerializer, EditionSerializer, \
    ArticleSerializer

import random
import string

import smtplib

from email.mime.text import MIMEText


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = serializers.LoginSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_user(request):
    if str(request.user) == "AnonymousUser":
        return Response({"detail": "Invalid token."}, status=status.HTTP_202_ACCEPTED)
    user = User.objects.get(username=request.user)
    serializer = UserSerializer(user, many=False)
    return Response({"detail": str(request.user), "groups": serializer.data['groups'],"user" : serializer.data}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def handle_user(request):
    if request.method == 'POST':
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for i in range(16))
        u_first_name = request.data['first_name'].replace(' ','').lower()
        u_last_name = request.data['last_name'].replace(' ', '').lower()
        username = u_first_name+'.'+u_last_name
        user = User.objects.create(
            username=username,
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            email=request.data['email'],
        )
        base_group = Group.objects.get(name="redactor")
        user.groups.add(base_group)
        user.set_password(password)
        user.save()
        return Response(data={"password": password}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response(None, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def lost_password(request, cred):
    if request.method == 'GET':
        try:
            user = User.objects.get(username=cred)
            serializer = UserSerializer(user, many=False)

            characters = string.ascii_letters + string.digits
            token = ''.join(random.choice(characters) for i in range(16))

            msg = MIMEText(f'''Bonjour, {serializer.data['first_name']}.
            
Vous avez demandé à réinitialiser votre mot de passe sur l'espace rédacteur.
            
Cliquez sur le lien ci-dessous pour effectuer le changement.
            
https://lagazettedeleon.social/admim/password/{token}
            
Cordialement,
L'équipe de La Gazette de Léon.''')
            msg['Subject'] = "Changement de mot de passe - La Gazette de Léon"
            msg['To'] = serializer.data['email']
            msg['From'] = "noreply@lagazettedeleon.social"

            server = smtplib.SMTP("smtp.eu.mailgun.org", 587)
            server.login("postmaster@lagazettedeleon.social", "#APIKEY_NOTHING_TO_SEE")
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()

            LostPasswordToken.objects.create(
                username=serializer.data['username'],
                token=token
            )
            return Response(None, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        try:
            token = LostPasswordToken.objects.get(token=cred)
            token_serializer = LostPasswordTokenSerializer(token, many=False)
            user = User.objects.get(username=token_serializer.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token.delete()
            return Response(None, status=status.HTTP_200_OK)
        except LostPasswordToken.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def editions_list(request):
    if request.method == 'GET':
        editions = Edition.objects.all().order_by('-id')
        serializer = EditionSerializer(editions, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def editions_add(request):
    if request.method == 'POST':
        serializer = EditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_201_CREATED)
        else:
            return Response(data=request.data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def editions_publish(request, pk):
    if request.method == 'GET':
        edition = Edition.objects.get(id=pk)
        try:
            edition.publish()
            edition.save()
            return Response(None, status=status.HTTP_202_ACCEPTED)
        except Edition.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def articles_list(request, pk):
    try:
        edition = Edition.objects.get(id=pk)
        edition_serializer = EditionSerializer(edition)
        articles = Article.objects.filter(edition=pk)
        articles_serializer = ArticleSerializer(articles, many=True)
        return Response(data={"title":edition_serializer.data["title"], "status":edition_serializer.data["status"], "articles":articles_serializer.data}, status=status.HTTP_200_OK)
    except Article.DoesNotExist:
        return Response(None, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def articles_perm(request, pk):
        article = Article.objects.filter(id=pk, redactor_1__username=str(request.user)) | Article.objects.filter(
            edition=pk, redactor_2__username=str(request.user))
        serializer = ArticleSerializer(article, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_list(request, pk):
    try:
        edition = Edition.objects.get(id=pk)
        edition_serializer = EditionSerializer(edition)
        articles = Article.objects.filter(edition=pk, redactor_1__username=str(request.user)) | Article.objects.filter(edition=pk, redactor_2__username=str(request.user))
        articles_serializer = ArticleSerializer(articles, many=True)
        return Response(data={"title": edition_serializer.data["title"], "status": edition_serializer.data["status"],
                              "articles": articles_serializer.data}, status=status.HTTP_200_OK)
    except Article.DoesNotExist:
        return Response(None, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser])
def articles_add(request):
    if request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(None, status=status.HTTP_201_CREATED)
        else:
            return Response(data=request.data, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        users = User.objects.all().order_by("last_name")
        users_serializer = UserSerializer(users, many=True)
        return Response(users_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def articles_edit(request, pk):
    if request.method == 'GET':
        try:
            article = Article.objects.get(id=pk)
            article_status = article.get_status()
            if str(article_status) == "Redaction":
                Article.objects.filter(id=pk).update(status="correction")
                return Response(None, status=status.HTTP_201_CREATED)
            elif str(article_status) == "Correction":
                Article.objects.filter(id=pk).update(status="done")
                return Response(None, status=status.HTTP_201_CREATED)
            else:
                return Response(None, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response(data=request.data, status=status.HTTP_404_NOT_FOUND)