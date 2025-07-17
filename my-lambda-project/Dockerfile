# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install Python and pip
RUN yum update -y && \
    yum install -y python3 python3-pip && \
    yum clean all

# Create a directory for the Lambda function
WORKDIR /lambda

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages to the target directory
RUN pip3 install -r requirements.txt --target .

# Copy your Lambda function code into the container
COPY schemas.py .
COPY utils.py .
COPY lambda_function.py .