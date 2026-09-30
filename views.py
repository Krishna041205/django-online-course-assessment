from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Choice, Course, Learner, Question, Submission


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    questions = Question.objects.filter(lesson__course=course).prefetch_related("choices")

    if request.method != "POST":
        return render(
            request,
            "onlinecourse/exam.html",
            {"course": course, "questions": questions},
        )

    # Remove an earlier attempt for this course before recording the new attempt.
    Submission.objects.filter(
        learner=learner,
        question__lesson__course=course,
    ).delete()

    for question in questions:
        selected_id = request.POST.get(f"question_{question.id}")
        selected_choice = None

        if selected_id:
            selected_choice = Choice.objects.filter(
                id=selected_id,
                question=question,
            ).first()

        Submission.objects.create(
            learner=learner,
            question=question,
            selected_choice=selected_choice,
            is_correct=bool(selected_choice and selected_choice.is_correct),
        )

    return redirect("onlinecourse:show_exam_result", course_id=course.id)


@login_required
def show_exam_result(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    submissions = Submission.objects.filter(
        learner=learner,
        question__lesson__course=course,
    ).select_related("question", "selected_choice")

    total_score = sum(
        submission.question.points
        for submission in submissions
        if submission.is_correct
    )
    max_score = sum(
        submission.question.points
        for submission in submissions
    )
    percentage = round((total_score / max_score) * 100, 2) if max_score else 0

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "course": course,
            "submissions": submissions,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
        },
    )
