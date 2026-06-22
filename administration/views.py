from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import Teacher, Standard, Student

# to protect the password
from django.contrib.auth.hashers import make_password

# to check the password
from django.contrib.auth.hashers import check_password

# regex checking ku python oda default package
import re

# json response for ajax
from django.http import JsonResponse

# 404 error kaaga
from django.shortcuts import get_object_or_404


# main - school_admin login
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "school_admin" and password == "Password@1215":
            request.session["admin_logged_in"] = True
            return redirect("admin_dashboard")

        messages.error(request, "Invalid Username or Password")

    return render(request, "admin_login.html")


def admin_dashboard(request):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    total_standards = Standard.objects.count()
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_standards": total_standards,
            "total_teachers": total_teachers,
            "total_students": total_students,
        },
    )


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Teacher Login
        teacher = Teacher.objects.filter(username=username).first()

        if teacher and check_password(password, teacher.password):
            request.session["teacher_id"] = teacher.id
            request.session["teacher_name"] = teacher.name

            return redirect("teacher_dashboard")

        # Student Login
        student = Student.objects.filter(username=username).first()

        if student and check_password(password, student.password):

            request.session["student_id"] = student.id
            request.session["student_name"] = student.name

            messages.success(request, "Student Login Successful")

            return redirect("student_dashboard")

        messages.error(request, "Invalid Credentials")

    return render(request, "user_login.html")


def teacher_dashboard(request):
    if not request.session.get("teacher_id"):
        messages.error(request, "Please login first")
        return redirect("user_login")

    teacher = Teacher.objects.get(id=request.session["teacher_id"])

    return render(request, "teacher_dashboard.html", {"teacher": teacher})


def student_dashboard(request):

    if not request.session.get("student_id"):
        messages.error(request, "Please login first")
        return redirect("user_login")

    student = Student.objects.get(id=request.session["student_id"])

    return render(
        request,
        "student_dashboard.html",
        {"student": student},
    )


def teacher_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect("user_login")


def student_logout(request):

    request.session.flush()

    messages.success(request, "Logged out successfully")

    return redirect("user_login")


def add_teacher(request):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    assigned_standards = Teacher.objects.values_list("standard", flat=True)

    standards = sorted(
        Standard.objects.exclude(standard_name__in=assigned_standards),
        key=lambda x: int(x.standard_name.split()[-1]),
    )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        standard = request.POST.get("standard", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        address = request.POST.get("address", "").strip()
        bank_account_number = request.POST.get("bank_account_number", "").strip()

        bank_branch = request.POST.get("bank_branch", "").strip()

        ifsc_code = request.POST.get("ifsc_code", "").strip().upper()

        if not all(
            [
                name,
                standard,
                phone,
                email,
                username,
                password,
                confirm_password,
                address,
                bank_account_number,
                bank_branch,
                ifsc_code,
            ]
        ):
            messages.error(request, "All fields are required")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[A-Za-z ]{3,25}$", name):
            messages.error(
                request,
                "Name must contain only letters and spaces (3-25 characters)",
            )
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not Standard.objects.filter(standard_name=standard).exists():
            messages.error(request, "Selected standard does not exist")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if Teacher.objects.filter(standard=standard).exists():
            messages.error(request, f"{standard} already has a teacher assigned")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if len(address) < 10 or len(address) > 200:
            messages.error(request, "Address must be between 10 and 200 characters")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[6789]\d{9}$", phone):
            messages.error(
                request,
                "Phone number must be 10 digits and start with 6, 7, 8 or 9",
            )
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        if Teacher.objects.filter(bank_account_number=bank_account_number).exists():
            messages.error(request, "Bank account number already exists")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            messages.error(request, "Only Gmail addresses are allowed")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$", username):
            messages.error(
                request,
                "Username must start with a letter and contain 4-20 characters",
            )
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        reserved_usernames = ["admin", "school_admin", "root", "teacher", "student"]

        if username.lower() in reserved_usernames:
            messages.error(request, "This username is not allowed")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?#&])[A-Za-z\d@$!%*?#&]{8,}$",
            password,
        ):
            messages.error(
                request,
                "Password must contain uppercase, lowercase, number and special character",
            )
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if Teacher.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        if Teacher.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        if Teacher.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if len(email) > 100:
            messages.error(request, "Email is too long")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        if not re.match(r"^[A-Za-z .,-]{3,50}$", bank_branch):
            messages.error(
                request,
                "Bank branch must contain only letters, spaces, dot (.), comma (,) and hyphen (-) (3-50 characters)",
            )
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^\d{9,18}$", bank_account_number):
            messages.error(request, "Bank account number must be 9-18 digits")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc_code):
            messages.error(request, "Enter a valid IFSC code")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if "  " in name:
            messages.error(request, "Multiple spaces are not allowed in name")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if "  " in bank_branch:
            messages.error(request, "Multiple spaces are not allowed in branch name")
            return render(
                request,
                "add_teacher.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        Teacher.objects.create(
            name=name,
            standard=standard,
            phone=phone,
            email=email,
            username=username,
            password=make_password(password),
            address=address,
            bank_account_number=bank_account_number,
            bank_branch=bank_branch,
            ifsc_code=ifsc_code,
        )

        messages.success(request, "Teacher Added Successfully")
        return redirect("admin_dashboard")

    return render(request, "add_teacher.html", {"standards": standards})


def add_standard(request):

    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    if request.method == "POST":
        standard_name = request.POST.get("standard_name", "").strip()

        # Only numbers allowed
        if not standard_name.isdigit():
            messages.error(request, "Only numbers from 1 to 12 are allowed")
            return redirect("add_standard")

        standard_number = int(standard_name)

        # Allow only 1 to 12
        if standard_number < 1 or standard_number > 12:
            messages.error(request, "Standard must be between 1 and 12")
            return redirect("add_standard")

        # Save as STANDARD 1, STANDARD 2, etc daa easy dhan..
        final_standard_name = f"STANDARD {standard_number}"

        if Standard.objects.filter(standard_name__iexact=final_standard_name).exists():
            messages.error(request, "Standard already exists")
            return redirect("add_standard")

        Standard.objects.create(standard_name=final_standard_name)

        messages.success(request, f"{final_standard_name} Added Successfully")
        return redirect("view_standards")

    return render(request, "add_standard.html")


def view_standards(request):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    standards = sorted(
        Standard.objects.all(), key=lambda x: int(x.standard_name.split()[-1])
    )
    return render(request, "view_standards.html", {"standards": standards})


def edit_standard(request, id):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    standard = Standard.objects.get(id=id)

    if Teacher.objects.filter(standard=standard.standard_name).exists():
        messages.error(request, "Teacher assigned to this standard. Cannot edit.")
        return redirect("view_standards")

    if request.method == "POST":
        standard_name = request.POST.get("standard_name", "").strip()

        if not standard_name:
            messages.error(request, "Standard number is required")
            return redirect("edit_standard", id=id)

        if not standard_name.isdigit():
            messages.error(request, "Only numbers from 1 to 12 are allowed")
            return redirect("edit_standard", id=id)

        standard_number = int(standard_name)

        if standard_number < 1 or standard_number > 12:
            messages.error(request, "Standard must be between 1 and 12")
            return redirect("edit_standard", id=id)

        final_standard_name = f"STANDARD {standard_number}"

        if final_standard_name.lower() == standard.standard_name.lower():
            messages.error(
                request, "Please enter a different standard, Standard already exists!"
            )
            return redirect("edit_standard", id=id)

        if (
            Standard.objects.filter(standard_name__iexact=final_standard_name)
            .exclude(id=id)
            .exists()
        ):
            messages.error(request, "Standard already exists")
            return redirect("edit_standard", id=id)

        standard.standard_name = final_standard_name
        standard.save()

        messages.success(request, "Standard updated successfully")
        return redirect("view_standards")

    return render(request, "edit_standard.html", {"standard": standard})


def delete_standard(request, id):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    standard = Standard.objects.get(id=id)

    if Teacher.objects.filter(standard=standard.standard_name).exists():
        messages.error(
            request,
            f"{standard.standard_name} is assigned to a teacher and cannot be deleted",
        )
        return redirect("view_standards")

    standard_name = standard.standard_name
    standard.delete()

    messages.success(request, f"{standard_name} deleted successfully")
    return redirect("view_standards")


def add_student(request):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    standards = sorted(
        Standard.objects.all(), key=lambda x: int(x.standard_name.split()[-1])
    )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        standard = request.POST.get("standard", "").strip()

        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not all([name, standard, phone, email, username, password]):
            messages.error(request, "All fields are required")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[A-Za-z ]{3,25}$", name):
            messages.error(
                request,
                "Student name must contain only letters and spaces (3-25 characters)",
            )
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if "  " in name:
            messages.error(
                request,
                "Multiple spaces are not allowed in student name",
            )
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if " " in email:
            messages.error(request, "Email cannot contain spaces")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if Student.objects.filter(name__iexact=name, standard=standard).exists():
            messages.error(request, f"Student '{name}' already exists in {standard}")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if Student.objects.filter(phone=phone).exists():
            messages.error(request, "Phone Number already exists")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[6789]\d{9}$", phone):
            messages.error(request, "Enter valid phone number")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?#&])[A-Za-z\d@$!%*?#&]{8,}$",
            password,
        ):
            messages.error(
                request,
                "Password must contain uppercase, lowercase, number and special character",
            )
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$", username):
            messages.error(
                request,
                "Username must start with a letter and contain 4-20 characters",
            )
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )
        if Student.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            messages.error(request, "Only Gmail addresses allowed")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        teacher = Teacher.objects.filter(standard=standard).first()

        if not teacher:
            messages.error(request, f"No teacher assigned for {standard}")
            return render(
                request,
                "add_student.html",
                {
                    "standards": standards,
                    "form_data": request.POST,
                },
            )

        Student.objects.create(
            name=name,
            standard=teacher.standard,
            roll_number=generate_roll_number(teacher.standard),
            phone=phone,
            email=email,
            username=username,
            password=make_password(password),
            teacher=teacher,
        )

        messages.success(request, "Student Added Successfully")
        return redirect("view_students")

    return render(
        request,
        "add_student.html",
        {"standards": standards},
    )


def admin_logout(request):
    request.session.flush()
    # messages.success(request, "Logged out successfully")
    return redirect("admin_login")


def get_teacher(request):
    standard = request.GET.get("standard")

    teacher = Teacher.objects.filter(standard=standard).first()

    if teacher:
        return JsonResponse({"teacher_name": teacher.name})

    return JsonResponse({"teacher_name": ""})


def teacher_add_student(request):

    if not request.session.get("teacher_id"):
        messages.error(request, "Please login first")
        return redirect("user_login")

    teacher = Teacher.objects.get(id=request.session["teacher_id"])

    if request.method == "POST":

        name = request.POST.get("name", "").strip()

        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        context = {
            "teacher": teacher,
            "roll_number": generate_roll_number(teacher.standard),
            "name": name,
            "phone": phone,
            "email": email,
        }
        if not all([name, phone, email, username, password]):
            messages.error(request, "All fields are required")
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            messages.error(request, "Only Gmail addresses allowed")
            return render(
                request,
                "teacher_add_student.html",
                context,
            )
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?#&])[A-Za-z\d@$!%*?#&]{8,}$",
            password,
        ):
            messages.error(
                request,
                "Password must contain uppercase, lowercase, number and special character",
            )
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if Student.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$", username):
            messages.error(
                request,
                "Username must start with a letter and contain 4-20 characters",
            )
            return render(
                request,
                "teacher_add_student.html",
                context,
            )
        if not re.match(r"^[A-Za-z ]{3,25}$", name):
            messages.error(
                request,
                "Student name must contain only letters and spaces (3-25 characters)",
            )
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if Student.objects.filter(phone=phone).exists():
            messages.error(request, "Phone Number already exists")
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if not re.match(r"^[6789]\d{9}$", phone):
            messages.error(request, "Enter valid phone number")
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        if Student.objects.filter(
            name__iexact=name, standard=teacher.standard
        ).exists():
            messages.error(
                request, f"Student '{name}' already exists in {teacher.standard}"
            )
            return render(
                request,
                "teacher_add_student.html",
                context,
            )

        Student.objects.create(
            name=name,
            standard=teacher.standard,
            roll_number=generate_roll_number(teacher.standard),
            phone=phone,
            email=email,
            username=username,
            password=make_password(password),
            teacher=teacher,
        )

        # messages.success(request, "Student Added Successfully")

        return redirect("teacher_view_students")

    return render(
        request,
        "teacher_add_student.html",
        {"teacher": teacher, "roll_number": generate_roll_number(teacher.standard)},
    )


def generate_roll_number(standard):
    standard_no = standard.split()[-1]

    last_student = Student.objects.filter(standard=standard).order_by("-id").first()

    if last_student:
        last_roll = int(last_student.roll_number)
        return str(last_roll + 1)

    return f"{standard_no}001"


def view_students(request):
    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    standards = sorted(
        Standard.objects.all(), key=lambda x: int(x.standard_name.split()[-1])
    )

    standard_data = []

    for standard in standards:
        count = Student.objects.filter(standard=standard.standard_name).count()

        standard_data.append({"standard": standard, "count": count})

    return render(request, "view_students.html", {"standard_data": standard_data})


def view_students_by_standard(request, standard):
    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    students = Student.objects.filter(standard=standard).order_by("roll_number")

    return render(
        request,
        "students_by_standard.html",
        {"students": students, "standard": standard},
    )


def admin_edit_student(request, id):

    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    student = Student.objects.get(id=id)

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not all([name, phone, email, username]):
            messages.error(request, "All fields are required")
            return redirect("admin_edit_student", id=id)

        if not re.match(r"^[A-Za-z ]{3,25}$", name):
            messages.error(
                request,
                "Student name must contain only letters and spaces (3-25 characters)",
            )
            return redirect("admin_edit_student", id=id)

        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            messages.error(request, "Only Gmail addresses allowed")
            return redirect("admin_edit_student", id=id)

        if not re.match(r"^[6789]\d{9}$", phone):
            messages.error(request, "Enter valid phone number")
            return redirect("admin_edit_student", id=id)

        if Student.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, "Email already exists")
            return redirect("admin_edit_student", id=id)

        if Student.objects.filter(phone=phone).exclude(id=id).exists():
            messages.error(request, "Phone Number already exists")
            return redirect("admin_edit_student", id=id)

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$", username):
            messages.error(
                request,
                "Username must start with a letter and contain 4-20 characters",
            )
            return redirect("admin_edit_student", id=id)

        if Student.objects.filter(username=username).exclude(id=id).exists():
            messages.error(request, "Username already exists")
            return redirect("admin_edit_student", id=id)

        if password and not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?#&])[A-Za-z\d@$!%*?#&]{8,}$",
            password,
        ):
            messages.error(
                request,
                "Password must contain uppercase, lowercase, number and special character",
            )
            return redirect("admin_edit_student", id=id)

        student.name = name
        student.phone = phone
        student.email = email
        student.username = username

        if password:
            student.password = make_password(password)

        student.save()


        messages.success(request, "Student Updated Successfully")

        return redirect(
            "view_students_by_standard",
            standard=student.standard,
        )

    return render(
        request,
        "admin_edit_student.html",
        {
            "student": student,
        },
    )


def admin_delete_student(request, id):

    if not request.session.get("admin_logged_in"):
        return redirect("admin_login")

    student = Student.objects.get(id=id)

    standard = student.standard

    student.delete()

    messages.success(request, "Student Deleted Successfully")

    return redirect(
        "view_students_by_standard",
        standard=standard,
    )


def get_roll_number(request):
    standard = request.GET.get("standard")

    roll_number = generate_roll_number(standard)

    return JsonResponse({"roll_number": roll_number})


def teacher_edit_student(request, id):

    if not request.session.get("teacher_id"):
        messages.error(request, "Please login first")
        return redirect("user_login")

    teacher = Teacher.objects.get(id=request.session["teacher_id"])

    student = Student.objects.filter(id=id, teacher=teacher).first()

    if not student:
        messages.error(request, "Student not found")
        return redirect("teacher_dashboard")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not all([name, phone, email, username]):
            messages.error(request, "All fields are required")
            return redirect("teacher_edit_student", id=id)

        if not re.match(r"^[A-Za-z ]{3,25}$", name):
            messages.error(
                request,
                "Student name must contain only letters and spaces (3-25 characters)",
            )
            return redirect("teacher_edit_student", id=id)

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$", username):
            messages.error(
                request,
                "Username must start with a letter and contain 4-20 characters",
            )
            return redirect("teacher_edit_student", id=id)

        if Student.objects.filter(username=username).exclude(id=id).exists():
            messages.error(request, "Username already exists")
            return redirect("teacher_edit_student", id=id)

        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            messages.error(request, "Only Gmail addresses allowed")
            return redirect("teacher_edit_student", id=id)

        if not re.match(r"^[6789]\d{9}$", phone):
            messages.error(request, "Enter valid phone number")
            return redirect("teacher_edit_student", id=id)

        if (
            Student.objects.filter(name__iexact=name, standard=student.standard)
            .exclude(id=id)
            .exists()
        ):

            messages.error(
                request, f"Student '{name}' already exists in {student.standard}"
            )
            return redirect("teacher_edit_student", id=id)

        if "  " in name:
            messages.error(request, "Multiple spaces are not allowed in student name")
            return redirect("teacher_edit_student", id=id)

        if Student.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, "Email already exists")
            return redirect("teacher_edit_student", id=id)

        if Student.objects.filter(phone=phone).exclude(id=id).exists():
            messages.error(request, "Phone Number already exists")
            return redirect("teacher_edit_student", id=id)

        student.name = name
        student.phone = phone
        student.email = email
        student.username = username

        if password:
            student.password = make_password(password)

        student.save()

        messages.success(request, "Student Updated Successfully")
        return redirect("teacher_view_students")

    return render(
        request,
        "teacher_edit_student.html",
        {
            "teacher": teacher,
            "student": student,
        },
    )


def teacher_view_students(request):

    if not request.session.get("teacher_id"):
        return redirect("user_login")

    teacher = Teacher.objects.get(id=request.session["teacher_id"])

    students = Student.objects.filter(teacher=teacher).order_by("roll_number")

    return render(
        request,
        "teacher_view_students.html",
        {"teacher": teacher, "students": students},
    )


def teacher_delete_student(request, id):

    if not request.session.get("teacher_id"):
        return redirect("user_login")

    teacher = Teacher.objects.get(id=request.session["teacher_id"])

    student = Student.objects.filter(id=id, teacher=teacher).first()

    if not student:
        messages.error(request, "Student not found")
        return redirect("teacher_view_students")

    student.delete()

    messages.success(request, "Student Deleted Successfully")

    return redirect("teacher_view_students")


def view_teachers(request):

    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    teachers = Teacher.objects.all().order_by("standard")

    teacher_data = []

    for teacher in teachers:

        student_count = Student.objects.filter(teacher=teacher).count()

        teacher_data.append(
            {
                "teacher": teacher,
                "student_count": student_count,
            }
        )

    return render(
        request,
        "view_teachers.html",
        {
            "teacher_data": teacher_data,
        },
    )


def edit_teacher(request, id):

    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    teacher = get_object_or_404(Teacher, id=id)

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        standard = request.POST.get("standard", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip()
        address = request.POST.get("address", "").strip()
        bank_account_number = request.POST.get("bank_account_number", "").strip()
        bank_branch = request.POST.get("bank_branch", "").strip()
        ifsc_code = request.POST.get("ifsc_code", "").strip().upper()

        if not all(
            [
                name,
                standard,
                phone,
                email,
                username,
                address,
                bank_account_number,
                bank_branch,
                ifsc_code,
            ]
        ):
            messages.error(request, "All fields are required")
            return redirect("edit_teacher", id=id)

        if not re.match(r"^[A-Za-z ]{3,25}$", name):
            messages.error(
                request,
                "Name must contain only letters and spaces (3-25 characters)",
            )
            return redirect("edit_teacher", id=id)

        if not Standard.objects.filter(standard_name=standard).exists():
            messages.error(request, "Selected standard does not exist")
            return redirect("edit_teacher", id=id)

        if Teacher.objects.filter(standard=standard).exclude(id=id).exists():

            messages.error(request, f"{standard} already has a teacher assigned")
            return redirect("edit_teacher", id=id)

        if len(address) < 10 or len(address) > 200:
            messages.error(request, "Address must be between 10 and 200 characters")
            return redirect("edit_teacher", id=id)

        if not re.match(r"^[6789]\d{9}$", phone):
            messages.error(
                request,
                "Phone number must be 10 digits and start with 6, 7, 8 or 9",
            )
            return redirect("edit_teacher", id=id)

        if (
            Teacher.objects.filter(bank_account_number=bank_account_number)
            .exclude(id=id)
            .exists()
        ):

            messages.error(request, "Bank account number already exists")
            return redirect("edit_teacher", id=id)

        if not re.match(r"^[a-zA-Z0-9_.]+@gmail\.com$", email):
            messages.error(request, "Only Gmail addresses are allowed")
            return redirect("edit_teacher", id=id)

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$", username):
            messages.error(
                request,
                "Username must start with a letter and contain 4-20 characters",
            )
            return redirect("edit_teacher", id=id)

        reserved_usernames = [
            "admin",
            "school_admin",
            "root",
            "teacher",
            "student",
        ]

        if username.lower() in reserved_usernames:
            messages.error(request, "This username is not allowed")
            return redirect("edit_teacher", id=id)

        if Teacher.objects.filter(username=username).exclude(id=id).exists():

            messages.error(request, "Username already exists")
            return redirect("edit_teacher", id=id)

        if Teacher.objects.filter(email=email).exclude(id=id).exists():

            messages.error(request, "Email already exists")
            return redirect("edit_teacher", id=id)

        if Teacher.objects.filter(phone=phone).exclude(id=id).exists():

            messages.error(request, "Phone number already exists")
            return redirect("edit_teacher", id=id)

        if " " in email:
            messages.error(request, "Email cannot contain spaces")
            return redirect("edit_teacher", id=id)

        if " " in username:
            messages.error(request, "Username cannot contain spaces")
            return redirect("edit_teacher", id=id)

        if len(email) > 100:
            messages.error(request, "Email is too long")
            return redirect("edit_teacher", id=id)

        if not re.match(r"^[A-Za-z .,-]{3,50}$", bank_branch):
            messages.error(
                request,
                "Bank branch must contain only letters, spaces, dot (.), comma (,) and hyphen (-) (3-50 characters)",
            )
            return redirect("edit_teacher", id=id)

        if not re.match(r"^\d{9,18}$", bank_account_number):
            messages.error(request, "Bank account number must be 9-18 digits")
            return redirect("edit_teacher", id=id)

        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc_code):
            messages.error(request, "Enter a valid IFSC code")
            return redirect("edit_teacher", id=id)

        if "  " in name:
            messages.error(request, "Multiple spaces are not allowed in name")
            return redirect("edit_teacher", id=id)

        if "  " in bank_branch:
            messages.error(request, "Multiple spaces are not allowed in branch name")
            return redirect("edit_teacher", id=id)

        teacher.name = name
        teacher.standard = standard
        teacher.phone = phone
        teacher.email = email
        teacher.username = username
        teacher.address = address
        teacher.bank_account_number = bank_account_number
        teacher.bank_branch = bank_branch
        teacher.ifsc_code = ifsc_code

        teacher.save()

        messages.success(request, "Teacher Updated Successfully")

        return redirect("view_teachers")

    standards = Standard.objects.all().order_by("standard_name")

    return render(
        request,
        "edit_teacher.html",
        {
            "teacher": teacher,
            "standards": standards,
        },
    )


def delete_teacher(request, id):

    if not request.session.get("admin_logged_in"):
        messages.error(request, "Please login first")
        return redirect("admin_login")

    teacher = get_object_or_404(Teacher, id=id)

    student_count = Student.objects.filter(teacher=teacher).count()

    if student_count > 0:
        messages.error(request, "Cannot delete teacher. Students are assigned.")
        return redirect("view_teachers")

    teacher.delete()

    messages.success(request, "Teacher Deleted Successfully")

    return redirect("view_teachers")


def student_profile(request):

    if not request.session.get("student_id"):
        messages.error(request, "Please login first")
        return redirect("user_login")

    student = Student.objects.get(id=request.session["student_id"])

    return render(
        request,
        "student_profile.html",
        {"student": student},
    )


def student_marks(request):
    return render(request, "student_marks.html")


def student_attendance(request):
    return render(request, "student_attendance.html")


def student_id(request):
    return render(request, "student_id.html")


def student_events(request):
    return render(request, "student_events.html")
