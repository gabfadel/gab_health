# GAB Health

GAB Health is a web application for managing healthcare workflows: user registration, doctor management, appointment scheduling, medication lookup, and medical records.

---

## 1. Doctor Creation (Admin Panel)

1. **Create superuser** (if not already created):

   ```bash
   docker-compose up -d        # start services
   docker-compose exec backend python manage.py createsuperuser
   ```

   Follow prompts to set username, email, and password for the admin.

2. **Start the application** (if not already running):

   ```bash
   docker-compose up -d
   ```

3. Open the admin interface at [http://localhost:8000/admin](http://localhost:8000/admin).

4. Log in as superuser.

5. Navigate to **Users** (the built-in User model) and click **Add User**.

6. Fill in required fields:

   - **Username**
   - **Email** (used for login)
   - **Password**

7. In the same form, locate the **isDoctor** checkbox under the custom fields section. Check **isDoctor** to designate this user as a doctor.

8. Save the user. A new **Doctor** entry is automatically available via the `/api/doctors/` endpoints for any user with `isDoctor = true`.

You can verify:

- In the admin panel, use **Users** list and confirm the new user has **yes** under the **isDoctor** column.
- Using the API: `GET /api/doctors/` should list the new doctor user.

---

## 2. Patient Registration and Login (Frontend)

1. Open the frontend at [http://localhost:3000](http://localhost:3000).
2. Click **Sign Up** and complete the patient registration form (name, email, password).
3. Submit and you will be redirected to the login page.
4. Log in using the registered credentials.

Upon successful login, you land on the patient dashboard.

---

## 3. Scheduling Appointments (Frontend)

1. In the patient dashboard, click **New Appointment**.
2. Select:
   - **Doctor** from dropdown (lists all users with `isDoctor = true`).
   - **Date** and **Time** slot.
3. Click **Schedule**.
4. On success, you see a confirmation and the appointment appears under **My Appointments**.

---

## 4. Medication Lookup (FDA Integration)

1. In the patient dashboard, click **Medications**.
2. Enter a drug name (e.g., "aspirin") and click **Search**.
3. Results are fetched from the FDA public API and displayed client-side, showing drug name, purpose, and manufacturer.

No credentials or API keys are required for testing in development.

---

## 5. Medical Records (Frontend)

### 5.1 As a Doctor

1. Log in as a doctor.
2. Navigate to **Appointments** and select a patient appointment.
3. Click **Add Medical Record**.
4. Enter:
   - **Patient** (pre-filled from appointment context)
   - **Date** (defaults to today)
   - **Notes** (clinical observations, prescriptions)
5. Click **Save**.

### 5.2 As a Patient

1. Log in as a patient.
2. Go to **My Records**.
3. View the list of records created by doctors.
4. Click a record to see full details.

---

## 6. API Endpoints

| Resource             | Method | Path                             | Description                                         |
| -------------------- | ------ | -------------------------------- | --------------------------------------------------- |
| **Authentication**   | POST   | `/api/auth/login/`               | Log in a user (returns token).                      |
| **Users** (patients) | POST   | `/api/users/`                    | Register a new patient.                             |
|                      | GET    | `/api/users/{id}/`               | Get patient profile (self or admin).                |
| **Doctors**          | POST   | `/api/doctors/`                  | Create a new doctor (admin only).                   |
|                      | GET    | `/api/doctors/`                  | List all doctors (patients and admins).             |
|                      | GET    | `/api/doctors/{id}/`             | Retrieve a doctor’s profile.                        |
| **Appointments**     | POST   | `/api/appointments/`             | Create a new appointment (patient).                 |
|                      | GET    | `/api/appointments/`             | List appointments (filtered by role and ownership). |
|                      | GET    | `/api/appointments/{id}/`        | Retrieve appointment details.                       |
| **Medications**      | GET    | `/api/medications/?query={name}` | Search drugs via FDA integration (patient/doctor).  |
| **Medical Records**  | POST   | `/api/medical_records/`          | Add a medical record (doctor).                      |
|                      | GET    | `/api/medical_records/`          | List medical records (filtered by user and role).   |
|                      | GET    | `/api/medical_records/{id}/`     | Retrieve a single medical record.                   |

All endpoints require an `Authorization: Bearer <token>` header, except user registration and login.

---

## 7. Testing

### 7.1 API Tests (pytest)

From the backend directory:

```bash
pytest tests/test_doctors.py::TestDoctorEndpoints
pytest tests/test_users.py::TestUserRegistration
pytest tests/test_appointments.py::TestAppointmentFlow
pytest tests/test_medical_records.py::TestMedicalRecordsFlow
```

### 7.2 Frontend Tests (Jest / React Testing Library)

From the frontend directory:

```bash
npm install
npm run test
```

Tests cover:

- User signup and login forms
- Doctor selection dropdown
- Appointment booking flow
- Medication search component
- Medical records display and creation

---

## 8. Docker Compose (Local Development)

Use the provided `docker-compose.yml` to start all services:

```bash
docker-compose up
```

- **backend**: Django/Express API on port 8000
- **frontend**: Next.js app on port 3000
- **db**: PostgreSQL on port 5432
- **redis**: Redis on port 6379

To stop and remove containers:

```bash
docker-compose down
```

---

With these steps, you can fully test all GAB Health features via both API and frontend interfaces.

## 8. .env and .env.local examples
