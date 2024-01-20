# Social Media API

Welcome to the Social Media API! This web application provides a comprehensive platform for creating profiles, follow accounts and publication posts!

# Features

1. **Token Authentication:**
   Secure your API with Token authentication.

2. **Admin Panel:**
   Effortlessly manage various aspects of the system through an intuitive admin panel.

3. **API Documentation:**
   Explore comprehensive API documentation available at `/api/doc/swagger` for clear insights into endpoints and functionality.

4. **Delayed posts:**
   Leverage Celery to implement delayed posts functionality, allowing users to schedule posts for a future date and time.

5. **Social Media Management:**
   Efficiently manage profile, including:

    - **Users**

    - **Creating profiles, posts:**

    - **Managing follows, likes and commentary:**

    - **Delay on post publication**

    - **Watch posts of users you are following**

    - **Watch your own posts**

    - **Filtering Profiles by owner, creating date, bio**

    - **Filtering Posts by title, owner, content, creating date:**

## Getting Started

To set up and run the project locally, follow these steps:

### Create `.env` file

Create a `.env` file in the root of your project and define the necessary variables. You can use `.env.sample` as a template.


1. **Clone the Repository:**
    ```bash
    git clone https://github.com/AnyoneClown/Social-Media-API.git
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Apply Database Migrations:**
    ```bash
    python manage.py migrate
    ```

4. **Start the Development Server:**
    ```bash
    python manage.py runserver
    ```
## Run with Docker

Ensure Docker is installed, and fill in the required environment variables in the `.env` file, use `.env.sample` as template. Once done, run the following commands:

1. **Build the Docker images:**
    ```bash
    docker-compose build
    ```

2. **Start the Docker containers:**
    ```bash
    docker-compose up
    ```

## Getting Access

To interact with the Airport API Service, follow these steps to create a user and obtain an access token:

1. **Create User:**
   Register a new user by making a POST request to `/api/user/register/`
2. **Verify User on your email:**
   Check your email for a verification letter containing a confirmation link. Click on the link to verify your registration.
3. **Get access token:**
   Obtain an authorization token by making a POST request to `/api/user/login/`


## Contributing

I welcome contributions to make this project even better. If you're interested in contributing, here's a step-by-step guide:

1. **Fork the Repository:**
   Click the "Fork" button on the top right of the repository's page to create your own fork.

2. **Create a New Branch:**
   Create a new branch for your feature or bug fix. Be descriptive with your branch name.

3. **Implement Your Changes:**
   Make your changes to the codebase. Ensure your code adheres to the project's coding standards.

4. **Test Thoroughly:**
   Test your changes rigorously to ensure they work as expected.

5. **Submit a Pull Request:**
   When ready, submit a pull request with details about your changes. Provide a clear and concise explanation of the problem and solution.

By following these guidelines, you'll contribute to the success of the Airport Api Service project. Thank you for your contributions!
