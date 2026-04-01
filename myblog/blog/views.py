from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Like, Profile, Category
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm, PostForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})


@never_cache
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = Comment.objects.filter(post=post)

    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=post, user=request.user).exists()

    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            Comment.objects.create(post=post, author=request.user, content=content)
            return redirect('post_detail', slug=post.slug)

    return render(request, 'post_details.html', {
        'post': post,
        'comments': comments,
        'liked': liked
    })


@login_required
@never_cache
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'created_post.html', {'form': form})


@login_required
@never_cache
def edit_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user == post.author:
        post.delete()
        messages.success(request, "Post deleted!")

    return redirect('home')


@login_required
def like_post(request, id):
    post = get_object_or_404(Post, id=id)
    like = Like.objects.filter(post=post, user=request.user)

    if like.exists():
        like.delete()
    else:
        Like.objects.create(post=post, user=request.user)

    return redirect('post_detail', slug=post.slug)


@never_cache
def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect('profile')

    return render(request, 'register.html', {'form': form})


@never_cache
def user_login(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect(next_url or 'profile')

        messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'next': next_url})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    posts = Post.objects.filter(author=request.user)
    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile,
        'posts': posts
    })

@login_required
@never_cache
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    u_form = UserUpdateForm(request.POST or None, instance=request.user)
    p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    if u_form.is_valid() and p_form.is_valid():
        u_form.save()
        p_form.save()
        messages.success(request, "Profile updated!")
        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })


def user_logout(request):
    logout(request)
    return redirect('home')


def csrf_failure(request, reason=""):
    messages.error(request, "Your form session expired. Please reload the page and try again.")
    return redirect('home')


def all_posts(request):
    category_id = request.GET.get('category')
    
    if category_id:
        posts = Post.objects.filter(category_id=category_id).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')
    
    categories = Category.objects.all()
    
    return render(request, 'all_posts.html', {
        'posts': posts,
        'categories': categories,
        'selected_category_id': category_id
    })


def categories_view(request):
    categories = Category.objects.all()
    
    # Count posts per category
    category_data = []
    for cat in categories:
        post_count = Post.objects.filter(category=cat).count()
        category_data.append({
            'category': cat,
            'post_count': post_count
        })
    
    return render(request, 'categories.html', {
        'category_data': category_data
    })


def about(request):
    post_count = Post.objects.count()
    user_count = Post.objects.values('author').distinct().count()
    comment_count = Comment.objects.count()
    
    return render(request, 'about.html', {
        'post_count': post_count,
        'user_count': user_count,
        'comment_count': comment_count
    })