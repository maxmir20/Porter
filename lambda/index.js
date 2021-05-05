
// FOR PinpointConnector 
"use strict";

const AWS = require('aws-sdk');
AWS.config.update({
    region: process.env.Region
});
const pinpoint = new AWS.Pinpoint();
const lex = new AWS.LexRuntime();

var AppId = process.env.PinpointApplicationId;
var BotName = process.env.BotName;
var BotAlias = process.env.BotAlias;

exports.handler = (event, context)  => {
    /*
    * Event info is sent via the SNS subscription: https://console.aws.amazon.com/sns/home
    * 
    * - PinpointApplicationId is your Pinpoint Project ID.
    * - BotName is your Lex Bot name.
    * - BotAlias is your Lex Bot alias (aka Lex function/flow).
    */
    console.log('Received event: ' + event.Records[0].Sns.Message);
    var message = JSON.parse(event.Records[0].Sns.Message);
    var customerPhoneNumber = message.originationNumber;
    var chatbotPhoneNumber = message.destinationNumber;
    var response = message.messageBody.toLowerCase();
    var userId = customerPhoneNumber.replace("+1", "");

    var params = {
        botName: BotName,
        botAlias: BotAlias,
        inputText: response,
        userId: userId
    };
    response = lex.postText(params, function (err, data) {

        if (err) {
            console.log(err, err.stack);
            //return null;
            sendResponse(customerPhoneNumber, chatbotPhoneNumber, "Sorry, I don't have an answer to that at the moment. Please try to rephrase the question, or try another one.");

        }
        else if (data != null && data.message != null) {
            console.log("Lex response: " + data.message);
            sendResponse(customerPhoneNumber, chatbotPhoneNumber, response.response.data.message);
        }
        else {
            console.log("Lex did not send a message back!");
            sendResponse(customerPhoneNumber, chatbotPhoneNumber, "Sorry, I don't have an answer to that at the moment. Please try to rephrase the question, or try another one.");

        }
    });
}

function sendResponse(custPhone, botPhone, response) {
    var paramsSMS = {
        ApplicationId: AppId,
        MessageRequest: {
            Addresses: {
                [custPhone]: {
                    ChannelType: 'SMS'
                }
            },
            MessageConfiguration: {
                SMSMessage: {
                    Body: response,
                    MessageType: "TRANSACTIONAL",
                    OriginationNumber: botPhone
                }
            }
        }
    };
    pinpoint.sendMessages(paramsSMS, function (err, data) {
        if (err) {
            console.log("An error occurred.\n");
            console.log(err, err.stack);
        }
        else if (data['MessageResponse']['Result'][custPhone]['DeliveryStatus'] != "SUCCESSFUL") {
            console.log("Failed to send SMS response:");
            console.log(data['MessageResponse']['Result']);
        }
        else {
            console.log("Successfully sent response via SMS from " + botPhone + " to " + custPhone);
        }
    });
}
