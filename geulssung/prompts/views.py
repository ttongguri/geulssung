from django.shortcuts import render
from django.http import JsonResponse
from .models import GeneratedPrompt
import random

def random_prompts(request):
    style = request.GET.get('style')
    genre = style  # style과 genre가 동일하게 쓰이는 구조
    prompts = list(GeneratedPrompt.objects.filter(style=genre).values_list('content', flat=True))
    selected = random.sample(prompts, min(4, len(prompts)))
    return JsonResponse({'prompts': selected})
