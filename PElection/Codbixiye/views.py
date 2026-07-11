from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json

from Musharax.models import musharax_DB
from Depadrments.models import depadrments_DB
from voiteID.models import ID_DB
from .models import codbixiye_DB


def codee_view(request):
    """Main voting page — shows all candidates."""
    candidates = musharax_DB.objects.filter(m_if_allowed=True)
    departments = depadrments_DB.objects.all()

    context = {
        'candidates': candidates,
        'departments': departments,
    }
    return render(request, 'Codbixiye/codee.html', context)


def verify_id_ajax(request):
    """AJAX endpoint: verify that a Vote ID exists and is unused."""
    if request.method == 'POST':
        data = json.loads(request.body)
        vote_id = data.get('vote_id', '').strip().upper()

        try:
            id_obj = ID_DB.objects.get(_c_id=vote_id)
            if id_obj._is_used:
                return JsonResponse({
                    'valid': False,
                    'error': 'used',
                    'message': 'ID-gan horay ayaa loo isticmaalay. Fadlan gali ID aan la isticmaalin.'
                })
            else:
                return JsonResponse({'valid': True})
        except ID_DB.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'error': 'notfound',
                'message': f'ID-gan "{vote_id}" Ma jiro.'
            })

    return JsonResponse({'valid': False, 'message': 'Invalid request.'})


def submit_vote(request):
    """Handle final vote submission."""
    if request.method == 'POST':
        vote_id_str = request.POST.get('vote_id', '').strip().upper()
        candidate_id = request.POST.get('candidate_id')
        dept_id = request.POST.get('department')
        gender = request.POST.get('gender')

        errors = {}

        # Validate ID
        try:
            id_obj = ID_DB.objects.get(_c_id=vote_id_str)
            if id_obj._is_used:
                errors['id'] = 'ID-gan horay ayaa loo isticmaalay.'
        except ID_DB.DoesNotExist:
            errors['id'] = 'ID-gan kuma jiro nidaamka.'

        if not candidate_id:
            errors['candidate'] = 'Musharax la dooran waayey.'
        if not dept_id:
            errors['dept'] = 'Waax la dooran waayey.'
        if not gender:
            errors['gender'] = 'Jins la dooran waayey.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        try:
            candidate = musharax_DB.objects.get(id=candidate_id)
            dept = depadrments_DB.objects.get(id=dept_id)

            vote = codbixiye_DB(
                c_id=id_obj,
                c_musharax=candidate,
                c_department=dept,
                c_gender=gender,
            )
            vote.save()  # model.save() marks ID as used automatically

            return JsonResponse({'success': True, 'candidate_name': candidate.m_name})

        except ValidationError as e:
            return JsonResponse({'success': False, 'errors': {'id': str(e.message_dict.get('c_id', ['Khalad dhacay.'])[0])}})
        except Exception as e:
            return JsonResponse({'success': False, 'errors': {'general': str(e)}})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})
