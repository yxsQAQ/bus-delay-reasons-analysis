from django.shortcuts import render
from django.core.serializers import serialize
from django.http import JsonResponse
import json
from app01.models import BodsBusAnalysis, BodsBusAnalysisAll


def operator(request):
    operators = BodsBusAnalysis.objects.filter(Name__in=['BRTB', 'KBUS', 'TBTN', 'VECT'])
    operators_name = [operator.Name for operator in operators]
    median_values = [operator.Median for operator in operators]
    mean_values = [operator.Mean for operator in operators]

    context = {
        'operators_name': operators_name,
        'median_values': median_values,
        'mean_values': mean_values,
    }

    return render(request, 'operators.html', context)

def line(request):
    operators = BodsBusAnalysis.objects.filter(Name__in=['cal', 'cot', 'i4', 'igo','key', 'mln', 'sky','9',
                                                         '3A', '3B', '3C', 'one','ra', 'two', '90', '90C', '92'])
    operators_name = [operator.Name for operator in operators]
    median_values = [operator.Median for operator in operators]
    mean_values = [operator.Mean for operator in operators]

    context = {
        'operators_name': operators_name,
        'median_values': median_values,
        'mean_values': mean_values,
    }

    return render(request, 'line.html', context)

def direction(request):
    operators = BodsBusAnalysis.objects.filter(Name__in=['inbound', 'outbound'])
    operators_name = [operator.Name for operator in operators]
    median_values = [operator.Median for operator in operators]
    mean_values = [operator.Mean for operator in operators]

    context = {
        'operators_name': operators_name,
        'median_values': median_values,
        'mean_values': mean_values,
    }

    return render(request, 'direction.html', context)

def time(request):
    operators = BodsBusAnalysis.objects.filter(Name__in=['hour7', 'hour8','hour9', 'hour10',
                                                         'hour11', 'hour12', 'hour13', 'hour14',
                                                         'hour15', 'hour16', 'hour17', 'hour18',
                                                         'hour19', 'hour20', 'hour21', 'hour22',
                                                         'hour23'])
    operators_name = [operator.Name for operator in operators]
    median_values = [operator.Median for operator in operators]
    mean_values = [operator.Mean for operator in operators]

    context = {
        'operators_name': operators_name,
        'median_values': median_values,
        'mean_values': mean_values,
    }

    return render(request, 'time.html', context)


def map(request):
    operators = BodsBusAnalysis.objects.filter(Name__in=['cal', 'cot', 'i4', 'igo','key', 'mln', 'sky','9',
                                                         '3A', '3B', '3C', 'one','ra', 'two', '90', '90C', '92'])
    operators_name = [operator.Name for operator in operators]
    median_values = [operator.Median for operator in operators]
    mean_values = [operator.Mean for operator in operators]

    context = {
        'operators_name': operators_name,
        'median_values': median_values,
        'mean_values': mean_values,
    }

    return render(request, 'map.html', context)

def heatmap(request):
    data = BodsBusAnalysisAll.objects.filter(LineRef__in=['cal', 'cot', 'i4', 'igo', 'key', 'mln', 'sky', '9',
                                             '3A', '3B', '3C', 'one', 'ra', 'two', '90', '90C', '92'])

    line_name = [data.LineRef for _ in data]
    hour = [data.hour for _ in data]
    data_values = [data.Degree for _ in data]

    context = {
        'line_name': line_name,
        'hour': hour,
        'data_values': data_values,
    }

    return render(request, 'heatmap.html', context)
