## The asynchronous telegram bot updates information from the Wikipedia API at the request of the administrator and returns the population of the city of the Moscow region and a link to its description on Wikipedia.

### Description

Designed to get the population size
cities of the Moscow region by its name. If you enter part of the name of the city,
then suitable options will come in response (if only one city is suitable, or if the name of the city is entered in its entirety,
then its number and a link to the Wiki).

### Technologies

aiohttp==3.8.1
aiosignal==1.2.0
async-timeout==4.0.2
asynctest==0.13.0
attrs==21.4.0
beautifulsoup4==4.11.1
certifi==2022.6.15
charset-normalizer==2.1.0
frozenlist==1.3.0
idna==3.3
lxml==4.9.1
multidict==6.0.2
pyTelegramBotAPI==4.6.0
python-dotenv==0.20.0
requests==2.28.1
soupsieve==2.3.2.post1
typing_extensions==4.3.0
urllib3==1.26.10
yarl==1.7.2

### To start a project, it must be cloned with the command:

    git clone git@github.com:Pavelkalininn/async_telegram_parser_bot.git

### Fill in the .env file according to the template:

[example.env](example.env)

### And execute in the work folder:

    docker-compose up -d --build

### After that, when sending the bot the token of which you specified in the .env file of the start command:

    /start

If your id matches the admin id also specified in .env, the update button will be available.
If your IDs do not match, the text with the description of the service and the ability to request the population of the cities of the Moscow region will be returned.

### To stop the container and clear the data, you must enter:

    docker-compose down -v

## Author: [__Pavel Kalinin__](https://github.com/Pavelkalininn)
