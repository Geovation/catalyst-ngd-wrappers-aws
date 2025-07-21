FROM python:3.6
RUN apt-get update && apt-get install -y zip
WORKDIR /lambda

# Install git to clone the repository
RUN apt-get update && apt-get install -y git && apt-get clean

# Add the requiremts
ADD requirements.txt /tmp

RUN python -m venv .venv
# ENV PATH="/lambda/venv/bin:$PATH"
RUN source .venv/bin/activate
RUN python -m pip install --upgrade pip
RUN pip install setuptools --upgrade
RUN pip install -r /tmp/requirements.txt

RUN pip install git+https://github.com/Geovation/catalyst-ngd-wrappers-python.git@0.1.0
RUN pip install --quiet -r /tmp/requirements.txt

# Add your source code
ADD lambda_function.py .
ADD schemas.py .
ADD utils.py .
RUN find -type d | xargs chmod ugo+rx \
    && find -type f | xargs chmod ugo+r

# compile the lot.
RUN python -m compileall -q .

RUN zip --quiet -9r /lambda.zip .

FROM scratch
COPY --from=0 /lambda.zip /