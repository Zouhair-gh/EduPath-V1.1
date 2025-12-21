import axios from 'axios';
import axiosRetry from 'axios-retry';
import CircuitBreaker from 'opossum';
import { logger } from '../common/logger.js';

export class MoodleClient {
  constructor({ baseUrl, token }) {
    this.baseUrl = baseUrl;
    this.token = token;
    this.restEndpoint = `${this.baseUrl}/webservice/rest/server.php`;
  }

  async call(wsfunction, params = {}) {
    const searchParams = new URLSearchParams();
    searchParams.append('wstoken', this.token);
    searchParams.append('wsfunction', wsfunction);
    searchParams.append('moodlewsrestformat', 'json');
    Object.entries(params).forEach(([k, v]) => {
      if (Array.isArray(v)) {
        v.forEach((val, idx) => searchParams.append(`${k}[${idx}]`, val));
      } else if (typeof v === 'object' && v !== null) {
        Object.entries(v).forEach(([kk, vv]) => searchParams.append(`${k}[${kk}]`, vv));
      } else if (v !== undefined && v !== null) {
        searchParams.append(k, v);
      }
    });

    // Axios retry policy
    axiosRetry(axios, {
      retries: 3,
      retryDelay: (count) => Math.min(1000 * Math.pow(2, count), 8000),
      retryCondition: (error) => {
        return axiosRetry.isNetworkOrIdempotentRequestError(error) || (error.response && error.response.status >= 500);
      },
    });

    const exec = async () => {
      const { data } = await axios.post(this.restEndpoint, searchParams);
      if (data && data.exception) {
        const err = new Error(`${data.errorcode || 'MOODLE_ERROR'}: ${data.message}`);
        err.code = data.errorcode;
        throw err;
      }
      return data;
    };

    // Circuit breaker
    if (!this.breaker) {
      this.breaker = new CircuitBreaker(exec, {
        timeout: 15000,
        errorThresholdPercentage: 50,
        resetTimeout: 30000,
      });
      this.breaker.on('open', () => logger.warn('Moodle breaker opened'));
      this.breaker.on('halfOpen', () => logger.info('Moodle breaker half-open'));
      this.breaker.on('close', () => logger.info('Moodle breaker closed'));
    }
    return this.breaker.fire();
  }

  async getSiteInfo() {
    return this.call('core_webservice_get_site_info');
  }

  async getCourses() {
    const data = await this.call('core_course_get_courses');
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.courses)) return data.courses;
    return [];
  }

  async getEnrolledUsers(courseid) {
    const data = await this.call('core_enrol_get_enrolled_users', { courseid });
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.users)) return data.users;
    return [];
  }

  async getUserGradeItems(courseid, userid) {
    return this.call('gradereport_user_get_grade_items', { courseid, userid });
  }

  async getActivitiesCompletionStatus(courseid, userid) {
    return this.call('core_completion_get_activities_completion_status', { courseid, userid });
  }

  async getForumDiscussions(forumid) {
    return this.call('mod_forum_get_forum_discussions', { forumid });
  }

  // Admin/create operations (require appropriate external service permissions)
  async createCourses(courses) {
    // courses: [{ fullname, shortname, categoryid, visible }]
    return this.call('core_course_create_courses', { courses });
  }

  async getCourseByField(field, value) {
    // field: 'id' | 'shortname' | 'idnumber' | 'fullname'
    const data = await this.call('core_course_get_courses_by_field', { field, value });
    if (data && Array.isArray(data.courses)) return data.courses;
    return [];
  }

  async createUsers(users) {
    // users: [{ username, password, email, firstname, lastname }]
    return this.call('core_user_create_users', { users });
  }

  async enrolUserManual(courseid, userid, roleid = 5) {
    // roleid: 5 => student
    const enrolments = [{ roleid, userid, courseid }];
    return this.call('enrol_manual_enrol_users', { enrolments });
  }
}
