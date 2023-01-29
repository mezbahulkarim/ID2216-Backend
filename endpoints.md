## Auth/user endpoints

POST login
Takes email, password
Returns a user object and jwt token

POST register
Takes email, password, user name
Returns OK/FAIL

POST change username
Takes new username
Returns OK/FAIL

POST change email
Takes new email
Returns OK/FAIL

POST change password
Takes new password
Returns OK/FAIL

POST refresh token
Returns a new JWT token

## Authorized endpoints
If we go with the basic JWT authentication, then there for all of these endpoints the frontend will send the request with the included Authorization header. If the auth header doesnt exist or its expired, the endpoint should not work.
Apart from expiration date, this token can also contain some user information like id or username (I am sure there is some python/fastapi package for easy-handling of the tokens) that later could be used to grab the correct data on the backend - https://jwt.io/ 


GET game activity search
Takes a search string
Returns a list of found items 

GET movie activity search 
Takes a search string
Returns a list of found items

GET books activity search
Takes a search string
Returns a list of found items

GET specific game activity item 
Takes some identifier** of an activity item
Returns all available information about that item

GET user activity item list (ie library)
(Uses the jwt token header)
Returns a list of user activity items

PUT add item to library
Takes some identifier** of an activity item
Return user activity item 

DELETE delete item from library
Takes some identifier** of an activity item
Return OK/FAIL

POST new activity progress
Takes some progress data** and identifier of an activity item
Returns the updates user activity item

GET user wishlist
(Uses the jwt token header)
Returns a list of wishlist items

PUT add item to wishlist
Takes some identifier** of an activity item
Return user wishlist item 

DELETE delete item from wishlist
Takes some identifier** of an activity item
Return OK/FAIL

POST move item from wishlist to library
Takes some identifier** of an activity item
Return user activity item

POST move item from library to wishlist
Takes some identifier** of an activity item
Return wishlist item

** exact format to be decided