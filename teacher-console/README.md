# TeacherConsole

Analytics dashboard for teachers to monitor class performance, identify at-risk students, and act on recommendations.

## Backend
```bash
cd teacher-console/backend
npm install
npm run dev
```
Env in backend/.env:
- `PORT=4000`
- `JWT_SECRET=your_jwt_secret`
- Microservice URLs (`PREPA_DATA_URL`, `STUDENT_PROFILER_URL`, `PATH_PREDICTOR_URL`, `RECO_BUILDER_URL`)

## Frontend
```bash
cd teacher-console/frontend
npm install
npm run dev
```
Env in frontend `.env`:
- `VITE_API_URL=http://localhost:4000/api`

Login: store a `token` in `localStorage` (temporary) to call protected endpoints.
