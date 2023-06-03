# PragmaChat
PragmaChat is an application that allows users to create chats, including public chats, private chats and groups with selected users. The application provides an intuitive interface and extensive functions that enable flexible and personalized communication.

Private chat in the PragmaChat application provides a secure and confidential communication environment. Users can create individual chats with selected contacts, so they can have private conversations.

Groups in PragmaChat allow users to create closed communities with selected users. You can invite members to the group and discuss together, organize meetings.

PragmaChat also offers features such as notifications about new messages, personalized user profiles, as well as the ability to search and add new contacts.

PragmaChat is a perfect tool for people who want to have various possibilities to communicate and interact with other users in a flexible and intuitive way.

## Features
### Personalized user profiles
The user can change his data such as email or username, moreover, as part of privacy, he can choose whether he wants his email to be displayed publicly. Changing your profile picture is easy and fun with picture cropping

![profile_edit](https://github.com/dawdom34/PragmaChat/assets/79845962/52165f0d-4e90-4737-a0f5-12e6c598e2a1)

### Searching for users
You have the ability to find your friends by searching for users


![friends_list](https://github.com/dawdom34/PragmaChat/assets/79845962/8c2f99f3-976e-43e9-ba7d-e8bb3a0749e7)

### Private chat
You can have private chats with your friends


![private_chat](https://github.com/dawdom34/PragmaChat/assets/79845962/7e6c762c-2263-49e0-9f9d-02bec5c4b7df)

### Public chat
Public chat is available for all users so you can meet new people


![publicChatjpg](https://github.com/dawdom34/PragmaChat/assets/79845962/35828ac8-b9c7-467a-a844-2f5272fe52aa)

### Group chat
You can create groups with selected users and stay in touch with the people you care about the most


![groupChat](https://github.com/dawdom34/PragmaChat/assets/79845962/35aff825-2ac5-4cae-9740-35c9a32afed0)

### Notifications
The application will inform you about a new message or activity of your friends, thanks to which you will be up to date

![chat_notifications](https://github.com/dawdom34/PragmaChat/assets/79845962/8b1c504b-8647-4c3b-b43f-c4eea424c066)

![general_notifications](https://github.com/dawdom34/PragmaChat/assets/79845962/77deec78-756e-4d99-8856-6e8fab897c77)

![group_notifications](https://github.com/dawdom34/PragmaChat/assets/79845962/9a09e0ff-59a2-474a-ac90-f4209107a601)

## Setup (Windows)

### PostgreSQL setup
This application uses a postgresql database.  This is because Postgres is more feature-rich and has more capabilities than SQLite. As a result, it can handle more data and process it more quickly and reliably.
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
