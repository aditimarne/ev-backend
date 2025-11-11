import os
from datetime import datetime, timedelta

import certifi
import gridfs
import jwt
from bson import ObjectId
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from pymongo import MongoClient
from rest_framework import permissions, status
from rest_framework.decorators import (api_view, parser_classes,permission_classes)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from users.models import User

from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          ProfileSerializer, RegisterSerializer)

# ---------------- Load MongoDB Connection ----------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "AuthDB")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where()) if MONGO_URI else None
db = client[MONGO_DB] if client else None
fs = gridfs.GridFS(db) if db is not None else None


# ---------- Update Profile (with GridFS upload) ----------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])



def get_profile(request):
    user = request.user
    data = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "mobile": getattr(user, "mobile", ""),
        "profile_image": getattr(user, "profile_image", ""),
        "avatar_file_id": getattr(user, "avatar_file_id", ""),
    }
    return Response(data)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])

def update_profile(request):
    try:
        user = request.user
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


        # ✅ Update basic fields
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.email = request.data.get("email", user.email)
        user.mobile = request.data.get("mobile", user.mobile)

        # ✅ Handle image upload safely
        if "profile_image" in request.FILES and fs is not None:
            file = request.FILES["profile_image"]
            print("Uploading file:", file.name)

            # delete old avatar if exists
            if user.avatar_file_id:
                try:
                    fs.delete(ObjectId(user.avatar_file_id))
                except Exception as e:
                    print("Delete old avatar error:", e)
                    print("Saved new GridFS file:", file_id)

            # Save new file in GridFS
            file_id = fs.put(file.read(), filename=file.name, content_type=file.content_type)
            user.avatar_file_id = str(file_id)
            user.profile_image = f"/api/avatar/{file_id}/"  # public access path

        user.save(force_insert=False, validate=False)
        # ✅ Save all changes (text + image)
        return Response(user.to_dict(), status=status.HTTP_200_OK)

    except Exception as e:
        print("❌ update_profile error:", str(e))  # 👈 log full error
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# ---------- Register ----------
@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(user.to_dict(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Login ----------
@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate JWT token
            payload = {
                "user_id": str(user.id),
                "exp": datetime.utcnow() + timedelta(days=7),
                "iat": datetime.utcnow(),
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            return Response(
                {
                    "token": token,
                    "user": user.to_dict(),
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # ---------- Profile (GET + PUT) ----------
# class ProfileView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def put(self, request):
#         user = request.user
#         data = request.data

#         user.first_name = data.get("first_name", user.first_name)
#         user.last_name = data.get("last_name", user.last_name)
#         user.email = data.get("email", user.email)
#         user.mobile = data.get("mobile", user.mobile)
#         user.save()

#         return Response({"message": "Profile updated!"}, status=status.HTTP_200_OK)



# ---------- Change Password ----------
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            from django.contrib.auth.hashers import (check_password,
                                                     make_password)
            user = request.user
            old = serializer.validated_data["old_password"]
            new = serializer.validated_data["new_password"]

            if not check_password(old, user.password):
                return Response({"old_password": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(new)
            user.save()
            return Response({"detail": "Password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- Delete Avatar ----------
class DeleteAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        if user.avatar_file_id and fs is not None:
            try:
                fs.delete(ObjectId(user.avatar_file_id))
            except Exception:
                pass
            user.avatar_file_id = ""
            user.profile_image = ""
            user.save()
        return Response({"message": "Avatar deleted"}, status=status.HTTP_200_OK)


# ---------- Serve Avatar ----------
class ServeAvatarView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, file_id):
        try:
            if fs is None:
                return Response({"detail": "GridFS not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            oid = ObjectId(file_id)
            grid_out = fs.get(oid)
            content = grid_out.read()
            content_type = grid_out.content_type or "application/octet-stream"
            return HttpResponse(content, content_type=content_type)
        except Exception:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
