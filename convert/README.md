# About CONVERT.py

Use this script to format spreadsheet source file to a better format that can be used to interrogate LLM. 

Input format looks like this: 

Query,Titles,ALL Applied Categories
what is roblox,Roblox - Wikipedia,"navigational, entertainment"
,What is Roblox? Here’s everything you need to know | CNN ...,
,Roblox,


Output format looks like this 
Query,Titles,ALL Applied Categories
what is roblox,Roblox - Wikipedia;What is Roblox? Here’s everything you need to know | CNN ...;Roblox,"navigational, entertainment"


Basically, the tree titles are combined in the same row and separated with ;
The format used for the LLM is query,title;title;title,'category,categor'


