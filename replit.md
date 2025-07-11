# Sistema de Pesagem de Caminhões

## Overview

This is a Flask-based web application for managing truck weighing operations. The system allows users to register truck weighing data, calculate cargo values based on location-specific lots, generate PDF tickets, and export reports. The application is designed for Brazilian truck weighing operations with Portuguese language support.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite as default (configurable via DATABASE_URL)
- **Session Management**: Flask sessions with configurable secret key
- **Proxy Support**: Werkzeug ProxyFix for deployment behind reverse proxies

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Data Storage
- **Primary Database**: SQLite (development) / PostgreSQL (production via DATABASE_URL)
- **ORM**: SQLAlchemy with declarative base
- **Database Features**: Connection pooling, automatic ping for connection health

## Key Components

### Models (models.py)
- **Pesagem Model**: Core entity storing truck weighing data
  - Fields: location data, date, vehicle plate, driver, product type, weight, lot, value
  - Automatic timestamp tracking
  - Dictionary conversion for JSON serialization

### Routes (routes.py)
- **Home Route** (`/`): Lists all weighing records
- **Registration Route** (`/registro`): Form for new weighing entries
- **Ticket Routes**: PDF generation and viewing for individual records
- **Report Routes**: Excel and CSV export functionality

### Utilities (utils.py)
- **Lot Calculation**: Determines lot category (3 or 5) based on pickup location
- **Value Calculation**: Computes cargo value using weight and lot-specific rates
- **PDF Generation**: Creates formatted tickets using ReportLab
- **Excel Export**: Generates reports using openpyxl

### Business Logic
- **Lot 3 Cities**: 16 locations with rate of R$ 575.75 per ton
- **Lot 5 Cities**: 13 locations with rate of R$ 591.82 per ton
- **Value Formula**: (Weight in kg / 1000) × Lot rate per ton

## Data Flow

1. **Registration Process**:
   - User fills form with truck and cargo details
   - System validates required fields and weight > 0
   - Pickup location determines lot category and rate
   - Cargo value calculated automatically
   - Record saved to database

2. **Ticket Generation**:
   - User requests ticket for specific weighing record
   - System generates PDF with formatted layout
   - Ticket includes all relevant weighing information

3. **Reporting**:
   - Users can export all records to Excel/CSV
   - Reports include calculated values and lot information

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and connection management
- **ReportLab**: PDF generation for tickets
- **openpyxl**: Excel file generation
- **Werkzeug**: WSGI utilities and proxy handling

### Frontend Dependencies
- **Bootstrap 5**: UI framework (loaded via CDN)
- **Font Awesome**: Icon library (loaded via CDN)
- **Custom CSS**: Application-specific styling

### Database Dependencies
- **SQLite**: Default database for development
- **PostgreSQL**: Production database (when DATABASE_URL is configured)

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database, debug mode enabled
- **Production**: PostgreSQL via DATABASE_URL, secure session key required
- **Proxy Support**: Configured for deployment behind reverse proxies

### Application Structure
- **app.py**: Main application factory and configuration
- **main.py**: Application entry point
- **Static Files**: CSS and JavaScript served via Flask
- **Templates**: Jinja2 templates with inheritance structure

### Key Configuration Points
- Database URL configurable via environment variable
- Session secret configurable for security
- Debug mode controllable for production deployment
- Connection pooling configured for database reliability

The application follows Flask best practices with clear separation of concerns, making it maintainable and deployable in various environments. The system is designed to be user-friendly while maintaining data integrity and providing comprehensive reporting capabilities.