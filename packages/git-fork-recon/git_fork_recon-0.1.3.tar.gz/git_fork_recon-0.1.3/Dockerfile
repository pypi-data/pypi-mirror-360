FROM python:3.9-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Accept build arguments for user/group IDs
ARG USER_ID=1000
ARG GROUP_ID=1000

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    pandoc \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user with the provided IDs
RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -u ${USER_ID} -g appuser -m appuser

WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Install our package in development mode
RUN pip install -e .

# Switch to non-root user
USER appuser

# Run as a module to make relative imports work
ENTRYPOINT ["python", "-m", "git_fork_recon.main"] 