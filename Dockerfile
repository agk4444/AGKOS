# AGK Language Compiler Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy all AGK compiler files
COPY . .

# Make the compiler executable
RUN chmod +x agk_compiler.py

# Create a volume for mounting source files
VOLUME ["/app/workspace"]

# Set the default command to show help
CMD ["python", "agk_compiler.py", "--help"]

# Labels for better maintainability
LABEL maintainer="AGK Language Compiler Team"
LABEL version="1.0"
LABEL description="A natural language programming compiler that combines the best features of C++, Java, and Python"

# Optional: Create a non-root user for security
RUN useradd -m -u 1000 agk_user
USER agk_user