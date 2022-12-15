# SI 507 Final Project: What do New York Times editorial staff follow on Twitter? 

## Project Overview 

In this project, users can get to know which accounts New York Times editorial staff are following on Twitter, what these accounts are talking about (i.e. the most popular words in their recent Tweets), and which articles are relevant on New York Times with the same topic. 

As a start point, I used an external file generated by Henry Copeland that contains information of 300 Twitter accounts followed by NYT editorial staff is (link: https://docs.google.com/spreadsheets/d/1KaaLkR_6xO81f7-DZQFHWfAYy_epfYrpMupTOfKjGOQ/edit#gid=0). I selected accounts from NY and DC and built a tree with location and popularity information. 

As for the interaction part, users can first choose conditions to search accounts, such as "NY" and "high popularity". Then, they can choose one account and the number of frequent words they want to see. The web page will be redirected to display the top n popular words occurring in the recent Tweets of that account. Based on the word list, users can select one keyword to search relevant articles on New York Times. The final result will be a table of New York Times articles with headlines and url included. At this stage, users are free to read articles that they're interested in by clicking the link. 

## API Keys 
Users are required to apply for both [Twitter's](https://developer.twitter.com/en) and [New York Times's](https://developer.nytimes.com/) API keys by registering a developer account on their official websites. With these keys, users need to store the information into a Python file named "Secrets.py" which includes variables "API_Key", "API_Key_Secret", "Bearer_Token", "Access_Token", "Access_Token_Secret" and "NYT_key". 

## Packages Required 
You need the following packages installed. 
- requests
- nltk 
- re
- flask

## Run the Program 
- The main program for the Flask app is main.py. 
- The program to build, save and load tree is userTree.py. 
