# 🚀 Startup Guide: E-Learning Platform

Follow these steps to get the enterprise-grade multi-page E-Learning platform up and running on your local machine.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **.NET 8.0 SDK**: [Download here](https://dotnet.microsoft.com/download/dotnet/8.0)
2.  **MySQL Server 8.0**: [Download here](https://dev.mysql.com/downloads/installer/) (Ensure it's running)
3.  **Node.js**: [Download here](https://nodejs.org/) (Required only for running frontend tests)

---

## 🛠️ Step-by-Step Installation

### 1. Database Configuration

> [!IMPORTANT]
> The application uses MySQL. You must ensure the connection string matches your local database credentials.

1.  Open the file: `Backend/ELearningAPI/appsettings.json`
2.  Locate the `"ConnectionStrings"` section.
3.  Update the `Password` (and `User` or `Port` if necessary) to match your MySQL setup:
    ```json
    "ConnectionStrings": {
      "DefaultConnection": "Server=localhost;Port=3306;Database=ELearningDB;User=root;Password=YOUR_PASSWORD_HERE;"
    }
    ```

### 2. Initialize the Database

Open your terminal (PowerShell or Command Prompt) and run the following commands to create the database schema:

```powershell
# Navigate to the API directory
cd Backend/ELearningAPI

# Apply Entity Framework Migrations
dotnet ef database update
```

### 3. Launch the Application

Static files (Frontend) are automatically served by the backend. To start the entire system:

```powershell
# Ensure you are in Backend/ELearningAPI
dotnet run
```

---

## 🌐 Accessing the Platform

Once the application is running, you can access it via the following URLs:

| View | URL |
| :--- | :--- |
| **User Interface (Frontend)** | [http://localhost:5208/index.html](http://localhost:5208/index.html) |
| **API Documentation (Swagger)** | [http://localhost:5208/swagger](http://localhost:5208/swagger) |
| **API Base URL** | `http://localhost:5208/api` |

---

## 🧪 Running Tests

### Frontend Logic Tests
The frontend uses Jest to verify logic (asynchronous calls, data processing).
```powershell
# Run from the project root directory
npm install
npm test
```

### Backend API Tests
```powershell
# Run from the project root directory
dotnet test
```

---

## ⚠️ Troubleshooting

> [!WARNING]
> If the application fails to start, check the following:

- **MySQL Connection**: Ensure the MySQL service is running and the credentials in `appsettings.json` are correct.
- **Port Conflict**: If port `5208` is already in use, you can change the port in `Backend/ELearningAPI/Properties/launchSettings.json`.
- **SDK Version**: Verify you are using .NET 8 by running `dotnet --version`.

---
*Created by Antigravity - Advanced Agentic Coding Assistant*
