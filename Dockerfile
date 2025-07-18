FROM amazonlinux:2

# 1) Install build tools, Python dev headers, GEOS C library
RUN yum update -y \
 && yum install -y \
      python3 \
      python3-devel \
      python3-pip \
      gcc \
      geos \
      geos-devel \
      zip \
 && yum clean all

WORKDIR /lambda

# 2) Upgrade pip and install Python deps into /lambda
COPY requirements.txt .
RUN pip3 install --upgrade pip \
 && pip3 install -r requirements.txt --target .

# 3) Copy your function code
COPY lambda_function.py .
COPY schemas.py .
COPY utils.py .