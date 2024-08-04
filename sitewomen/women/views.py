from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView

from .forms import AddPostForm, UploadFileForm, ContactForm
from .models import Women, Category, TagPost, UploadFiles
from .utils import DataMixin





def custom_permission_denied(request, exception):
    return render(request, '403.html', {
        'current_year': datetime.now().year,
    }, status=403)




class WomenHome(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    title_page = 'Главная страница'
    cat_selected = 0

    def get_queryset(self):
        w_lst = cache.get('women_posts')
        if not w_lst:
            w_lst = Women.published.all().select_related('cat')
            cache.set('women_posts', w_lst, 60)
        return w_lst




@login_required
def about(request):
    contact_list = Women.published.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'women/about.html',
                  {'title': 'О сайте', 'page_obj': page_obj})





class ShowPost(DataMixin, DetailView):
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['post'].title)

    def get_object(self, queryset=None):
        return get_object_or_404(Women.published, slug=self.kwargs[self.slug_url_kwarg])






class AddPage(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'women/addpage.html'
    title_page = 'Добавление статьи'
    permission_required = 'women.add_women'

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)




class UpdatePage(PermissionRequiredMixin, DataMixin, UpdateView):
    model = Women
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование статьи'
    permission_required = 'women.change_women'













class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')
    title_page = 'Обратная связь'

    def get_form_kwargs(self):
        kwargs = super(ContactFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated:
            # Проверяем, что имя пользователя не было изменено
            if form.cleaned_data['name'] != user.username:
                form.add_error(None, "Недопустимое изменение имени пользователя.")
                return self.form_invalid(form)

            # Проверяем email
            if user.email:
                # Если у пользователя есть email, он не должен быть изменен
                if form.cleaned_data['email'] != user.email:
                    form.add_error(None, "Недопустимое изменение email пользователя.")
                    return self.form_invalid(form)
            else:
                # Если у пользователя нет email, новый email должен быть введен
                new_email = form.cleaned_data['email']
                if not new_email:
                    form.add_error('email', "Email обязателен.")
                    return self.form_invalid(form)
                # Сохраняем новый email пользователя
                user.email = new_email
                user.save()
                messages.success(self.request, "Ваш email успешно сохранен.")


        # Остальной код обработки формы...
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message = form.cleaned_data.get('message')
        media_files = form.cleaned_data.get('media_files')

        # Формируем тело письма
        full_message = f"Сообщение от {name} ({email}):\n\n{message}"

        # Создаем и отправляем письмо...
        email_message = EmailMessage(
            subject=f"Обратная связь от {name}",
            body=full_message,
            from_email='no-reply@yourdomain.com',
            to=['iqro.forum@gmail.com'],
            reply_to=[email]
        )

        if media_files:
            for file in media_files:
                email_message.attach(file.name, file.read(), file.content_type)

        email_message.send(fail_silently=False)

        return super().form_valid(form)








def login(request):
    return HttpResponse("Авторизация")


class WomenCategory(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Women.published.filter(cat__slug=self.kwargs['cat_slug']).select_related("cat")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context,
                                      title='Категория - ' + cat.name,
                                      cat_selected=cat.pk,
                                      )





def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")




class TagPostList(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag)

    def get_queryset(self):
        return Women.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')



