# py-salesforce-events

This is a PoC to pull down events from Salesforce via its [Change Data Capture](https://trailhead.salesforce.com/content/learn/modules/change-data-capture) solution. 
It uses the JWT Flow without a refresh token.

This workflow can be used for mirroring events into oather repos as part of an ETL process. Source and sync hooks can be placed into the code with trivial effort.

## Salesforce Prereqs
1. Have a Connected App Made (apps -> app manager)
   - Have it use digital signatures and `api`, `refresh_token` access.
     - this keypair has to be uploaded & the private key stored where the app is running.
   - Have its Permitted Users be preapproval and add the user profile to its Profiles section
   
2. Add objects to the Change Data Capture setup.

3. Edit events
