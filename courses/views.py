import collections
import json
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from pytz import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import SharedCourseView
from courses.serializers import get_detailed_course_json, get_basic_course_json
from student.models import Student
from student.utils import get_classmates_from_course_id
from timetable.models import Semester, Course, Updates
from timetable.school_mappers import school_code_to_name
from helpers.mixins import ValidateSubdomainMixin, FeatureFlowView
from helpers.decorators import validate_subdomain


# TODO: use CBV
@validate_subdomain
def all_courses(request):
    school = request.subdomain
    school_name = school_code_to_name[school]  # TODO: use single groupby query
    dep_to_courses = collections.OrderedDict()
    departments = Course.objects.filter(school=school) \
        .order_by('department').values_list('department', flat=True).distinct()
    for department in departments:
        dep_to_courses[department] = Course.objects.filter(school=school,
                                                           department=department).all()
    context = {
        'course_map': dep_to_courses,
        'school': school,
        'school_name': school_name}
    return render_to_response("all_courses.html",
                              context,
                              context_instance=RequestContext(request))


# TODO: use implementation in student
def get_classmates_in_course(request, school, sem_name, year, course_id):
    school = school.lower()
    sem, _ = Semester.objects.get_or_create(name=sem_name, year=year)
    json_data = {}
    course = Course.objects.get(school=school, id=course_id)
    student = None
    logged = request.user.is_authenticated()
    if logged and Student.objects.filter(user=request.user).exists():
        student = Student.objects.get(user=request.user)
    if student and student.user.is_authenticated() and student.social_courses:
        json_data = get_classmates_from_course_id(
            school, student, course.id, sem)
    return HttpResponse(json.dumps(json_data), content_type="application/json")


# TODO delete or rewrite as CBV
@validate_subdomain
def course_page(request, code):
    school = request.subdomain
    try:
        school_name = school_code_to_name[school]
        course_obj = Course.objects.filter(code__iexact=code)[0]
        # TODO: hard coding (section type, semester)
        current_year = datetime.now().year
        semester, _ = Semester.objects.get_or_create(
            name='Fall', year=current_year)
        course_dict = get_basic_course_json(course_obj, semester)
        l = course_dict['sections'].get('L', {}).values()
        t = course_dict['sections'].get('T', {}).values()
        p = course_dict['sections'].get('P', {}).values()
        avg = round(course_obj.get_avg_rating(), 2)
        evals = course_dict['evals']
        clean_evals = evals
        for i, v in enumerate(evals):
            for k, e in v.items():
                if isinstance(evals[i][k], basestring):
                    clean_evals[i][k] = evals[i][k].replace(u'\xa0', u' ')
                if k == "year":
                    clean_evals[i][k] = evals[i][k].replace(":", " ")
        if school == "jhu":
            course_url = "/course/" + course_dict['code'] + "/F"
        else:
            course_url = "/course/" + course_dict['code'] + "/F"
        context = {
            'school': school,
            'school_name': school_name,
            'course': course_dict,
            'lectures': l if l else None,
            'tutorials': t if t else None,
            'practicals': p if p else None,
            'url': course_url,
            'evals': clean_evals,
            'avg': avg
        }
        return render_to_response("course_page.html",
                                  context,
                                  context_instance=RequestContext(request))
    except Exception as e:
        return HttpResponse(str(e))


class CourseDetail(ValidateSubdomainMixin, APIView):

    def get(self, request, sem_name, year, course_id):
        school = request.subdomain
        sem, _ = Semester.objects.get_or_create(name=sem_name, year=year)
        course = get_object_or_404(Course, school=school, id=course_id)
        student = None
        is_logged_in = request.user.is_authenticated()
        if is_logged_in and Student.objects.filter(user=request.user).exists():
            student = Student.objects.get(user=request.user)
        json_data = get_detailed_course_json(school, course, sem, student)
        return Response(json_data, status=status.HTTP_200_OK)


class SchoolList(APIView):

    def get(self, request, school):
        last_updated = None
        if Updates.objects.filter(
                school=school, update_field="Course").exists():
            update_time_obj = Updates.objects.get(school=school, update_field="Course") \
                .last_updated.astimezone(timezone('US/Eastern'))
            last_updated = update_time_obj.strftime('%Y-%m-%d %H:%M') + " " + update_time_obj.tzname()
        json_data = {
            'areas': sorted(list(Course.objects.filter(school=school)
                                 .exclude(areas__exact='')
                                 .values_list('areas', flat=True)
                                 .distinct())),
            'departments': sorted(list(Course.objects.filter(school=school)
                                       .exclude(department__exact='')
                                       .values_list('department', flat=True)
                                       .distinct())),
            'levels': sorted(list(Course.objects.filter(school=school)
                                  .exclude(level__exact='')
                                  .values_list('level', flat=True)
                                  .distinct())),
            'last_updated': last_updated
        }
        return Response(json_data, status=status.HTTP_200_OK)


class CourseModal(FeatureFlowView):
    feature_name = "SHARE_COURSE"

    def get_feature_flow(self, request, code, sem_name, year):
        semester, _ = Semester.objects.get_or_create(name=sem_name, year=year)
        code = code.upper()
        course = get_object_or_404(Course, school=self.school, code=code)
        course_json = get_detailed_course_json(
            self.school, course, semester, self.student)

        # analytics
        SharedCourseView.objects.create(
            student=self.student,
            shared_course=course,
        ).save()

        return {'sharedCourse': course_json, 'semester': semester}