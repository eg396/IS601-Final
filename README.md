# IS 601 M14 - Complete BREAD Functionality for Calculations

This project is for the IS 601 summer semester.

# How to install the program and run the front end

- 1: have postgres and all its dependencies installed on your computer.
- 2: have python 3.12 or later installed on your computer.
- 3: activate a python virtual environment on your computer.
- 4: install all dependencies listed in requirements.txt.
- 5: run the following in your terminal: uvicorn app.main:app --host 127.0.0.1 --port 8000
- 6: enter http://localhost:8000/login on your web browser.
- 7: enjoy!

# How to execute playwright tests

- 1: in your terminal, activate your virtual environment.
- 2: run the following command in your terminal: python3 -m pytest
- Note: there is one test with the 'slow' tag on it. to run that in the test suite, run the following command: python3 -m pytest --run-slow

# Reflection

This assignment was tough - I felt like the BREAD added in a layer of complexity to everything that, while very helpful to the overall process, took some getting used to. I expect this to be a good enough basis to propel me towards a decent score in the final project, at least, even though I lost a significant amount of time this past 2 weeks.

I do feel like I learned a lot about e2e tests though; I haven't had a ton of experience with them so more interaction is always helpful towards a strong understanding of core concepts.

# Links

docker hub: https://hub.docker.com/repository/docker/eg396/is601-m13/general