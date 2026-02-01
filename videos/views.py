from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from courses.models import Course, Enrollment
from .models import Video, VideoProgress, TranscodingJob
from .forms import VideoUploadForm
import os
from accounts.decorators import instructor_required


@instructor_required
def upload_video(request, course_id):
    """Upload video to course (instructor only)"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.course = course
            video.save()
            
            # Create transcoding job
            TranscodingJob.objects.create(
                video=video,
                source_file=str(video.video_file)
            )
            
            return redirect('course_detail', course_id=course.id)
    else:
        form = VideoUploadForm()
    
    context = {'form': form, 'course': course}
    return render(request, 'videos/upload_video.html', context)


@login_required
def watch_video(request, video_id):
    """Watch video (check enrollment)"""
    video = get_object_or_404(Video, id=video_id)
    course = video.course
    
    # Check if student is enrolled
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course,
        is_active=True
    ).exists()
    
    if not is_enrolled and course.instructor != request.user:
        return redirect('login')
    
    # Get or create progress
    progress, created = VideoProgress.objects.get_or_create(
        video=video,
        student=request.user
    )
    
    context = {
        'video': video,
        'course': course,
        'progress': progress,
    }
    return render(request, 'videos/watch_video.html', context)


@login_required
def stream_video(request, video_id):
    """Stream video file with range request support"""
    video = get_object_or_404(Video, id=video_id)
    course = video.course
    
    # Check access
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course,
        is_active=True
    ).exists()
    
    if not is_enrolled and course.instructor != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # If video is stored in S3
    if video.s3_video_key:
        import boto3
        from django.conf import settings
        s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': video.s3_video_key},
            ExpiresIn=3600
        )
        return redirect(presigned_url)
    
    # Local file streaming
    file_path = video.video_file.path
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'Video not found'}, status=404)
    
    file_size = os.path.getsize(file_path)
    range_header = request.META.get('HTTP_RANGE', '')
    
    if range_header:
        # Parse range header
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        def file_generator():
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        response = StreamingHttpResponse(file_generator(), content_type='video/mp4')
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Content-Length'] = end - start + 1
        response.status_code = 206
        return response
    
    def file_generator():
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
    
    response = StreamingHttpResponse(file_generator(), content_type='video/mp4')
    response['Content-Length'] = file_size
    return response


@login_required
def save_progress(request, video_id):
    """Save video progress (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    video = get_object_or_404(Video, id=video_id)
    
    try:
        watched_duration = int(request.POST.get('watched_duration', 0))
        progress, created = VideoProgress.objects.get_or_create(
            video=video,
            student=request.user
        )
        progress.watched_duration = watched_duration
        progress.update_completion()
        
        return JsonResponse({
            'status': 'success',
            'completion_percent': float(progress.completion_percent),
            'is_completed': progress.is_completed
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
