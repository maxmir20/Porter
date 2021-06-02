<img width="944" alt="Screen Shot 2021-05-06 at 11 32 00 PM" src="https://user-images.githubusercontent.com/54463500/117407488-7afa1e80-aec3-11eb-8151-ff0792d3ebce.png">

## What is Porter?
Porter is an SMS-based chatbot designed to address local citizens' needs for information. Porter was designed to be easily accessible as a tool for both citizens and government officials, regardless of technical proficiency. From inquiries regarding city departments to parking hours, to general service requests, Porter works just like a trustworthy assistant to help cities save time and get things done. 

## How does Porter work?

#### 1. You send a text message to Porter with your question
No need to download any apps or sign up for any services. Simply text a question like "Where can I get vaccinated" to Porter's number and Porter will get back to you for free**
#### 2. Porter searches for answers from government-hosted data sources 
Using your question, Porter searches for keywords within our internal database,  built directly from the City of Porterville website. 
#### 3. Porter delivers the answer to you
Within seconds, you'll get a text back from Porter containing the most relevant answer and a link for more information. No internet service required, everything done right at your fingertips, literally.

** _T&C:Standard messaging and data rates may apply through your carrier_


## High Level System Architecture

<img width="619" alt="System design" src="https://user-images.githubusercontent.com/54463500/117407021-cbbd4780-aec2-11eb-8723-1787f602e03f.png">

An incoming message from a cellphone first gets piped to Amazon Pinpoint, which furthers it to SNS that acts as a conduit between the SMS service and the Lex engine. Lex, our core chabot engine, evaluates the incoming message and tries to identify its underlying intent by parsing it against a rule set of predefined slots and intents. Once a match is found, Lex then does one of three things:
1. Replies with a static response that is encoded at the Lex level,
2. Invokes a lambda function that pulls data from S3 which is further parsed by Athena to pull live data from a database and packaged into a reply, or
3. Invokes a lambda function that consumes Kendra’s services to use deep learning NLP methods to parse the document store in S3 and reply with an answer, if available. 

If none of the above intents match, Lex invokes a fallback intent that requests the user to rephrase the query. Each component of this entire stack works in unison with every other component and our current design ensures we maintain a closed-loop dialogue flow between the user and our system.

## Features

#### Current

![Current Features](https://user-images.githubusercontent.com/53662441/120541115-5304ba80-c39e-11eb-8911-f6f7e8b78574.png)

Currently, Porter can answer questions regarding directory information, Porterville-specific questions around services or COVID-19, or can direct users to the MyPorterville App for reporting issues.

#### Looking Ahead

![Future Features](https://user-images.githubusercontent.com/53662441/120541293-8cd5c100-c39e-11eb-9e05-5d4c7453f9f5.png)

Looking ahead, Porter was specifically designed on AWS so that it would be compatible with multiple channels, allowing Porter to be hosted on the Porterville government website, official Facebook groups, or even Alexa speakers. Porter can also be easily integrated with multi-lingual translation services. Finally, Porter supports web scrapers that will allow for more dynamic content updates.

## Demo

https://user-images.githubusercontent.com/54463500/117406858-87ca4280-aec2-11eb-9258-456a74425a5c.mp4


https://user-images.githubusercontent.com/54463500/117406861-8a2c9c80-aec2-11eb-8e25-7081fe6f68a4.mp4


https://user-images.githubusercontent.com/54463500/117406863-8ac53300-aec2-11eb-9880-30086cb1fde7.mp4


## Frequently Asked Questions

#### Do you get paid for this?
Nope! We are only a group of grad students trying to create an impact for our capstone project.

#### What kind of questions can I ask Porter?
You can ask questions about the City of Porterville and its city departments, public health information like Covid-19 vaccine availability, directory information, and report issues. For example, you can ask "When is City Hall open", "Where can I get vaccinated?", "How can I get a fire report?". 

#### Where does Porter get the information from?
We pull the data from government-hosted data sources. Although we are not yet able to directly sync information with the official websites, we maintain and update our databases regularly.

#### Are you going to spam me?
Porter is not a subscription-based service and we only send information back if you request first. We are a group of grad students and don’t have ads or solicit business of any kind. Every text costs us money, and your time, so we want to get you the right answer as quickly as possibly.

#### How much does Porter cost?
Porter is free to use. If you text the bot at the number (SMS), you’ll need to pay whatever your mobile carrier charges you for text messages. We’d prefer you don’t send unnecessary SMS as texts cost us a lot of money even if they’re free for you.

#### Does Porter save my number in the system?
Don't worry. Porter is an information dissemination system that uses SMS as a medium to communicate. We do not track your requests, save your cellphone number, or profit off of your personal information.
