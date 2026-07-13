from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from Codbixiye.models import codbixiye_DB
from Musharax.models import musharax_DB
from voiteID.models import ID_DB
from Depadrments.models import depadrments_DB

from django.contrib.auth.models import User as AdminUser
import os
import requests
import uuid

def upload_image_to_supabase(file_obj):
    if not file_obj:
        return None
    
    supabase_url = "https://hfxcvpogwocrputxmdoh.supabase.co"
    bucket_name = "mushraximage"
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_key:
        print("WARNING: SUPABASE_KEY is missing. Cannot upload image to Supabase.")
        return None
        
    # Generate unique filename to avoid overwrites
    ext = os.path.splitext(file_obj.name)[1]
    file_name = f"{uuid.uuid4()}{ext}"
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/{file_name}"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": file_obj.content_type,
    }
    
    try:
        response = requests.post(url, headers=headers, data=file_obj.read())
        if response.status_code == 200:
            return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"
        else:
            print(f"Supabase upload failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return None


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=identifier, password=password)

        if user is not None and user.is_active and (user.is_staff or user.is_superuser):
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('dashboard')

        messages.error(request, ' Hubi username/email iyo password-ka Sax Yihin.')

    return render(request, 'adminapp/login.html')


def logout_view(request):
    logout(request)
    return redirect('voiteid')

@login_required(login_url='login')
def dashboard_view(request):
    # --- Core Counts ---
    total_voters = codbixiye_DB.objects.count()
    total_candidates = musharax_DB.objects.count()
    total_ids = ID_DB.objects.count()
    total_departments = depadrments_DB.objects.count()
    total_admins = AdminUser.objects.count()

    used_ids = ID_DB.objects.filter(_is_used=True).count()
    unused_ids = total_ids - used_ids
    id_utilization = int(round(used_ids / total_ids * 100)) if total_ids > 0 else 0

    # --- Gender Demographics ---
    male_voters = codbixiye_DB.objects.filter(c_gender='lab').count()
    female_voters = codbixiye_DB.objects.filter(c_gender='dhadig').count()
    male_pct = int(round(male_voters / total_voters * 100)) if total_voters > 0 else 0
    female_pct = int(round(female_voters / total_voters * 100)) if total_voters > 0 else 0

    # --- Top Candidate ---
    top_candidate = None
    if total_candidates > 0:
        max_votes = -1
        for cand in musharax_DB.objects.all():
            v = codbixiye_DB.objects.filter(c_musharax=cand).count()
            if v > max_votes:
                max_votes = v
                top_candidate = {
                    'name': cand.m_name,
                    'dept': cand.m_depadrments.d_name if cand.m_depadrments else 'N/A',
                    'votes': v,
                    'image': cand.m_image if cand.m_image else None,
                    'pct': int(round(v / total_voters * 100)) if total_voters > 0 else 0,
                }

    # --- Candidates Leaderboard (top 5) ---
    leaderboard = []
    for cand in musharax_DB.objects.all():
        v = codbixiye_DB.objects.filter(c_musharax=cand).count()
        leaderboard.append({
            'name': cand.m_name,
            'dept': cand.m_depadrments.d_name if cand.m_depadrments else 'N/A',
            'votes': v,
            'pct': int(round(v / total_voters * 100)) if total_voters > 0 else 0,
            'image': cand.m_image if cand.m_image else None,
        })
    leaderboard = sorted(leaderboard, key=lambda x: x['votes'], reverse=True)[:5]

    # --- Department Stats ---
    dept_stats = []
    for dept in depadrments_DB.objects.all():
        dept_v = codbixiye_DB.objects.filter(c_department=dept).count()
        dept_stats.append({
            'name': dept.d_name,
            'votes': dept_v,
            'pct': int(round(dept_v / total_voters * 100)) if total_voters > 0 else 0,
        })
    dept_stats = sorted(dept_stats, key=lambda x: x['votes'], reverse=True)

    # --- Recent Votes ---
    recent_votes = codbixiye_DB.objects.all().order_by('-id')[:6]

    context = {
        'total_voters': total_voters,
        'total_candidates': total_candidates,
        'total_ids': total_ids,
        'total_departments': total_departments,
        'total_admins': total_admins,
        'used_ids': used_ids,
        'unused_ids': unused_ids,
        'id_utilization': id_utilization,
        'male_voters': male_voters,
        'female_voters': female_voters,
        'male_pct': male_pct,
        'female_pct': female_pct,
        'top_candidate': top_candidate,
        'leaderboard': leaderboard,
        'dept_stats': dept_stats,
        'recent_votes': recent_votes,
    }
    return render(request, 'adminapp/dashboard.html', context)

@login_required(login_url='login')
def musharax_view(request):
    candidates = musharax_DB.objects.all().order_by('-m_joined')
    departments = depadrments_DB.objects.all()
    total_system_votes = codbixiye_DB.objects.count()
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('m_name')
            email = request.POST.get('m_email')
            gender = request.POST.get('m_gender')
            dept_id = request.POST.get('m_depadrments')
            image_url = request.POST.get('m_image')
            
            if name and email and gender and dept_id:
                if musharax_DB.objects.filter(m_email=email).exists():
                    messages.error(request, 'Email-kan horay ayaa loo isticmaalay. Fadlan mid kale geli.')
                else:
                    dept = get_object_or_404(depadrments_DB, id=dept_id)
                        
                    musharax_DB.objects.create(
                        m_name=name,
                        m_email=email,
                        m_gender=gender,
                        m_depadrments=dept,
                        m_image=image_url
                    )
                    messages.success(request, 'Musharax si guul ah ayaa lagu daray.')
            return redirect('musharax')

        elif action == 'edit':
            candidate_id = request.POST.get('candidate_id')
            candidate = get_object_or_404(musharax_DB, id=candidate_id)
            
            email = request.POST.get('m_email')
            if musharax_DB.objects.filter(m_email=email).exclude(id=candidate_id).exists():
                messages.error(request, 'Email-kan musharax kale ayaa isticmaalaya. Fadlan mid kale geli.')
            else:
                candidate.m_name = request.POST.get('m_name')
                candidate.m_email = email
                candidate.m_gender = request.POST.get('m_gender')
                dept_id = request.POST.get('m_depadrments')
                if dept_id:
                    candidate.m_depadrments = get_object_or_404(depadrments_DB, id=dept_id)
                
                new_image_url = request.POST.get('m_image')
                if new_image_url is not None:
                    candidate.m_image = new_image_url
                
                update_fields = ['m_name', 'm_email', 'm_gender', 'm_depadrments', 'm_if_allowed', 'm_image']
                candidate.save(update_fields=update_fields)
                messages.success(request, 'Musharaxa xogihiisa waa la cusboonaysiiyay.')
            return redirect('musharax')

        elif action == 'toggle_allow':
            candidate_id = request.POST.get('candidate_id')
            candidate = get_object_or_404(musharax_DB, id=candidate_id)
            candidate.m_if_allowed = not candidate.m_if_allowed
            candidate.save(update_fields=['m_if_allowed'])
            return redirect('musharax')

        elif action == 'delete':
            candidate_id = request.POST.get('candidate_id')
            candidate = get_object_or_404(musharax_DB, id=candidate_id)
            candidate.delete()
            return redirect('musharax')
            
    import json
    # Pre-calculate overall system stats
    total_system_male = codbixiye_DB.objects.filter(c_gender='lab').count()
    total_system_female = codbixiye_DB.objects.filter(c_gender='dhadig').count()
    
    system_dept_totals = {}
    for dept in departments:
        system_dept_totals[dept.id] = codbixiye_DB.objects.filter(c_department=dept).count()

    # Calculate analytics for each candidate
    for cand in candidates:
        cand_votes = codbixiye_DB.objects.filter(c_musharax=cand)
        total_cand_votes = cand_votes.count()
        cand.vote_count = total_cand_votes
        
        male = cand_votes.filter(c_gender='lab').count()
        female = cand_votes.filter(c_gender='dhadig').count()
        
        cand.male_votes = male
        cand.female_votes = female
        
        if total_system_votes > 0:
            cand.vote_percentage = int(round(total_cand_votes / total_system_votes * 100))
        else:
            cand.vote_percentage = 0
            
        # Candidate's internal percentages
        male_pct = int(round(male / total_cand_votes * 100)) if total_cand_votes > 0 else 0
        female_pct = int(round(female / total_cand_votes * 100)) if total_cand_votes > 0 else 0
        
        # System-wide percentages for this candidate
        sys_male_pct = int(round(male / total_system_male * 100)) if total_system_male > 0 else 0
        sys_female_pct = int(round(female / total_system_female * 100)) if total_system_female > 0 else 0
        
        # Calculate votes per department for this candidate
        dept_stats = []
        for dept in departments:
            dept_votes = cand_votes.filter(c_department=dept).count()
            sys_dept_total = system_dept_totals.get(dept.id, 0)
            
            if dept_votes > 0 or sys_dept_total > 0:
                # Percentage of candidate's total votes
                dept_pct = int(round(dept_votes / total_cand_votes * 100)) if total_cand_votes > 0 else 0
                # Percentage of system's total votes for this department
                sys_dept_pct = int(round(dept_votes / sys_dept_total * 100)) if sys_dept_total > 0 else 0
                
                if dept_votes > 0:
                    dept_stats.append({
                        'name': dept.d_name,
                        'votes': dept_votes,
                        'pct': dept_pct,
                        'sys_pct': sys_dept_pct,
                        'sys_total': sys_dept_total
                    })
        
        # Sort departments by candidate's votes descending
        dept_stats = sorted(dept_stats, key=lambda x: x['votes'], reverse=True)
        
        analytics_data = {
            'name': cand.m_name,
            'dept': cand.m_depadrments.d_name if cand.m_depadrments else 'Unknown',
            'total_votes': total_cand_votes,
            'vote_percentage': cand.vote_percentage,
            'male': male,
            'female': female,
            'male_pct': male_pct,
            'female_pct': female_pct,
            'sys_male_pct': sys_male_pct,
            'sys_female_pct': sys_female_pct,
            'total_sys_male': total_system_male,
            'total_sys_female': total_system_female,
            'dept_stats': dept_stats
        }
        cand.analytics_json = json.dumps(analytics_data)

    # Sort: votes DESC first, then m_joined ASC (earlier join date wins the tie)
    candidates_sorted = sorted(
        candidates,
        key=lambda c: (-c.vote_count, c.m_joined)
    )

    # Assign rank and mark the winner
    for i, cand in enumerate(candidates_sorted):
        cand.rank = i + 1
        cand.is_winner = (i == 0 and cand.vote_count > 0)

    context = {
        'candidates': candidates_sorted,
        'departments': departments,
        'total_system_votes': total_system_votes,
    }
    return render(request, 'adminapp/musharax.html', context)

@login_required(login_url='login')
def voiteid_view(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'generate':
            try:
                quantity = int(request.POST.get('quantity', 1))
                if quantity > 0 and quantity <= 1000: # Limit to 1000 at a time for safety
                    for _ in range(quantity):
                        ID_DB.objects.create()
                    messages.success(request, f'Wa la Sameyey {quantity} IDs.')
            except ValueError:
                messages.error(request, 'Invalid quantity.')
                
            return redirect('voiteid')
            
        elif action == 'delete':
            id_val = request.POST.get('id_val')
            if id_val:
                ID_DB.objects.filter(_c_id=id_val).delete()
                messages.success(request, 'ID  Wa la Tirtiray.')
            return redirect('voiteid')
            
        elif action == 'export':
            import openpyxl
            from django.http import HttpResponse
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "IDs an La,adegsan"
            ws.append(['Vote ID'])
            
            unused_ids = ID_DB.objects.filter(_is_used=False)
            for obj in unused_ids:
                ws.append([obj._c_id])
                
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="IDs.xlsx"'
            
            wb.save(response)
            return response
            
        elif action == 'import':
            import openpyxl
            
            file = request.FILES.get('excel_file')
            if not file:
                messages.error(request, "Fadlan soo dooro file-ka.")
                return redirect('voiteid')
                
            try:
                wb = openpyxl.load_workbook(file, data_only=True)
                ws = wb.active
                
                accepted = 0
                skipped_exists = 0
                
                for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
                    if not row or row[0] is None:
                        continue
                        
                    vote_id = str(row[0]).strip().upper()
                    
                    # Skip header
                    if row_idx == 0 and vote_id == 'VOTE ID':
                        continue
                        
                    # Validation: check if it already exists
                    if ID_DB.objects.filter(_c_id=vote_id).exists():
                        skipped_exists += 1
                        continue
                        
                    # Create the new ID
                    ID_DB.objects.create(_c_id=vote_id)
                    accepted += 1
                    
                msg = f"Natiijada So xaraynta: {accepted} ID waa la aqbalay. "
                if skipped_exists > 0:
                    msg += f" | {skipped_exists} ID waa laga booday (Horay ayay u jireen). "

                if accepted > 0:
                    messages.success(request, msg)
                elif skipped_exists > 0:
                    messages.warning(request, msg)
                else:
                    messages.info(request, "Wax ID ah lagama helin file-ka.")
                    
            except Exception as e:
                messages.error(request, f'Khalad ayaa dhacay  Excel-ka: Fadlan hubi inuu yahay file sax ah.')
            return redirect('voiteid')

    # Unused first (False=0 sorts before True=1, reversed to get unused on top)
    all_ids_qs = ID_DB.objects.all().order_by('_is_used', '-_created_at')
    total_ids = all_ids_qs.count()
    used_ids = all_ids_qs.filter(_is_used=True).count()
    unused_ids = all_ids_qs.filter(_is_used=False).count()
    
    all_ids = []
    for obj in all_ids_qs:
        all_ids.append({
            'c_id': obj._c_id,
            'is_used': obj._is_used,
            'created_at': obj._created_at,
        })
    
    context = {
        'all_ids': all_ids,
        'total_ids': total_ids,
        'used_ids': used_ids,
        'unused_ids': unused_ids,
    }
    return render(request, 'adminapp/voiteid.html', context)

@login_required(login_url='login')
def codbixiye_view(request):
    voters = codbixiye_DB.objects.all().order_by('-id')
    
    total_votes = voters.count()
    male_votes = voters.filter(c_gender='lab').count()
    female_votes = voters.filter(c_gender='dhadig').count()
    
    context = {
        'voters': voters,
        'total_votes': total_votes,
        'male_votes': male_votes,
        'female_votes': female_votes,
    }
    return render(request, 'adminapp/codbixiye.html', context)

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

@login_required(login_url='login')
def manageadmin_view(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            is_superuser = request.POST.get('is_superuser') == 'on'
            
            if username and password:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=is_superuser
                )
            return redirect('manageadmin')
            
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            user_obj = get_object_or_404(User, id=user_id)
            
            user_obj.username = request.POST.get('username')
            user_obj.email = request.POST.get('email')
            user_obj.first_name = request.POST.get('first_name', '')
            user_obj.last_name = request.POST.get('last_name', '')
            user_obj.is_superuser = request.POST.get('is_superuser') == 'on'
            
            new_password = request.POST.get('password')
            if new_password:
                user_obj.set_password(new_password)
                
            user_obj.save()
            return redirect('manageadmin')
            
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            user_obj = get_object_or_404(User, id=user_id)
            # Prevent deleting the last superuser or currently logged in user (optional but good practice)
            if not (user_obj.is_superuser and User.objects.filter(is_superuser=True).count() == 1):
                user_obj.delete()
            return redirect('manageadmin')

    admins = User.objects.all().order_by('-date_joined')
    total_admins = admins.count()
    superusers = admins.filter(is_superuser=True).count()
    staff = admins.filter(is_superuser=False).count()
    
    context = {
        'admins': admins,
        'total_admins': total_admins,
        'superusers': superusers,
        'staff': staff,
    }
    return render(request, 'adminapp/manageadmin.html', context)

@login_required(login_url='login')
def departments_view(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            d_name = request.POST.get('d_name')
            if d_name:
                depadrments_DB.objects.create(d_name=d_name)
                messages.success(request, 'Wax Cusub ayad ku dartay!')
            return redirect('departments')
            
        elif action == 'edit':
            dept_id = request.POST.get('dept_id')
            dept_obj = get_object_or_404(depadrments_DB, id=dept_id)
            
            d_name = request.POST.get('d_name')
            if d_name:
                dept_obj.d_name = d_name
                dept_obj.save()
                messages.success(request, 'Waxdan Wad Habaysay')
            return redirect('departments')
            
        elif action == 'delete':
            dept_id = request.POST.get('dept_id')
            dept_obj = get_object_or_404(depadrments_DB, id=dept_id)
            dept_obj.delete()
            messages.success(request, 'Waxda wa tirtirtay!')
            return redirect('departments')

    departments_qs = depadrments_DB.objects.all().order_by('-id')
    total_departments = departments_qs.count()
    
    departments_data = []
    for dept in departments_qs:
        total_voters = dept.voters.count()
        male_voters = dept.voters.filter(c_gender='lab').count()
        female_voters = dept.voters.filter(c_gender='dhadig').count()
        candidates = dept.musharax_db_set.count()
        
        departments_data.append({
            'id': dept.id,
            'd_name': dept.d_name,
            'total_voters': total_voters,
            'male_voters': male_voters,
            'female_voters': female_voters,
            'candidates_count': candidates,
        })
    
    context = {
        'departments': departments_data,
        'total_departments': total_departments,
    }
    return render(request, 'adminapp/departments.html', context)
