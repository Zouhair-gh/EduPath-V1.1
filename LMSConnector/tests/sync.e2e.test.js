import { syncMoodleSource } from '../src/services/sync.service.js';
import { MoodleClient } from '../src/connectors/moodle.js';

jest.mock('../src/connectors/moodle.js');

const sampleCourses = [{ id: 1, fullname: 'Course A', shortname: 'A', categoryid: 10, visible: true }];
const sampleUsers = [{ id: 100, email: 'u@example.com', firstname: 'U', lastname: 'Ser', username: 'user', lastaccess: Math.floor(Date.now()/1000) }];
const sampleGrades = { usergrades: [{ gradeitems: [{ itemname: 'Quiz 1', graderaw: 85, grademax: 100, grademodified: Math.floor(Date.now()/1000) }] }] };
const sampleCompletions = { statuses: [{ cmid: 200, state: 1, timemodified: Math.floor(Date.now()/1000) }] };

MoodleClient.mockImplementation(() => ({
  getSiteInfo: jest.fn().mockResolvedValue({}),
  getCourses: jest.fn().mockResolvedValue(sampleCourses),
  getEnrolledUsers: jest.fn().mockResolvedValue(sampleUsers),
  getUserGradeItems: jest.fn().mockResolvedValue(sampleGrades),
  getActivitiesCompletionStatus: jest.fn().mockResolvedValue(sampleCompletions),
}));

test('syncMoodleSource processes records without throwing', async () => {
  // Skip actual DB by monkey-patching getPool
  jest.unstable_mockModule('../src/db/pool.js', () => ({ getPool: () => ({
    query: jest.fn().mockResolvedValue({ rows: [{ id: 'job-1' }] })
  }) }));
  const source = { id: 'src-1', base_url: 'https://fake', token: 't' };
  await expect(syncMoodleSource(source)).resolves.toBeDefined();
});
