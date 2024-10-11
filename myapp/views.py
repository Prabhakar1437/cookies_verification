from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import UserData
from .forms import UserDataForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UserDataView(View):
    def get(self, request):
        form = UserDataForm()
        return render(request, 'dataform.html', {'form': form})

    def post(self, request):
        form = UserDataForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'User data saved successfully'})
        else:
            errors = {field: str(error[0]) for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)

class UserDataListView(View):
    def get(self, request):
        users = UserData.objects.all()
        return render(request, 'user_list.html', {'users': users})

@method_decorator(csrf_exempt, name='dispatch')
class UserDataEditView(View):
    def get(self, request, pk):
        user = get_object_or_404(UserData, pk=pk)
        form = UserDataForm(instance=user)
        return render(request, 'user_edit.html', {'form': form})

    def post(self, request, pk):
        user = get_object_or_404(UserData, pk=pk)
        form = UserDataForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'User data updated successfully'})
        else:
            errors = {field: str(error[0]) for field, error in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)