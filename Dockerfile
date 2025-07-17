# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install Python and pip
RUN yum update -y && \
    yum install -y python3 python3-pip git && \
    yum clean all

# Create a directory for the Lambda function
WORKDIR /lambda

COPY requirements.txt .

# Install the required Python packages to the target directory
RUN pip3 install -r requirements.txt --target .

COPY local_packages/. .

# Copy all Python files into the container
COPY lambda_function.py .
COPY schemas.py .
COPY utils.py .