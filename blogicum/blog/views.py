from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from .forms import CommentForm, PostForm, ProfileForm
from .mixins import OnlyAuthorMixin
from .models import Category, Comment, Post

NUM_IN_PAGE = 10
User = get_user_model()


class IndexListView(ListView):
    template_name = 'blog/index.html'
    paginate_by = NUM_IN_PAGE
    model = Post

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().all_filter()


class PostDetailView(SingleObjectMixin, ListView):
    template_name = 'blog/detail.html'
    paginate_by = NUM_IN_PAGE
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Post.objects.all())
        if self.object.author != self.request.user:
            self.object = self.get_object(
                queryset=Post.objects.category_filter(),
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['comments'] = context['page_obj']
        if self.request.user.is_authenticated:
            context['form'] = CommentForm(self.request.POST or None)
        return context

    def get_queryset(self) -> QuerySet:
        return self.object.comments_for_post.select_related('author')


class CategoryListView(SingleObjectMixin, ListView):
    template_name = 'blog/category.html'
    paginate_by = NUM_IN_PAGE
    slug_url_kwarg = 'category_slug'
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=Category.objects.filter(is_published=True),
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        return context

    def get_queryset(self) -> QuerySet:
        return (
            self.object.posts_for_category
            .publish_filter()
            .annotate_comment_count()
        )


class ProfileListView(SingleObjectMixin, ListView):
    paginate_by = NUM_IN_PAGE
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'name_slug'
    slug_field = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context

    def get_queryset(self) -> QuerySet:
        queryset = (
            self.object.posts_for_author
            .annotate_comment_count()
            .select_related('category')
        )
        if self.request.user != self.object:
            queryset = queryset.category_filter()
        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'name_slug': self.request.user.username},
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            instance=get_object_or_404(
                Post,
                pk=self.kwargs.get(self.pk_url_kwarg),
            ),
        )
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'name_slug': self.request.user.username},
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/detail.html'
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        form.instance.author = self.request.user
        post = get_object_or_404(
            Post.objects.annotate_comment_count(),
            pk=post_id,
        )
        if post.author != form.instance.author:
            post = get_object_or_404(
                Post.objects.all_filter(),
                pk=post_id,
            )
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')},
        )


class CommentUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')},
        )


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')},
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'name_slug': self.request.user.username},
        )
