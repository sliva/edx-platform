"""
Tests for the Course Home Course Metadata API in the Course Home API
"""

from datetime import datetime, timedelta
import ddt
import mock

from django.urls import reverse
from pytz import UTC

from edx_toggles.toggles.testutils import override_waffle_flag
from common.djangoapps.course_modes.models import CourseMode
from lms.djangoapps.courseware.toggles import (
    COURSEWARE_MICROFRONTEND_PROGRESS_MILESTONES,
    COURSEWARE_MICROFRONTEND_PROGRESS_MILESTONES_STREAK_CELEBRATION,
    REDIRECT_TO_COURSEWARE_MICROFRONTEND
)
from lms.djangoapps.course_home_api.tests.utils import BaseCourseHomeTests
from common.djangoapps.student.models import (
    CourseEnrollment, STREAK_LENGTH_TO_CELEBRATE, UserCelebration
)
from common.djangoapps.student.tests.factories import UserFactory


@ddt.ddt
@override_waffle_flag(REDIRECT_TO_COURSEWARE_MICROFRONTEND, active=True)
@override_waffle_flag(COURSEWARE_MICROFRONTEND_PROGRESS_MILESTONES, active=True)
@override_waffle_flag(COURSEWARE_MICROFRONTEND_PROGRESS_MILESTONES_STREAK_CELEBRATION, active=True)
class CourseHomeMetadataTests(BaseCourseHomeTests):
    """
    Tests for the Course Home Course Metadata API
    """
    def setUp(self):
        super().setUp()
        self.url = reverse('course-home-course-metadata', args=[self.course.id])

    def test_get_authenticated_user(self):
        CourseEnrollment.enroll(self.user, self.course.id, CourseMode.VERIFIED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data.get('is_staff'))
        # 'Course', 'Wiki', 'Progress' tabs
        self.assertEqual(len(response.data.get('tabs', [])), 3)

    def test_get_authenticated_staff_user(self):
        self.client.logout()
        staff_user = UserFactory(
            username='staff',
            email='staff@example.com',
            password='bar',
            is_staff=True
        )
        self.client.login(username=staff_user.username, password='bar')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_staff'])
        # This differs for a staff user because they also receive the Instructor tab
        # 'Course', 'Wiki', 'Progress', and 'Instructor' tabs
        self.assertEqual(len(response.data.get('tabs', [])), 4)

    def test_get_unknown_course(self):
        url = reverse('course-home-course-metadata', args=['course-v1:unknown+course+2T2020'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_happy_path_for_streak(self):
        """ Test that metadata endpoint returns correct data for the streak celebration"""
        CourseEnrollment.enroll(self.user, self.course.id, 'audit')

        today = datetime.now(UTC)
        for i in range(1, STREAK_LENGTH_TO_CELEBRATE + 1):
            with mock.patch.object(UserCelebration, '_get_now') as get_now_mock:
                get_now_mock.return_value = today + timedelta(days=i)
                response = self.client.get(self.url, content_type='application/json')
                should_celebrate = response.json()['celebrations']['should_celebrate_streak']
                self.assertEqual(should_celebrate, i == STREAK_LENGTH_TO_CELEBRATE)

    @mock.patch.object(UserCelebration, 'perform_streak_updates')
    def test_streak_masquerade(self, perform_streak_updates_mock):
        """ Don't update streak data when masquerading as a specific student """
        self.user.is_staff = True
        self.user.save()

        user = UserFactory()
        CourseEnrollment.enroll(user, self.course.id, 'verified')

        self.update_masquerade(username=user.username)
        now = datetime.now(UTC)
        for i in range(1, STREAK_LENGTH_TO_CELEBRATE + 1):
            with mock.patch.object(UserCelebration, '_get_now') as get_now_mock:
                get_now_mock.return_value = now + timedelta(days=i)
                response = self.client.get(self.url, content_type='application/json')
                should_celebrate = response.json()['celebrations']['should_celebrate_streak']
                self.assertEqual(should_celebrate, False)
                perform_streak_updates_mock.assert_not_called()
