# Galpão Tênis de Mesa - Sistema de Check-in

## Overview

This is a Flask-based web application for managing table tennis session reservations at a sports facility. The system provides a dual-access interface for both students and administrators, handling session bookings, credit management, and attendance tracking.

## User Preferences

Preferred communication style: Simple, everyday language.
Timezone preference: Brazil time (GMT-3) for cancellation policies.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Session Management**: Flask sessions with configurable secret key
- **Data Models**: Relational database with proper foreign keys and constraints
- **Template Engine**: Jinja2 (Flask's default)

### Frontend Architecture
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Font Awesome for consistent iconography
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Styling**: Custom CSS with CSS variables for theming

### Data Storage Solutions
- **PostgreSQL Database**: Relational database with three main tables
  - `alunos`: Student information (id, name, password, payment status, credits, timestamps)
  - `checkins`: Check-in records with foreign key relationships (id, student_id, date, time_slot, timestamps)
  - `admin_config`: Administrative configuration settings (admin password, system settings)
- **Data Migration**: Automatic migration from JSON files to database on first run
- **Relationships**: Proper foreign key constraints between students and check-ins

## Key Components

### Authentication System
- **Dual login interface**: Separate access for students and administrators
- **Session-based authentication**: Uses Flask sessions to maintain user state
- **Password protection**: 
  - Administrator access protected by password "bolinha"
  - Student access requires individual passwords (auto-generated from name if not specified)
  - Secure login validation for both user types

### Reservation System
- **Time slots**: Two fixed time periods (18:00-20:00, 20:00-22:00)
- **Capacity management**: Maximum 12 players per time slot
- **Credit system**: Students use credits to book sessions

### Administrative Panel
- **Student management**: Add new students with credit allocation and password management
- **Payment tracking**: Record payment information for each student
- **Credit management**: Assign and track student credits
- **Check-in reports**: Daily and weekly check-in summaries with detailed statistics
- **Real-time monitoring**: View current day check-ins by time slot and weekly activity per student

## Data Flow

1. **Student Login**: Student enters name and password → System validates credentials → Access granted to booking panel
2. **Admin Login**: Administrator enters password → System validates admin credentials → Access granted to management interface
3. **Booking Process**: Student selects time slot → System checks credits and capacity → Reservation confirmed → Credits deducted
4. **Data Persistence**: All changes immediately saved to PostgreSQL database
5. **Reporting**: System automatically generates daily and weekly check-in reports for administrators

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI components and responsive grid system
- **Font Awesome 6.4.0**: Icon library for consistent visual elements

### Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database engine with psycopg2 adapter
- **Standard library modules**: `json`, `datetime`, `os` for utilities and date handling

## Deployment Strategy

### Environment Configuration
- **Secret key**: Configurable via `SESSION_SECRET` environment variable with fallback
- **File permissions**: Requires write access to `data/` directory
- **Static assets**: Served through Flask's static file handling

### File Structure
```
/
├── main.py                 # Main Flask application
├── models.py              # Database models (Aluno, Checkin, Admin)
├── data/                   # Legacy JSON data (auto-migrated)
│   ├── alunos.json        # Student records (migrated to DB)
│   └── checkins.json      # Check-in data (migrated to DB)
├── static/                # Static assets
│   ├── style.css          # Custom styling
│   └── script.js          # Client-side functionality
└── templates/             # Jinja2 templates
    ├── base.html          # Base template
    ├── login.html         # Dual login interface
    ├── admin_login.html   # Admin password login
    ├── admin.html         # Admin panel with reports
    ├── usuario.html       # Student login with password
    └── painel_usuario.html # Student dashboard
```

### Scalability Considerations
- **Database-driven**: PostgreSQL provides robust data storage with ACID compliance
- **Optimized queries**: Database indexes on frequently queried fields (date, time_slot, student_id)
- **Connection pooling**: Configured for efficient database connection management
- **Session management**: Uses server-side sessions, ready for multi-instance deployment

### Security Notes
- **Session security**: Configurable secret key for session encryption
- **Access control**: Password-based authentication for both administrators and students
- **Admin security**: Fixed administrator password ("bolinha") for secure access
- **Student security**: Individual passwords (auto-generated or manually set)
- **Data validation**: Input sanitization and form validation implemented
- **Session management**: Separate admin and user sessions with proper logout functionality