# Programming vacancies compare

With my tool you can get information 
about quantity of vacancies and average salary 
of top-8 most popular programming languages.
The tool takes information from HeadHunter and SuperJob. 

### How to install

Python3 should be already installed.

1) clone the repo
2) use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
    ```
    pip install -r requirements.txt
    ```
3) add .env file in the directory of the tool:
    ```
    LOGIN_SUPERJOB=<your login from superjob>
    SECRET_KEY_SUPERJOB=<your secret key from superjob>
    PASSWORD_SUPERJOB=<your password from superjob>
    CLIENT_ID_SUPERJOB=<your client id from superjob>
   
    ```
### How to use
1) Write: 
    ```
    python3 main.py 
    ```
2) Use the result

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).