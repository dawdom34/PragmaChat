# PragmaChat
PragmaChat is an application that allows users to create chats, including public chats, private chats and groups with selected users. The application provides an intuitive interface and extensive functions that enable flexible and personalized communication.

Private chat in the PragmaChat application provides a secure and confidential communication environment. Users can create individual chats with selected contacts, so they can have private conversations.

Groups in PragmaChat allow users to create closed communities with selected users. You can invite members to the group and discuss together, organize meetings.

PragmaChat also offers features such as notifications about new messages, personalized user profiles, as well as the ability to search and add new contacts.

PragmaChat is a perfect tool for people who want to have various possibilities to communicate and interact with other users in a flexible and intuitive way.

DEMO: https://www.pragmachatdemo.online

## Features
### Personalized user profiles
The user can change his data such as email or username, moreover, as part of privacy, he can choose whether he wants his email to be displayed publicly. Changing your profile picture is easy and fun with picture cropping

![profile_edit](https://github.com/dawdom34/PragmaChat/assets/79845962/14af1e73-ce24-483e-828e-665e1b2622f9)


### Searching for users
You have the ability to find your friends by searching for users


![friends_list](https://github.com/dawdom34/PragmaChat/assets/79845962/71d88c76-c22e-4609-a770-56a93282dfe2)


### Private chat
You can have private chats with your friends


![private_chat](https://github.com/dawdom34/PragmaChat/assets/79845962/e5688a48-54ca-4e54-b0ce-c33c2f70a408)


### Public chat
Public chat is available for all users so you can meet new people


![publicChatjpg](https://github.com/dawdom34/PragmaChat/assets/79845962/4567cfa8-d036-4841-a0d7-a36164510f22)


### Group chat
You can create groups with selected users and stay in touch with the people you care about the most


![groupChat](https://github.com/dawdom34/PragmaChat/assets/79845962/1eb951a2-7547-4cbb-a495-140830af747c)


### Notifications
The application will inform you about a new message or activity of your friends, thanks to which you will be up to date

![chat_notifications](https://github.com/dawdom34/PragmaChat/assets/79845962/f3179c49-1c28-44fa-9860-326942dcb0a4)

![general_notifications](https://github.com/dawdom34/PragmaChat/assets/79845962/2284e3c6-7697-4f75-ade8-76de8d710709)

![group_notifications](https://github.com/dawdom34/PragmaChat/assets/79845962/202bb16d-ccba-43b5-a50a-44059038b28f)

## Setup (Windows)

### PostgreSQL setup
This application uses a postgresql database. This is because Postgres is more feature-rich and has more capabilities than SQLite. As a result, it can handle more data and process it more quickly and reliably.
1. Download postgres https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Run .exe file and run through installation. (**Remember superuser password, this is very important!**)
3. After installation confirm the service is running by opening the "Services" window on windows. (If it's not then run it)
4. Confirm that postgres is installed correctly.
  - Write `psql postgres postgres` (connect to the database named 'postgres' with the user 'postgres')
5. Now create new database.
  - Open psql command-line tool and execute command: `CREATE DATABASE database_name;` (You can replace databsae_name with any name)
6. Create a new user and give him all permissions to the database
  - Create user by execute this command: `CREATE USER django WITH PASSWORD 'password';` (You can replace 'django' and 'password' with your own data **but it is very important that you remember this data because we will    use it to later configure the django connection to the database**)
  - Now grant all permissions to the previously created database to the new user: `GRANT ALL PRIVILEGES ON DATABASE database_name TO django;` (remember to change the username and database name to those you provided when creating them)

### Redis setup
Redis is not officially supported on Windows. However, you can install Redis on Windows for development by following the instructions below.
Memurai is a Redis 5 compatible cache and data store for Windows. 
Memurai runs natively on Windows and it's designed to provide the reliability and performance demanded by enterprise Windows environments. 
1. Download Memurai: https://www.memurai.com/get-memurai
2. Run instalation file and follow the instructions.
3. After installation confirm the service is running by opening the "Services" window on windows. (If it's not then run it)

### Virtual enviroment setup
Different projects are based on other packages or their versions. Django provides us with virtual environments that allow us to isolate individual projects and their packages from each other
1. Open CMD and navigate to **Desktop**
2. Create virtual enviroment: `virtualenv venv_name --python=python3.8.5` (You can replace 'venv_name' with your own name)
3. Change directory to venv_name `cd venv_name` and activate virtual enviroment `Scripts\activate`.

### Project setup
1. Make sure you are in 'venv_name' directory and virtual enviroment is active.
2. Download app: `git clone https://github.com/dawdom34/PragmaChat.git`.
3. Change directory to `PragmaChat`
4. Now install all required packages `pip install -r requirements.txt`.
5. Now it's time to configure the connection to the database created earlier, go to `PragmaChat/settings.py` and find the DATABASES section.
6. Fill the variables with the values of the previously created user.

![db](https://github.com/dawdom34/PragmaChat/assets/79845962/d04346fa-734a-4f3c-9921-a1ea48c98d8b)

7. Save the file.
8. Create migrations and apply them: `python manage.py makemigrations`, `python manage.py migrate`.
9. Create superuser: `python manage.py createsuperuser`.
10. Run the server: `python manage.py runserver`
11. Once the server is hosted, head over to http://127.0.0.1:8000/

