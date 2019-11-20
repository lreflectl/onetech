from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def post_list(request):
	post_list = Post.objects.filter(published_date__isnull=False).order_by('-published_date')
	paginator = Paginator(post_list, 5)

	page = request.GET.get('page')
	posts_on_page = paginator.get_page(page)
	return render(request, 'blog/post_list.html', {'posts': posts_on_page})


def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	comments = post.approved_comments().order_by('-created_date')
	un_comments = post.unapproved_comments().order_by('-created_date')
	paginator = Paginator(comments, 10)

	page = request.GET.get('comment_page')
	comments_on_page = paginator.get_page(page)
	return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments_on_page, 'un_comments': un_comments})


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def post_new(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm()
	return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
	return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
	post_list = Post.objects.filter(published_date__isnull=True).order_by('-created_date')
	paginator = Paginator(post_list, 5)

	page = request.GET.get('page')
	posts_on_page = paginator.get_page(page)
	return render(request, 'blog/post_draft_list.html', {'posts': posts_on_page})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
	post = get_object_or_404(Post, pk=pk)
	post.delete()
	return redirect('post_list')

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)