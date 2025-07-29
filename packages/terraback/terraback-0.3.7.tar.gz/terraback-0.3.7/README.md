# 🚀 Terraback

**Multi-Cloud Infrastructure as Code Tool**

Terraback is an advanced CLI tool that reverse-engineers existing cloud infrastructure into clean, production-ready Terraform code with intelligent dependency discovery.

**Transform legacy cloud environments into infrastructure-as-code in minutes, not months.**

---

## ✨ Why Terraback?

- **🎯 90% Faster**: Reduce infrastructure documentation time from weeks to hours  
- **🧠 Intelligent Discovery**: Automatic dependency mapping across 50+ cloud services  
- **🏢 Enterprise-Ready**: Production-ready templates with lifecycle management  
- **☁️ Multi-Cloud**: Full support for AWS and Azure, with GCP coming soon  
- **🔒 Security-First**: Read-only permissions, no credential storage, enterprise compliance

---

## 🌟 Features

### 📊 Comprehensive Cloud Coverage

**Core Infrastructure (Community Edition - Free):**

- **AWS**: EC2 Instances, VPCs, Subnets, Security Groups, S3 Buckets, IAM Roles
- **Azure**: Virtual Machines, Virtual Networks, Subnets, Network Security Groups, Storage Accounts
- **GCP**: Compute Instances, Networks, Subnets, Storage Buckets
- **Basic Commands**: list, import, scan
- **✨ Unlimited core resources**
- **Basic dependency mapping**

**Advanced Services (Migration Pass & Enterprise):**

**AWS Services:**
- **Container Platform**: ECS Clusters, Services, Task Definitions, ECR Repositories
- **Advanced Networking**: CloudFront CDN, Route 53 DNS, NAT/Internet Gateways, VPC Endpoints
- **Database & Caching**: RDS instances, ElastiCache Redis/Memcached clusters
- **Monitoring & Security**: CloudWatch, Auto Scaling, ACM Certificates
- **Serverless & APIs**: Lambda Functions, API Gateway, SQS, SNS
- **Storage**: EFS, EBS Volumes/Snapshots, S3 advanced features
- **Load Balancing**: ALB/NLB with advanced features, listener rules, SSL policies

**Azure Services:**
- **Compute**: Virtual Machines with OS detection, Managed Disks, SSH Keys
- **Networking**: Virtual Networks, Subnets with delegations, NSGs with rules
- **Storage**: Storage Accounts with blob properties, static websites, encryption
- **Load Balancing**: Application Gateway, Load Balancers
- **Database**: Azure SQL, Cosmos DB
- **Container**: AKS, Container Instances

**GCP Services:**
- **Compute**: VM Instances, Persistent Disks, Machine Images
- **Networking**: VPC Networks, Subnets, Firewall Rules
- **Storage**: Cloud Storage, Persistent Disks
- **Container**: GKE Clusters, Node Pools

### 🔗 Intelligent Dependency Discovery

The `--with-deps` flag automatically discovers and maps complete infrastructure stacks:

```bash
# AWS Example
terraback ec2 scan --with-deps
# Automatically finds and scans:
# ├── VPC and networking (subnets, security groups)
# ├── Load balancers (ALB, target groups, listeners)
# ├── Storage (EBS volumes, snapshots)
# ├── Security (IAM roles, certificates)
# ├── Monitoring (CloudWatch logs, alarms)
# └── All interconnected dependencies

# Azure Example
terraback vm scan --with-deps
# Automatically finds and scans:
# ├── Virtual Networks and Subnets
# ├── Network Security Groups with rules
# ├── Managed Disks and Snapshots
# ├── Network Interfaces and Public IPs
# ├── Storage Accounts
# └── All interconnected dependencies
```

### 🚀 Advanced Features

- **Performance Optimization**: API response caching, parallel scanning, smart dependency resolution
- **Multi-Account/Subscription**: Scan across multiple AWS accounts or Azure subscriptions
- **Module Generation**: Create reusable Terraform modules automatically
- **State Management**: Import existing resources directly into Terraform state
- **Compliance Ready**: Generate code following HashiCorp and cloud provider best practices

---

## 📦 Installation

### Prerequisites
- Python 3.8+ (for pip installation)
- Terraform 1.0+ (for import functionality)
- Cloud CLI tools:
  - AWS: `aws` CLI configured
  - Azure: `az` CLI configured and logged in
  - GCP: `gcloud` CLI configured

### Install via pip (Recommended)

```bash
pip install terraback
```

### Install via Binary

**Linux/macOS:**
```bash
# Linux
curl -L https://dist.terraback.dev.io/releases/latest/terraback-linux -o terraback
chmod +x terraback
sudo mv terraback /usr/local/bin/

# macOS
curl -L https://dist.terraback.dev.io/releases/latest/terraback-macos -o terraback
chmod +x terraback
sudo mv terraback /usr/local/bin/
```

**Windows:**
Download from [releases](https://dist.terraback.dev.io/releases/latest/terraback-windows.exe)

---

## 🚀 Quick Start

### AWS Scanning

```bash
# Configure AWS credentials (if not already done)
aws configure

# Scan EC2 instances
terraback ec2 scan

# Scan VPC with all dependencies
terraback vpc scan --with-deps

# Scan specific region
terraback ec2 scan --region eu-west-1

# Scan with specific profile
terraback s3 scan --profile production
```

### Azure Scanning

```bash
# Login to Azure (if not already done)
az login

# Scan Virtual Machines
terraback vm scan

# Scan entire resource group
terraback vm scan --resource-group production-rg

# Scan specific subscription
terraback vnet scan --subscription-id YOUR-SUBSCRIPTION-ID

# Scan with location filter
terraback storage scan --location westeurope
```

### Multi-Cloud Commands

```bash
# Scan all resources (cloud-specific)
terraback scan-all aws --region us-east-1
terraback scan-all azure --resource-group my-rg

# Check authentication status
terraback auth-check

# Use caching for large infrastructures
terraback scan-recursive ec2 --use-cache --cache-ttl 120
terraback scan-recursive vm --use-cache --parallel-workers 10
```

---

## 📋 Supported Resources

### AWS Resources (Full Support)

| Service | Resources | Status |
|---------|-----------|---------|
| **EC2** | Instances, Volumes, Snapshots, AMIs, Key Pairs, Launch Templates, Network Interfaces | ✅ Full Support |
| **VPC** | VPCs, Subnets, Security Groups, Internet/NAT Gateways, Route Tables, VPC Endpoints | ✅ Full Support |
| **IAM** | Roles, Policies, Instance Profiles | ✅ Full Support |
| **S3** | Buckets, Versioning, Lifecycle, ACLs, Policies | ✅ Full Support |
| **RDS** | Instances, Subnet Groups, Parameter Groups | ✅ Full Support |
| **Load Balancing** | ALB, NLB, CLB, Target Groups, Listeners, SSL Policies | ✅ Full Support |
| **Lambda** | Functions, Layers, Permissions | ✅ Full Support |
| **Route 53** | Hosted Zones, Records | ✅ Full Support |
| **CloudWatch** | Log Groups, Alarms, Dashboards | ✅ Full Support |
| **Auto Scaling** | Groups, Launch Templates, Policies | ✅ Full Support |
| **ECS/ECR** | Clusters, Services, Task Definitions, Repositories | ✅ Full Support |
| **CloudFront** | Distributions, Origin Access Controls, Cache Policies | ✅ Full Support |
| **ElastiCache** | Redis/Memcached Clusters, Parameter Groups | ✅ Full Support |
| **ACM** | Certificates | ✅ Full Support |
| **EFS** | File Systems, Mount Targets, Access Points | ✅ Full Support |
| **API Gateway** | REST APIs, Resources, Methods, Deployments | ✅ Full Support |
| **SQS/SNS** | Queues, Topics, Subscriptions | ✅ Full Support |
| **Secrets Manager** | Secrets, Versions | ✅ Full Support |
| **Systems Manager** | Parameters, Documents | ✅ Full Support |

### Azure Resources

| Service | Resources | Status |
|---------|-----------|---------|
| **Compute** | Virtual Machines, Managed Disks, Availability Sets, SSH Keys | ✅ Full Support |
| **Networking** | Virtual Networks, Subnets, Network Security Groups, Network Interfaces | ✅ Full Support |
| **Storage** | Storage Accounts, Blob Storage, File Shares | ✅ Full Support |
| **Load Balancing** | Load Balancers, Application Gateways | ✅ Full Support |
| **Database** | SQL Database, Cosmos DB | ✅ Full Support |
| **Container** | AKS, Container Instances | ✅ Full Support |
| **Identity** | Managed Identities, Service Principals | ✅ Full Support |

### GCP Resources

| Service | Resources | Status |
|---------|-----------|---------|
| **Compute Engine** | Instances, Disks, Images | ✅ Full Support |
| **VPC** | Networks, Subnets, Firewalls | ✅ Full Support |
| **Cloud Storage** | Buckets, Objects | ✅ Full Support |
| **GKE** | Clusters, Node Pools | ✅ Full Support |

---

## 🎯 Advanced Usage

### Dependency Scanning

```bash
# AWS: Scan EC2 with all dependencies
terraback ec2 scan --with-deps --output-dir ./infrastructure

# Azure: Scan VM with all dependencies  
terraback vm scan --with-deps --output-dir ./infrastructure

# Result: Complete infrastructure graph
# ├── compute/
# │   ├── instances.tf
# │   └── launch_templates.tf
# ├── networking/
# │   ├── vpc.tf
# │   ├── subnets.tf
# │   └── security_groups.tf
# └── storage/
#     ├── volumes.tf
#     └── snapshots.tf
```

### Caching & Performance

```bash
# Enable caching for large infrastructures
terraback scan-recursive ec2 --use-cache --cache-ttl 60

# View cache statistics
terraback cache stats

# Clear cache
terraback cache clear

# Parallel scanning
terraback scan-recursive vm --parallel-workers 10
```

### Import to Terraform

```bash
# List discovered resources
terraback list all

# Import specific resource
terraback ec2 import i-1234567890abcdef0

# Import Azure VM
terraback vm import /subscriptions/xxx/resourceGroups/my-rg/providers/Microsoft.Compute/virtualMachines/my-vm
```

---

## ⚖️ License & Pricing

Terraback uses a multi-tier licensing model:

### Community Edition (Free)
- ✅ **Core resources for AWS, Azure, GCP**
- ✅ EC2, VPC, S3 (AWS)
- ✅ VMs, VNets, Storage (Azure)  
- ✅ Compute, Networks, Storage (GCP)
- ✅ **✨ Unlimited core resources**
- ✅ Basic dependency mapping
- ✅ Community support via GitHub
- ❌ Advanced services (RDS, Lambda, etc.)
- ❌ Multi-account support

### Migration Pass ($299 per user/business for 3 months)
- ✅ **All 50+ cloud services**
- ✅ Unlimited resources & accounts
- ✅ Advanced dependency mapping
- ✅ Multi-account/subscription scanning
- ✅ RDS, Lambda, EKS, and more
- ✅ Module generation & best practices
- ✅ State file management
- ✅ Priority email support
- ✅ Migration planning assistance
- ✅ API access for automation

### Enterprise Edition (Coming Soon)
- ✅ **Everything in Migration Pass**
- ✅ Annual/multi-year licensing
- ✅ SSO integration (SAML, OIDC)
- ✅ Custom resource scanners
- ✅ On-premise deployment options
- ✅ SLA with guaranteed uptime
- ✅ Dedicated training & onboarding
- ✅ Dedicated customer success manager
- ✅ Volume licensing & team management
- ✅ Compliance reporting

---

## 📚 Documentation

- [Full Documentation](https://docs.terraback.io)
- [AWS Scanning Guide](https://docs.terraback.io/aws)
- [Azure Scanning Guide](https://docs.terraback.io/azure)
- [GCP Scanning Guide](https://docs.terraback.io/gcp)
- [API Reference](https://docs.terraback.io/api)
- [Examples & Tutorials](https://docs.terraback.io/examples)

---

## 🐛 Troubleshooting

### AWS Issues

```bash
# Check AWS credentials
aws sts get-caller-identity

# Use specific profile
export AWS_PROFILE=production

# Debug mode
terraback ec2 scan --debug
```

### Azure Issues

```bash
# Check Azure login
az account show

# Set subscription
az account set --subscription "My Subscription"

# List available subscriptions
az account list --output table
```

### Common Issues

1. **Permission Denied**: Ensure your cloud credentials have read access to resources
2. **Rate Limiting**: Use `--use-cache` flag for large infrastructures
3. **Module Not Found**: Install with `pip install -e .` for development

---

## 🚀 Roadmap

- [x] AWS support (50+ services)
- [x] Azure support (Core services)
- [x] GCP support (Core services)
- [ ] Terraform module generation
- [ ] Web UI dashboard
- [ ] CI/CD integrations

---

## 📞 Support

- **Community**: [GitHub Discussions](https://github.com/terraback/terraback/discussions)
- **Issues & Feature Requests**: [GitHub Issues](https://github.com/terraback/terraback/issues)
- **Professional Support**: support@terraback.io
- **Enterprise Sales**: sales@terraback.io

---

## 🙏 Acknowledgments

Built with ❤️ by DevOps engineers who understand the pain of manual cloud documentation.

---

**Copyright © 2025 Terraback**