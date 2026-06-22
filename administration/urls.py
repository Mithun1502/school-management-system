from django.urls import path
from . import views

urlpatterns = [
    # admin
    path("", views.admin_login, name="admin_login"),
    path("teacher-student-login/", views.user_login, name="user_login"),
    # dashboards
    path("teacher-dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # logout
    path("student-logout/", views.student_logout, name="student_logout"),
    path("teacher-logout/", views.teacher_logout, name="teacher_logout"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
    # admin functions
    path("add-teacher/", views.add_teacher, name="add_teacher"),
    path("add-standard/", views.add_standard, name="add_standard"),
    path("view-standards/", views.view_standards, name="view_standards"),
    path("edit-standard/<int:id>/", views.edit_standard, name="edit_standard"),
    path("delete-standard/<int:id>/", views.delete_standard, name="delete_standard"),
    path("add-student/", views.add_student, name="add_student"),
    path(
        "admin-edit-student/<int:id>/",
        views.admin_edit_student,
        name="admin_edit_student",
    ),
    path(
        "admin-delete-student/<int:id>/",
        views.admin_delete_student,
        name="admin_delete_student",
    ),
    path(
        "view-students/",
        views.view_students,
        name="view_students",
    ),
    path(
        "view-students/<str:standard>/",
        views.view_students_by_standard,
        name="view_students_by_standard",
    ),
    # teacher functions
    path("get-teacher/", views.get_teacher, name="get_teacher"),
    path("teacher-add-student/", views.teacher_add_student, name="teacher_add_student"),
    path("get-roll-number/", views.get_roll_number, name="get_roll_number"),
    path(
        "teacher-edit-student/<int:id>/",
        views.teacher_edit_student,
        name="teacher_edit_student",
    ),
    path(
        "teacher-delete-student/<int:id>/",
        views.teacher_delete_student,
        name="teacher_delete_student",
    ),
    path(
        "teacher-view-students/",
        views.teacher_view_students,
        name="teacher_view_students",
    ),
    path("view-teachers/", views.view_teachers, name="view_teachers"),
    path("edit-teacher/<int:id>/", views.edit_teacher, name="edit_teacher"),
    path("delete-teacher/<int:id>/", views.delete_teacher, name="delete_teacher"),
    path(
        "student-profile/",
        views.student_profile,
        name="student_profile",
    ),
    path("student-marks/", views.student_marks, name="student_marks"),
    path("student-attendance/", views.student_attendance, name="student_attendance"),
    path("student-events/", views.student_events, name="student_events"),
    path("student-id/", views.student_id, name="student_id"),

]
