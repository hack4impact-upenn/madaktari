# Madaktari

## Hack4Impact Team
- **Santiago Buenahora** (Technical Lead)
- **Abhinav Suri** (Product Manager)
- **Nishita Jain**
- **Roberta Nin Feliz**
- **Sanjay Subramaniam**

## Features Overview
- Application for interested volunteers
- Admin application view, accept, reject capabilities
- Intro page for accepted applicants
- Team search / discovery capabilities
- Algorithmic matching / suggestions
- Team management + scheduling
- Trip preparation resources and reminders
- Email notifications
- Rating and testimonial system (for team and host)
- Admin dashboard to manage volunteer pipeline

___

## Application for interested volunteers

### User Story
- Interested volunteer redirected to external application from Madaktari website.
- User fills out long-form application and submits responses
- User is thanked for the submission and gets an email confirmation

### Technical Requirements
- Admin configurable form
- Form responses accessible via API calls if external
- Form submission prompts an email

### Technical Stack
- [FormBuilder](https://formbuilder.online/): Drag and drop form creation
- Other Relevant Libraries / Resources
	- Google Forms
		- [Form responses to webhooks](https://zapier.com/zapbook/zaps/11086/post-new-google-forms-responses-to-a-webhook-url/)
		- [Query for form responses](https://developers.google.com/apps-script/reference/forms/form-response)
	- Airtable
	- [TypeForm](https://developer.typeform.com/responses/): Collect typeform responses on demand in JSON format
	- [Fireform](http://fireform.org/): Program html forms and see responses in a table using private backend library
	- [MailThisTo](https://www.mailthis.to/): Email API from form submissions
	- [FormsFree](https://formspree.io/): Email form responses to admin after submission
	- [Offline Forms](https://mxb.at/blog/offline-forms/): Offline fallback for forms

## Admin Application View, Accept, Reject Capabilities

### User Story
- Admin can see application responses
- Admin can read application responses
- Admin can accepted and reject an application 
- ? Admin can see previously accepted, or rejected applications
- ? Admin can download application responses as CSV

### Technical Requirements
- Database querying for application responses
- Page population of form responses supporting dynamic questions
- Pagination of form responses for readibility
- Accept and Reject buttons and backend logic
- ? Page population of rejected or accepted responses
- ? Download button and write to CSV logic

### Technical Stack
TODO

## Intro page for accepted applicants

### User Story
- Static Page welcoming users to Madaktari
- ? Intro video by Madaktari clients
- ? Letter by Madaktari Clients
- ? Programmatic Page content
- ? Tutorial overlay of team search, discovery, creation capabilities

### Technical Requirements & Stack
- Static Page
- Content from Madaktari clients

## Team search / discovery capabilities

### User Story
- Volunteer opens team discovery tool
- Volunteer sees profiles of individuals who may be potential comrades
- Volunteer can see information from profiles such as motivation, available dates, specialization, and photo

### Technical Requirements & Tech Stack
- Retrieve Entries from database: See [Flask View Functions](http://flask.pocoo.org/docs/0.12/tutorial/views/)
- Pagination: See [Pagination.js](http://pagination.js.org/)
- User Profile schema for the database

## Algorithmic matching / suggestions
- Defer until we have more information from the client

### Things we need
- Have several varied examples of "optimal teams", "good" teams, and "bad" teams divided by specialization
- Aside from specialization and dates, what other attributes will make a difference for coordinating teams?
- Should we match teams based off of predefined team distributions, or should we account for alternative distributions. In other words, if a host requests specific specializations, is there a way we can input this preference as data to make our algorithm more intelligent or to create a posting targetting specific individuals

## Team management + scheduling
## Trip preparation resources and reminders
## Email notifications
## Rating and testimonial system (for team and host)
## Admin dashboard to manage volunteer pipeline
