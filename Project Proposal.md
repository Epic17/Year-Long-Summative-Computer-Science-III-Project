* Project Title  
  * NeXGen Flight Dispatch  
* Problem Statement/Goal  
  * Airlines, especially major ones, have hundreds to thousands of flights every day. Each flight needs to be managed and kept track of properly for efficiency and safety. The first step to success for each flight starts with dispatching, and that is what my program intends to solve.  
* Target Audience (if applicable)  
  * Passenger and/or freight airline companies  
    * Major  
    * Minor  
    * National  
    * Regional  
    * etc.  
* Proposed Features (minimum of 3 core features)  
  * Monitor real-time flight progress, weather, fuel, and more  
  * Interactive moving map showing current location of every flight  
  * Ability to quickly pull up current and past flight plans  
  * Ability to generate complete flight plan from Airport A to Airport B  
  * and (likely) more  
* Anticipated Technologies/Libraries (e.g., Tkinter for GUI, Flask for web, Pandas for data)  
  * Python (Flask, APIs, etc.)  
  * JavaScript (probably)  
  * HTML (web interface)  
  * CSS (web styling)  
* High-level timeline for the first 9 weeks:  
  * Week 1: Plan organization of the program, such as how each component will communicate with each other, how data will be stored, and more.  
  * Week 2: Research all necessary APIs such as Simbrief and Flightradar24 to understand how to implement them into the program  
  * Week 3: Begin programming of a basic dispatching program that pulls data from real-life flights (given any airline) through Flightradar24/Flightaware API  
  * Week 4: Implement flight plan generation functionality through Simbrief API  
  * Week 5: Build basic front-end of website with static elements  
  * Week 6: Determine how to overlay real-life flight data from API onto interactive map, likely using either Google Maps or OpenStreetMaps API and map data  
  * Week 7: Finish all back-end programming that sends data to front-end (Flask) and receives and parses data from several sources. Additionally, implement data storage to log past flights.  
  * Week 8: Tidy up front-end, moving map, and styling  
  * Week 9: Implement comprehensive error handling for every foreseeable scenario. Anything not 100% finished gets completed here.  
* Initial Research Summary: Brief report on existing solutions or similar projects, and initial findings on chosen technologies.  
  * Popular aviation flight dispatcher software include ForeFlight Dispatch, Maverick Dispatch, PPS Flight Planning, Sabre, Navtech, Lido, Jeppesen, and skyhook. These systems assist with crucial tasks such as flight planning, real-time flight tracking, pilot briefings, weather analysis (METAR, TAF, NOTAMs), and communication. They help dispatchers maintain situational awareness and ensure safe and efficient flight operations.