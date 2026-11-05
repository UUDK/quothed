# Goal

The goal is to demonstrate how to set up a Flask application for production on
Ubuntu, as it would be done for a publicly accessible server. This is a
learning exercise: the application is deliberately simple, but the deployment
principles should be production-oriented.

The environment is an Ubuntu 24.04 LTS or newer virtual machine running in
VirtualBox. The application hostname is `quothed.example.com`.

- Create a Flask application that displays a randomly selected quote
- Read quotes from a simple text file, with one quote on each line
- Return a new random quote on each request
- Use Gunicorn as the WSGI server for production
- Use nginx as a reverse proxy for the Flask application
- Run the Flask application as a dedicated system user
- Setup Systemd service for the Flask application
- Generate OpenSSL certificates, root CA, and server certificates for HTTPS setup
- Configure nginx to use the generated certificates for secure HTTPS connections

# Important:

- It is not about the application but the deployment journey
- Documentation is king
- The purpose is to understand the principles, not to build a useful quote service
- Repetition between the goal and the tasks is intentional and supports understanding
- The setup targets Ubuntu
- The setup targets Ubuntu 24.04 LTS or newer in a VirtualBox virtual machine
- Use Python 3.12 and include `uv` as the Python environment and package manager
- Use pytest for application tests
- The generated root CA and server certificates are for learning and controlled testing;
  they are not a replacement for certificates issued by a public certificate authority

# Tasks

- Create a quote file with one quote per line
- Create a basic Flask application
- Implement random quote selection from a text file
- Configure Gunicorn to serve the Flask application
- Set up nginx as a reverse proxy for the Flask application
- Create a Systemd service for the Flask application
- Create a script to generate OpenSSL certificates, root CA, and server certificates
- Configure nginx to use the generated certificates for HTTPS
- Test the application and deployment components that are directly related to it
- Write extensive documentation for the entire setup in the README.md file

The documentation and tests should cover the application, Gunicorn, nginx,
Systemd, and HTTPS configuration. General server administration topics such as
firewalls, password policy, RAID, physical access control, and UPS power are
outside the scope of this exercise.

The deployment must be testable in small, incremental steps. Each step should
be verified before moving on to the next one:

- Run and verify the Flask application directly
- Run and verify the application through Gunicorn
- Run and verify the application through the Systemd service as the dedicated system user
- Reach and verify the application through nginx
- Reach and verify the application through HTTPS

The project should primarily be a practical guide. Short helper scripts are
welcome when they remove repetitive setup work, but scripts should remain small
and focused. Do not replace simple two-line instructions with large scripts.

# Development sequence

The deployment is developed and verified in small, incremental steps. Each
step should work before the next one is added:

1. Run and verify the Flask application directly
2. Run and verify the application through Gunicorn
3. Run and verify the application through Systemd as the dedicated system user
4. Reach and verify the application through nginx
5. Reach and verify the application through HTTPS

The README is the deployment guide for the system administrator. The details
of this development sequence belong here in `goal.md`, not in the README.

