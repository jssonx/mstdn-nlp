FROM apache/spark-py:v3.4.0
USER root
RUN apt-get update && apt-get install -y python3
RUN pip install fastapi uvicorn[standard] pandas pyspark scikit-learn numpy
WORKDIR /app
COPY . /app
EXPOSE 8000
# Run the app using uvicorn
# CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000 && python3 test-api.py"]
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python3", "test-api.py"]

# Test with:
# docker build -t my-fastapi-app .
# docker run -it --rm -p 8000:8000 my-fastapi-app /bin/bash
# python3 test-api.py