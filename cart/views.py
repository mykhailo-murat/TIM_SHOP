from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction
from main.models import Product, ProductSize
from .models import Cart, CartItem
from .forms import AddToCartForm, UpdateCartItemForm
import json

