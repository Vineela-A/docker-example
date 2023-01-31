# pull official base image
FROM python:3.8-slim-buster

# ENV FLAVORPATH=/Volumes/DriveA/code/MobiTV/mobi-client-connect-ios-swift5/MobiConnect/MobiConnect/Flavors
ENV FLAVORNAME=MobiConnect

WORKDIR /

RUN pip install requests

# Copies everything over to Docker environment
COPY test.py ./
RUN mkdir -p flavors

# start app
# CMD ["python3", "./test.py"]
# CMD ["python3", "test.py", "-f", "/Volumes/DriveA/code/MobiTV/mobi-client-connect-ios-swift5/MobiConnect/MobiConnect/Flavors", "--flav", "MobiConnect"]

# ENTRYPOINT ["python3", "test.py"]

CMD python3 test.py --flav ${FLAVORNAME}