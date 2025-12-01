 
Hello,	
 
 
 
 
We’ve had some trouble sending requests in live mode to a webhook endpoint associated with your DreamWedAI account for nine consecutive days. Stripe sends webhook events to your server to notify you of activity in your Stripe account, such as a completed payout or a newly created invoice.	
 
 
 
 
The URL of the failing webhook endpoint is: https://dreamwedai.com/subscriptions/webhook/	
 
 
 
 
We have disabled your webhook endpoint so it will no longer receive these events from Stripe. If you’d like to re-enable your endpoint once you’ve fixed the problem, click the Enable button for the webhook endpoint in your Stripe settings.	
 
 
 
 
Here is the summary of errors we received while attempting to send webhook events:	
 
 
 
 
 
 
 
 
 
 
13 requests had other errors while sending the webhook event.	
 
 
 
 
 
You need to return any status code between HTTP 200 to 299 for Stripe to consider the webhook event successfully delivered.	
 
 
 
 
For more details on these errors and to review your account’s recent activity, you can find the full set of events and request logs on the Dashboard.	
 
 
 
 
For more in-depth information on how to use webhooks, we recommend reviewing our documentation.	
 
 
 
 
— The Stripe team
