# Task Management System

## Overview

This is a comprehensive task management web application designed to demonstrate modern full-stack development practices. The application enables users to create, view, edit, and delete tasks, assign them to specific users, and receive real-time updates on task status changes.

The project showcases practical implementation of contemporary web technologies and development tools, including Flask, React, SQLite/PostgreSQL, Docker, and WebSockets.

## Key Features

*   **User Management**: Registration, authentication, and profile management
*   **Task Management**: Create, read, update, and delete tasks with various statuses and priorities
*   **Task Assignment**: Assign tasks to specific users with role-based permissions
*   **Real-time Updates**: Instant notifications for task changes using WebSockets
*   **Authentication & Authorization**: Secure JWT-based authentication system
*   **API Documentation**: Interactive Swagger/OpenAPI documentation
*   **Responsive Design**: Mobile-friendly interface built with modern UI components

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Real-time Communication**: Socket.IO
- **API Documentation**: Swagger/OpenAPI
- **Testing**: pytest, pytest-flask
- **Production Server**: Gunicorn with Eventlet workers

### Frontend
- **Framework**: React 18
- **Language**: JavaScript (JSX)
- **Routing**: React Router
- **UI Components**: Tailwind CSS + shadcn/ui
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Real-time Client**: Socket.IO Client
- **Build Tool**: Vite

### DevOps & Deployment
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (production)
- **Process Management**: Gunicorn
- **Environment Management**: dotenv
- **Deployment Scripts**: Bash scripts for automated deployment

## Project Structure

```
task-management-system/
├── backend/                 # Flask API application
│   ├── src/
│   │   ├── models/          # Database models (User, Task)
│   │   ├── routes/          # API endpoints and business logic
│   │   ├── middleware/      # Authentication and validation
│   │   └── main.py          # Application entry point
│   ├── tests/               # Backend test suite
│   ├── Dockerfile           # Backend container configuration
│   └── requirements.txt     # Python dependencies
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── pages/           # Application pages/views
│   │   ├── contexts/        # React context providers
│   │   ├── services/        # API communication layer
│   │   └── hooks/           # Custom React hooks
│   ├── Dockerfile           # Frontend container configuration
│   └── package.json         # Node.js dependencies
├── scripts/                 # Deployment and utility scripts
├── docker-compose.yml       # Multi-container orchestration
├── .env.example             # Environment variables template
└── README.md                # Project documentation
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd task-management-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Deploy with Docker Compose**
   ```bash
   ./scripts/deploy.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api
   - API Documentation: http://localhost:5000/api/docs

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

#### Frontend Setup
```bash
cd frontend
npm install  # or pnpm install
npm run dev  # or pnpm run dev
```

## API Documentation

The API is fully documented using OpenAPI/Swagger specification. Once the application is running, you can access the interactive documentation at:

- **Swagger UI**: http://localhost:5000/api/docs
- **OpenAPI Spec**: http://localhost:5000/api/swagger.yaml

### Key API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Get current user info
- `GET /api/tasks` - List tasks with filtering options
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update existing task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/tasks/stats` - Get task statistics

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=src
```

### Frontend Tests
```bash
cd frontend
npm test  # or pnpm test
```

## Deployment Options

### Docker Compose (Local/Development)
```bash
./scripts/deploy.sh
```

### Production Deployment
The application is containerized and can be deployed to any Docker-compatible platform:

- **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Instances
- **Container Orchestration**: Kubernetes, Docker Swarm
- **PaaS Platforms**: Heroku, Railway, Render

### Environment Configuration

Key environment variables for production:

```env
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/dbname
CORS_ORIGINS=https://yourdomain.com
```

## Features in Detail

### Authentication System
- JWT-based stateless authentication
- Secure password hashing with bcrypt
- Token refresh mechanism
- Protected routes and API endpoints

### Task Management
- CRUD operations for tasks
- Task status tracking (Pending, In Progress, Completed, Cancelled)
- Priority levels (Low, Medium, High, Urgent)
- Due date management
- Task assignment to users

### Real-time Features
- WebSocket connections using Socket.IO
- Live task updates and notifications
- Real-time status changes
- User-specific notification rooms

### Security Features
- CORS configuration
- SQL injection prevention with ORM
- XSS protection headers
- Secure session management
- Input validation and sanitization

## Development Guidelines

### Code Style
- Backend: PEP 8 for Python code
- Frontend: ESLint and Prettier for JavaScript/React
- Consistent naming conventions
- Comprehensive error handling

### Git Workflow
- Feature branch workflow
- Descriptive commit messages
- Pull request reviews
- Automated testing on CI/CD

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 5000 are available
2. **Docker issues**: Restart Docker service and try again
3. **Database connection**: Check database configuration in .env
4. **CORS errors**: Verify CORS_ORIGINS setting matches your frontend URL

### Logs and Debugging
```bash
# View application logs
./scripts/deploy.sh logs

# Check container status
./scripts/deploy.sh status

# Restart services
./scripts/deploy.sh restart
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/api/docs`
- Review the troubleshooting section above

---

chmod +x scripts/deploy.sh
./scripts/deploy.sh deploy    # full deploy
./scripts/deploy.sh stop      # stop containers
./scripts/deploy.sh restart   # restart
./scripts/deploy.sh logs      # logs view
./scripts/deploy.sh status    # containers status
./scripts/deploy.sh backup    # backup
./scripts/deploy.sh cleanup   # delete useless data

**Note**: This is a demonstration project showcasing modern full-stack development practices and can serve as a foundation for building production-ready task management applications. This project was created as a portfolio piece to demonstrate comprehensive full-stack development skills including backend API development, frontend React applications, real-time features, testing, containerization, and deployment practices.

