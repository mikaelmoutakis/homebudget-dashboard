FROM python:3.9-slim

#EXPOSE 8501

#Copies scripts and data directory to container
COPY ./app /app

#Switches to the /app directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential software-properties-common git \
    && rm -rf /var/lib/apt/lists/*

# Installs python modules listed in /app/requirements.txt
RUN pip3 install -r requirements.txt

#creates a non-privileged user for running streamlit
RUN useradd  --shell /bin/bash  streamlit_user

#Sets the owner of the /app/data directory to the streamlit user
RUN chown -R streamlit_user /app/data

#and switches over to it
USER streamlit_user

#Runs the streamlit server 
ENTRYPOINT ["streamlit", "run", "expenses.py", "--server.port=8501", "--server.address=0.0.0.0", "/app/data/config.ini"]