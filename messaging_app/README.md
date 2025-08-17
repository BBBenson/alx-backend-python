# Messaging App API

A Django REST API for messaging functionality with JWT authentication, conversation management, and message filtering capabilities.

## Table of Contents

- [Messaging App API](#messaging-app-api)
  - [Table of Contents](#table-of-contents)
  - [Quick Start with Docker Compose](#quick-start-with-docker-compose)
    - [Prerequisites](#prerequisites)
    - [Data Persistence](#data-persistence)
    - [Setup Instructions](#setup-instructions)
      - [1. Clone the Repository](#1-clone-the-repository)
      - [2. Configure Environment](#2-configure-environment)
      - [3. Build and Start Services](#3-build-and-start-services)
      - [4. Apply Database Migrations](#4-apply-database-migrations)
      - [5. Create Superuser (Admin)](#5-create-superuser-admin)
    - [Docker Commands Cheat Sheet](#docker-commands-cheat-sheet)
    - [Common Issues and Solutions](#common-issues-and-solutions)
    - [Health Check](#health-check)
    - [Stopping and Cleaning Up](#stopping-and-cleaning-up)
  - [Kubernetes Deployment](#kubernetes-deployment)
    - [Prerequisites](#prerequisites-1)
    - [Local Development with Minikube](#local-development-with-minikube)
      - [1. Start Minikube Cluster](#1-start-minikube-cluster)
      - [2. Deploy Database](#2-deploy-database)
      - [3. Deploy Application](#3-deploy-application)
    - [Production Deployment](#production-deployment)
      - [1. Prepare Configuration](#1-prepare-configuration)
      - [2. Deploy to Cluster](#2-deploy-to-cluster)
    - [Setting Up Ingress for External Access](#setting-up-ingress-for-external-access)
      - [1. Install Nginx Ingress Controller](#1-install-nginx-ingress-controller)
      - [2. Configure Ingress Resource](#2-configure-ingress-resource)
      - [3. Apply the Ingress Configuration](#3-apply-the-ingress-configuration)
      - [4. Configure Local DNS (for Development)](#4-configure-local-dns-for-development)
      - [5. Access the Application](#5-access-the-application)
    - [Production Considerations](#production-considerations)
    - [Troubleshooting Ingress](#troubleshooting-ingress)
    - [Scaling and Management](#scaling-and-management)
      - [Using kubectl-0x01 Script](#using-kubectl-0x01-script)
      - [Manual Scaling](#manual-scaling)
    - [Monitoring and Logging](#monitoring-and-logging)
      - [View Logs](#view-logs)
      - [Monitor Resources](#monitor-resources)
    - [Backup and Recovery](#backup-and-recovery)
      - [Database Backups](#database-backups)
      - [Restore from Backup](#restore-from-backup)
    - [Troubleshooting](#troubleshooting)
      - [Common Issues](#common-issues)
    - [Cleanup](#cleanup)
  - [Blue-Green Deployment Strategy](#blue-green-deployment-strategy)
    - [Key Components](#key-components)
    - [How It Works](#how-it-works)
    - [Using the Deployment Controller](#using-the-deployment-controller)
    - [Deployment Files](#deployment-files)
    - [Best Practices](#best-practices)
    - [Troubleshooting Blue-Green Deployments](#troubleshooting-blue-green-deployments)
  - [Rolling Updates with Zero Downtime](#rolling-updates-with-zero-downtime)
    - [Key Features](#key-features)
    - [Deployment Configuration](#deployment-configuration)
    - [Using the Rolling Update Script](#using-the-rolling-update-script)
    - [How It Works](#how-it-works-1)
    - [Monitoring the Update](#monitoring-the-update)
    - [Verifying the Update](#verifying-the-update)
    - [Rollback Process](#rollback-process)
    - [Best Practices](#best-practices-1)
    - [Troubleshooting](#troubleshooting-1)
  - [Project Structure](#project-structure)
  - [API Documentation](#api-documentation)
    - [Authentication](#authentication)
      - [Obtain Token](#obtain-token)
      - [Refresh Token](#refresh-token)
    - [Endpoints](#endpoints)
      - [Users](#users)
      - [Conversations](#conversations)
      - [Messages](#messages)
    - [Filtering and Search](#filtering-and-search)
  - [Testing](#testing)
    - [Running Tests](#running-tests)
    - [Test Data](#test-data)
    - [API Testing with cURL](#api-testing-with-curl)
    - [Using the Rolling Update Script](#using-the-rolling-update-script-1)
    - [How It Works](#how-it-works-2)
    - [Monitoring the Update](#monitoring-the-update-1)
    - [Verifying the Update](#verifying-the-update-1)
    - [Rollback Process](#rollback-process-1)
    - [Best Practices](#best-practices-2)
    - [Troubleshooting](#troubleshooting-2)

## Quick Start with Docker Compose

The fastest way to get the application running is with Docker Compose:

### Prerequisites

- [Docker Engine](https://docs.docker.com/engine/install/) (version 20.10.0 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0.0 or higher)
- At least 2GB of free disk space
- At least 4GB of available RAM

### Data Persistence

The application uses Docker volumes to ensure data persistence across container restarts:

| Volume Name     | Description                                                                 | Location in Container |
|-----------------|-----------------------------------------------------------------------------|-----------------------|
| `mysql_data`    | Stores all MySQL database files                                             | `/var/lib/mysql`      |
| `static_volume` | Contains collected static files (CSS, JavaScript, etc.)                     | `/app/static`         |
| `media_volume`  | Stores user-uploaded files (if any file uploads are implemented)            | `/app/media`          |

To back up these volumes, you can use Docker's built-in volume commands:

```bash
# Create a backup of mysql_data volume
docker run --rm -v mysql_data:/source -v $(pwd):/backup alpine tar czf /backup/mysql_backup_$(date +%Y%m%d).tar.gz -C /source .
```

### Setup Instructions

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd messaging_app
```

#### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the configuration (adjust values as needed)
nano .env
```

Key environment variables to configure:

| Variable           | Description                                  | Example Value          |
|--------------------|----------------------------------------------|------------------------|
| `DB_NAME`          | Database name                                | `messaging_app`        |
| `DB_USER`          | Database user                                | `messaging_user`       |
| `DB_PASSWORD`      | Database password                            | `secure_password123`   |
| `DB_HOST`          | Database host (use `db` for Docker)          | `db`                   |
| `DB_PORT`          | Database port                                | `3306`                 |
| `DJANGO_SECRET_KEY`| Secret key for Django                        | (random 50 characters) |
| `DEBUG`            | Debug mode (set to `False` in production)    | `True`                 |
| `ALLOWED_HOSTS`    | Allowed hostnames (comma-separated)          | `localhost,127.0.0.1`  |

#### 3. Build and Start Services

```bash
# Build and start all services in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f
```

#### 4. Apply Database Migrations

```bash
docker-compose exec web python manage.py migrate
```

#### 5. Create Superuser (Admin)

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Docker Commands Cheat Sheet

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services in detached mode |
| `docker-compose down` | Stop and remove all containers |
| `docker-compose logs -f` | Follow logs from all services |
| `docker-compose exec web bash` | Open shell in web container |
| `docker-compose exec db mysql -u root -p` | Access MySQL shell |
| `docker-compose restart web` | Restart the web service |
| `docker-compose build --no-cache` | Rebuild images without cache |

### Common Issues and Solutions

1. **Port Conflicts**
   - If port 8000 is in use, change it in `docker-compose.yml`
   - Check for existing containers: `docker ps`

2. **Database Connection Issues**
   - Ensure the database container is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`
   - Try restarting the database: `docker-compose restart db`

3. **Permission Issues**
   - If you see permission errors, try:

     ```bash
     sudo chown -R $USER:$USER .
     docker-compose down -v
     docker-compose up -d
     ```

4. **Out of Memory**
   - Increase Docker's memory allocation in Docker Desktop settings
   - Or run: `docker system prune -a` to clean up unused resources

5. **Slow Performance**
   - Exclude the project directory from any antivirus scanning
   - Increase Docker's CPU and memory allocation
   - Use `.dockerignore` to exclude unnecessary files from the build context

### Health Check

Verify the application is running:

```bash
# Check if the web server is responding
curl http://localhost:8000/api/v1/health/

# Check database connection
docker-compose exec web python manage.py check --database default
```

### Stopping and Cleaning Up

```bash
# Stop all containers
docker-compose down

# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all unused containers, networks, and images
docker system prune -a
```

## Kubernetes Deployment

### Prerequisites

- [kubectl](https://kubernetes.io/docs/tasks/tools/) (v1.22+)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) (v1.25+ for local development)
- [Docker](https://docs.docker.com/get-docker/) (v20.10.0+)
- [Helm](https://helm.sh/docs/intro/install/) (v3.8+ for production deployments)
- [envsubst](https://www.gnu.org/software/gettext/manual/html_node/envsubst-Invocation.html) (usually comes with the `gettext` package)

### Local Development with Minikube

#### 1. Start Minikube Cluster

```bash
# Start Minikube with recommended settings
minikube start \
  --cpus=4 \
  --memory=8192mb \
  --disk-size=20g \
  --driver=docker \
  --kubernetes-version=v1.24.0

# Enable required addons
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable ingress

# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Verify cluster status
kubectl cluster-info
kubectl get nodes -o wide
```

#### 2. Deploy Database

```bash
# Create namespace
kubectl create namespace messaging

# Create secrets from .env file
kubectl create secret generic messaging-app-secrets \
  --from-env-file=.env \
  --namespace=messaging

# Apply database configuration
kubectl apply -f k8s/db-deployment.yaml -n messaging

# Verify database pod is running
kubectl get pods -n messaging -l app=postgres

# Check database logs
kubectl logs -n messaging -l app=postgres -f
```

#### 3. Deploy Application

```bash
# Build and tag the Docker image
docker build -t messaging-app:1.0.0 .

# Apply application configuration
kubectl apply -f k8s/deployment.yaml -n messaging

# Monitor deployment status
kubectl get all -n messaging
kubectl get pods -n messaging -w

# View application logs
kubectl logs -n messaging -l app=messaging-app -f

# Access the application
kubectl port-forward svc/messaging-app-service 8000:8000 -n messaging &
```

### Production Deployment

#### 1. Prepare Configuration

1. **Update Secrets**

   ```bash
   # Create or update secrets
   kubectl create secret generic messaging-app-secrets \
     --from-literal=DB_NAME=production_db \
     --from-literal=DB_USER=production_user \
     --from-literal=DB_PASSWORD=$(openssl rand -base64 32) \
     --from-literal=DJANGO_SECRET_KEY=$(openssl rand -base64 50) \
     --namespace=messaging
   ```

2. **Configure Resource Limits**
   Update `k8s/deployment.yaml` with appropriate resource requests and limits:

   ```yaml
   resources:
     requests:
       cpu: "100m"
       memory: "256Mi"
     limits:
       cpu: "500m"
       memory: "1Gi"
   ```

3. **Enable Ingress**

   ```yaml
   # k8s/ingress.yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: messaging-app-ingress
     namespace: messaging
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
   spec:
     rules:
     - host: your-domain.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: messaging-app-service
               port:
                 number: 8000
   ```

#### 2. Deploy to Cluster

```bash
# Apply all configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/db-deployment.yaml
kubectl apply -f k8s/deployment.yaml

# Optional: Set up monitoring with Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

# Verify all components are running
kubectl get all --all-namespaces
```

### Setting Up Ingress for External Access

To expose your Django application to the internet using an Ingress controller, follow these steps:

#### 1. Install Nginx Ingress Controller

```bash
# For Minikube (local development)
minikube addons enable ingress

# For production clusters
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

#### 2. Configure Ingress Resource

Create a file named `ingress.yaml` in the `k8s` directory with the following content:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: messaging-app-ingress
  namespace: messaging
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  rules:
  - host: messaging-app.local
    http:
      paths:
      - path: /api/?(.*)
        pathType: Prefix
        backend:
          service:
            name: messaging-app-service
            port:
              number: 8000
      - path: /admin/?(.*)
        pathType: Prefix
        backend:
          service:
            name: messaging-app-service
            port:
              number: 8000
      - path: /?(.*)
        pathType: Prefix
        backend:
          service:
            name: messaging-app-service
            port:
              number: 8000
```

#### 3. Apply the Ingress Configuration

```bash
# Apply the Ingress configuration
kubectl apply -f k8s/ingress.yaml

# Verify the Ingress is created
kubectl get ingress -n messaging
```

#### 4. Configure Local DNS (for Development)

For local development with Minikube, update your `/etc/hosts` file:

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (Linux/macOS)
echo "$(minikube ip) messaging-app.local" | sudo tee -a /etc/hosts
```

#### 5. Access the Application

After setting up the Ingress, you can access the application at:

- Web interface: <http://messaging-app.local>
- API: <http://messaging-app.local/api/>
- Admin: <http://messaging-app.local/admin/>

### Production Considerations

1. **Custom Domain**: Replace `messaging-app.local` with your production domain.
2. **TLS/HTTPS**: Add TLS certificates using cert-manager or your preferred certificate management solution.
3. **Load Balancer**: In production, your cloud provider will provision a load balancer automatically.
4. **Annotations**: Customize Nginx behavior using [annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/).

### Troubleshooting Ingress

```bash
# Check Ingress status
kubectl describe ingress messaging-app-ingress -n messaging

# View Nginx controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=50

# Check if the Ingress controller is running
kubectl get pods -n ingress-nginx
```

### Scaling and Management

#### Using kubectl-0x01 Script

```bash
# Make script executable
chmod +x kubectl-0x01

# Basic usage (scales to 3 replicas, 30s test)
./kubectl-0x01

# Custom parameters
./kubectl-0x01 <namespace> <deployment> <service> <replicas> <duration> <threads> <connections>

# Example: Scale to 5 replicas with custom load test
./kubectl-0x01 messaging messaging-app messaging-app-service 5 1m 4 100
```

#### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment messaging-app -n messaging --replicas=3

# Check deployment status
kubectl get deployment messaging-app -n messaging
kubectl get pods -n messaging

# View resource usage
kubectl top pods -n messaging

# View Horizontal Pod Autoscaler (if configured)
kubectl get hpa -n messaging
```

### Monitoring and Logging

#### View Logs

```bash
# View application logs
kubectl logs -n messaging -l app=messaging-app -f

# View database logs
kubectl logs -n messaging -l app=postgres -f

# View logs from a specific pod
kubectl logs -n messaging <pod-name> -c <container-name>
```

#### Monitor Resources

```bash
# View cluster metrics
dashboard

# View pod resource usage
kubectl top pods -n messaging

# View node resource usage
kubectl top nodes

# View events
kubectl get events --sort-by='.metadata.creationTimestamp' -n messaging
```

### Backup and Recovery

#### Database Backups

```bash
# Create a backup job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: messaging
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command: ["/bin/sh", "-c"]
            args:
              - >
                PGPASSWORD=\$(PGPASSWORD) pg_dump -h postgres -U \$(PGUSER) \$(PGDATABASE) | gzip > /backup/db_backup_\$(date +%Y%m%d).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: messaging-app-secrets
                  key: DB_PASSWORD
            - name: PGUSER
              valueFrom:
                secretKeyRef:
                  name: messaging-app-secrets
                  key: DB_USER
            - name: PGDATABASE
              valueFrom:
                secretKeyRef:
                  name: messaging-app-secrets
                  key: DB_NAME
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
EOF
```

#### Restore from Backup

```bash
# Copy backup file to pod
kubectl cp db_backup_20230812.sql.gz <postgres-pod>:/tmp/ -n messaging

# Restore database
kubectl exec -n messaging <postgres-pod> -- bash -c \
  "gunzip -c /tmp/db_backup_20230812.sql.gz | psql -U \$POSTGRES_USER -d \$POSTGRES_DB"
```

### Troubleshooting

#### Common Issues

1. **Pods in CrashLoopBackOff**

   ```bash
   # Check pod status
   kubectl describe pod <pod-name> -n messaging
   
   # View container logs
   kubectl logs <pod-name> -n messaging -c <container-name> --previous
   
   # Check events
   kubectl get events --sort-by='.metadata.creationTimestamp' -n messaging
   ```

2. **Service Not Accessible**

   ```bash
   # Check service endpoints
   kubectl get endpoints -n messaging
   
   # Check service details
   kubectl describe svc messaging-app-service -n messaging
   
   # Check network policies
   kubectl get networkpolicies -n messaging
   ```

3. **Persistent Volume Issues**

   ```bash
   # Check PVC status
   kubectl get pvc -n messaging
   
   # Check PV status
   kubectl get pv
   
   # Check storage class
   kubectl get storageclass
   
   # Check events for PVC
   kubectl describe pvc <pvc-name> -n messaging
   ```

4. **Resource Constraints**

   ```bash
   # Check node capacity
   kubectl describe nodes | grep -A 10 "Allocated resources"
   
   # Check pod resource usage
   kubectl top pods -n messaging
   
   # Check node resource usage
   kubectl top nodes
   ```

5. **DNS Resolution Issues**

   ```bash
   # Check CoreDNS pods
   kubectl get pods -n kube-system -l k8s-app=kube-dns
   
   # Test DNS resolution
   kubectl run -it --rm --restart=Never --image=busybox:1.28 dns-test -- nslookup kubernetes.default
   ```

### Cleanup

```bash
# Delete all resources in the messaging namespace
kubectl delete all --all -n messaging

# Delete persistent volume claims
kubectl delete pvc --all -n messaging

# Delete secrets
kubectl delete secret messaging-app-secrets -n messaging

# Delete namespace
kubectl delete namespace messaging

# Stop Minikube cluster
minikube stop

# Delete Minikube cluster
minikube delete
```

## Blue-Green Deployment Strategy

This project implements a blue-green deployment strategy to ensure zero-downtime deployments. The strategy maintains two identical production environments (blue and green) where only one environment is live at any given time.

### Key Components

1. **Blue Deployment** (`blue_deployment.yaml`): The current production version
2. **Green Deployment** (`green_deployment.yaml`): The new version being deployed
3. **Service** (`kubeservice.yaml`): Routes traffic to the active deployment
4. **Deployment Controller** (`kubectl-0x02`): Manages the deployment process

### How It Works

1. **Current State**: Traffic is routed to the blue environment
2. **Deploy New Version**: Deploy the new version to the green environment
3. **Test**: Verify the new version works correctly
4. **Switch Traffic**: Update the service to point to the green environment
5. **Rollback (if needed)**: Switch back to blue if issues are detected

### Using the Deployment Controller

The `kubectl-0x02` script provides a simple interface for managing blue-green deployments:

```bash
# Make the script executable
chmod +x kubectl-0x02

# Show help
./kubectl-0x02 --help

# Deploy a new version (blue or green)
./kubectl-0x02 deploy green

# Verify the deployment
./kubectl-0x02 verify green

# Switch traffic to the new version
./kubectl-0x02 switch green

# Rollback to blue version if needed
./kubectl-0x02 rollback
```

### Deployment Files

1. **Blue Deployment** (`k8s/blue_deployment.yaml`):
   - Deploys the current stable version
   - Labeled with `version: blue`
   - Configured with appropriate resource limits and health checks

2. **Green Deployment** (`k8s/green_deployment.yaml`):
   - Deploys the new version being tested
   - Labeled with `version: green`
   - Identical configuration to blue deployment except for version tags

3. **Service** (`k8s/kubeservice.yaml`):
   - Routes traffic to the active deployment
   - Uses label selectors to determine active version
   - Can be updated to switch between blue and green

### Best Practices

1. **Testing**: Always verify the new deployment before switching traffic
2. **Rollback**: Keep the previous version running until the new version is verified
3. **Monitoring**: Monitor application metrics during and after the switch
4. **Documentation**: Update deployment documentation with each release
5. **Backup**: Ensure database backups are current before deployment

### Troubleshooting Blue-Green Deployments

1. **Deployment Fails**
   - Check pod logs: `kubectl logs -n messaging -l version=green`
   - Verify resource limits and requests
   - Check for configuration errors

2. **Service Not Updating**
   - Verify service selector matches deployment labels
   - Check service endpoints: `kubectl get endpoints -n messaging`

3. **Rollback Issues**
   - Previous version should remain running
   - Verify blue deployment is still healthy before switching back

4. **Performance Issues**
   - Check resource usage: `kubectl top pods -n messaging`
   - Verify database connection pool settings
   - Monitor application metrics

For more information on blue-green deployments, refer to the [Kubernetes documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).

## Rolling Updates with Zero Downtime

This project supports zero-downtime rolling updates using Kubernetes' built-in deployment strategies. The `kubectl-0x03` script automates the update process and verifies application health throughout the deployment.

### Key Features

- **Zero-downtime updates** - Maintains application availability during deployment
- **Health monitoring** - Continuous verification of application health
- **Automatic rollback** - On failure, the deployment automatically rolls back
- **Progress tracking** - Real-time monitoring of the update process

### Deployment Configuration

The rolling update strategy is configured in `blue_deployment.yaml`:

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  minReadySeconds: 5
```

- **maxSurge: 1** - Allows one extra pod during the update
- **maxUnavailable: 0** - Ensures full capacity during updates
- **minReadySeconds: 5** - Gives pods time to warm up before receiving traffic

### Using the Rolling Update Script

The `kubectl-0x03` script automates the update process:

```bash
# Make the script executable
chmod +x kubectl-0x03

# Run the rolling update
./kubectl-0x03
```

### How It Works

1. **Starts Health Checks**
   - Begins continuous health checks against the application
   - Logs all requests for later analysis

2. **Applies Updates**
   - Updates the deployment with the new image version
   - Uses Kubernetes' rolling update strategy
   - Monitors the update progress

3. **Verifies Deployment**
   - Checks that all pods are running the new version
   - Verifies service endpoints are updated
   - Confirms application health

### Monitoring the Update

During the update, the script provides real-time feedback:

- Green checkmarks (✓) for successful health checks
- Red X's (✗) for failed health checks
- Progress updates on the deployment status

### Verifying the Update

After the update completes, verify the deployment:

```bash
# Check deployment status
kubectl get deployments -n messaging

# View pods (should show new version)
kubectl get pods -n messaging -l app=messaging-app

# Check rollout history
kubectl rollout history deployment/messaging-app-blue -n messaging

# View detailed status
kubectl describe deployment messaging-app-blue -n messaging
```

### Rollback Process

If an update fails, Kubernetes automatically rolls back to the previous version. You can also manually rollback:

```bash
# View rollout history
kubectl rollout history deployment/messaging-app-blue -n messaging

# Rollback to previous version
kubectl rollout undo deployment/messaging-app-blue -n messaging

# Rollback to specific revision
kubectl rollout undo deployment/messaging-app-blue -n messaging --to-revision=2
```

### Best Practices

1. **Test Updates in Staging**
   - Always test updates in a staging environment first
   - Verify compatibility with the current database schema

2. **Monitor During Updates**
   - Keep an eye on application metrics
   - Watch for increased error rates or performance issues

3. **Set Resource Limits**
   - Ensure pods have appropriate resource requests and limits
   - Prevents resource starvation during updates

4. **Use Readiness Probes**
   - Configure proper readiness probes
   - Ensures traffic only reaches healthy pods

### Troubleshooting

1. **Update Stalls**

   ```bash
   # Check deployment status
   kubectl describe deployment messaging-app-blue -n messaging
   
   # Check pod events
   kubectl get events -n messaging --sort-by='.metadata.creationTimestamp'
   ```

2. **Health Check Failures**

   ```bash
   # Check pod logs
   kubectl logs -n messaging -l app=messaging-app --tail=50
   
   # Check pod status
   kubectl get pods -n messaging -o wide
   ```

3. **Image Pull Issues**

   ```bash
   # Check pod status
   kubectl describe pod -n messaging -l app=messaging-app
   
   # Check image pull secrets
   kubectl get secrets -n messaging
   ```

For more information on rolling updates, refer to the [Kubernetes documentation](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/).

## Project Structure

```text
messaging_app/
├── api/                   # API endpoints and views
│   ├── __init__.py
│   ├── urls.py           # API URL routing
│   ├── views.py          # View functions
│   ├── serializers.py    # DRF serializers
│   └── permissions.py    # Custom permissions
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── models.py         # Base models
│   └── utils.py          # Utility functions
├── messages/             # Messaging app
│   ├── migrations/       # Database migrations
│   ├── __init__.py
│   ├── admin.py         # Admin interface
│   ├── apps.py          # App config
│   ├── models.py        # Data models
│   ├── serializers.py   # Model serializers
│   ├── services.py      # Business logic
│   ├── signals.py       # Signal handlers
│   ├── tasks.py         # Celery tasks
│   └── views.py         # View classes
├── k8s/                 # Kubernetes configurations
│   ├── deployment.yaml    # Main app deployment
│   ├── db-deployment.yaml # Database configuration
│   ├── secrets.yaml       # Sensitive configuration
│   └── namespace.yaml     # Namespace configuration
├── tests/               # Test files
│   ├── __init__.py
│   ├── conftest.py     # Pytest fixtures
│   ├── test_models.py  # Model tests
│   └── test_views.py   # View tests
├── .dockerignore        # Docker ignore file
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## API Documentation

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. All endpoints except `/api/v1/token/` and `/api/v1/token/refresh/` require authentication.

#### Obtain Token

```http
POST /api/v1/token/
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass123"
}
```

Response:

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token

```http
POST /api/v1/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Endpoints

#### Users

- `GET /api/v1/users/` - List all users (admin only)
- `POST /api/v1/users/` - Register a new user
- `GET /api/v1/users/me/` - Get current user profile
- `PUT /api/v1/users/me/` - Update current user profile
- `PATCH /api/v1/users/me/` - Partially update current user profile

#### Conversations

- `GET /api/v1/conversations/` - List user's conversations
- `POST /api/v1/conversations/` - Create a new conversation
- `GET /api/v1/conversations/{id}/` - Retrieve a conversation
- `PUT /api/v1/conversations/{id}/` - Update a conversation
- `PATCH /api/v1/conversations/{id}/` - Partially update a conversation
- `DELETE /api/v1/conversations/{id}/` - Delete a conversation

#### Messages

- `GET /api/v1/conversations/{conversation_id}/messages/` - List messages in a conversation
- `POST /api/v1/conversations/{conversation_id}/messages/` - Send a message
- `GET /api/v1/conversations/{conversation_id}/messages/{id}/` - Retrieve a message
- `PUT /api/v1/conversations/{conversation_id}/messages/{id}/` - Update a message
- `PATCH /api/v1/conversations/{conversation_id}/messages/{id}/` - Partially update a message
- `DELETE /api/v1/conversations/{conversation_id}/messages/{id}/` - Delete a message

### Filtering and Search

All list endpoints support the following query parameters:

- `search`: Search in all text fields
- `ordering`: Sort results by field (prefix with - for descending)
- `limit`: Number of results to return per page
- `offset`: The initial index from which to return the results

Example:

```text
GET /api/v1/conversations/?search=project&ordering=-created_at&limit=10&offset=20
```

## Testing

### Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run a specific test case
docker-compose exec web python manage.py test messages.tests.test_views

# Run with coverage
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage report
```

### Test Data

Pre-created test users (available after running `create_test_data` command):

1. **Kwame Mensah**
   - Username: `kwame`
   - Password: `testpass123`
   - Email: `kwame@example.com`

2. **Ama Aidoo**
   - Username: `ama`
   - Password: `testpass123`
   - Email: `ama@example.com`
   - Has a conversation with Kwame

3. **Kofi Asare**
   - Username: `kofi`
   - Password: `testpass123`
   - Email: `kofi@example.com`

### API Testing with cURL

```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"kwame","password":"testpass123"}' | jq -r '.access')

# List conversations
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/conversations/

# Send a message
curl -X POST http://localhost:8000/api/v1/conversations/1/messages/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, this is a test message!"}'

```

Follow these instructions to make the following change to my code document.

Instruction: Add a new section for Rolling Updates after the Blue-Green Deployment Strategy section

Code Edit:

```
{{ ... }}
## Rolling Updates with Zero Downtime

This project supports zero-downtime rolling updates using Kubernetes' built-in deployment strategies. The `kubectl-0x03` script automates the update process and verifies application health throughout the deployment.

### Key Features

- **Zero-downtime updates** - Maintains application availability during deployment
- **Health monitoring** - Continuous verification of application health
- **Automatic rollback** - On failure, the deployment automatically rolls back
- **Progress tracking** - Real-time monitoring of the update process

### Deployment Configuration

The rolling update strategy is configured in `blue_deployment.yaml`:

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  minReadySeconds: 5
```

- **maxSurge: 1** - Allows one extra pod during the update
- **maxUnavailable: 0** - Ensures full capacity during updates
- **minReadySeconds: 5** - Gives pods time to warm up before receiving traffic

### Using the Rolling Update Script

The `kubectl-0x03` script automates the update process:

```bash
# Make the script executable
chmod +x kubectl-0x03

# Run the rolling update
./kubectl-0x03
```

### How It Works

1. **Starts Health Checks**
   - Begins continuous health checks against the application
   - Logs all requests for later analysis

2. **Applies Updates**
   - Updates the deployment with the new image version
   - Uses Kubernetes' rolling update strategy
   - Monitors the update progress

3. **Verifies Deployment**
   - Checks that all pods are running the new version
   - Verifies service endpoints are updated
   - Confirms application health

### Monitoring the Update

During the update, the script provides real-time feedback:

- Green checkmarks (✓) for successful health checks
- Red X's (✗) for failed health checks
- Progress updates on the deployment status

### Verifying the Update

After the update completes, verify the deployment:

```bash
# Check deployment status
kubectl get deployments -n messaging

# View pods (should show new version)
kubectl get pods -n messaging -l app=messaging-app

# Check rollout history
kubectl rollout history deployment/messaging-app-blue -n messaging

# View detailed status
kubectl describe deployment messaging-app-blue -n messaging
```

### Rollback Process

If an update fails, Kubernetes automatically rolls back to the previous version. You can also manually rollback:

```bash
# View rollout history
kubectl rollout history deployment/messaging-app-blue -n messaging

# Rollback to previous version
kubectl rollout undo deployment/messaging-app-blue -n messaging

# Rollback to specific revision
kubectl rollout undo deployment/messaging-app-blue -n messaging --to-revision=2
```

### Best Practices

1. **Test Updates in Staging**
   - Always test updates in a staging environment first
   - Verify compatibility with the current database schema

2. **Monitor During Updates**
   - Keep an eye on application metrics
   - Watch for increased error rates or performance issues

3. **Set Resource Limits**
   - Ensure pods have appropriate resource requests and limits
   - Prevents resource starvation during updates

4. **Use Readiness Probes**
   - Configure proper readiness probes
   - Ensures traffic only reaches healthy pods

### Troubleshooting

1. **Update Stalls**

   ```bash
   # Check deployment status
   kubectl describe deployment messaging-app-blue -n messaging
   
   # Check pod events
   kubectl get events -n messaging --sort-by='.metadata.creationTimestamp'
   ```

2. **Health Check Failures**

   ```bash
   # Check pod logs
   kubectl logs -n messaging -l app=messaging-app --tail=50
   
   # Check pod status
   kubectl get pods -n messaging -o wide
   ```

3. **Image Pull Issues**

   ```bash
   # Check pod status
   kubectl describe pod -n messaging -l app=messaging-app
   
   # Check image pull secrets
   kubectl get secrets -n messaging
   ```

For more information on rolling updates, refer to the [Kubernetes documentation](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/).

