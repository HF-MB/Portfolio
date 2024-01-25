# Data Analytics Project – Analyzing "Hotel Booking Demand" Dataset
The original data was published in 2019 in the Journal "Data in Brief".

[DOI Link](https://doi.org/10.1016/j.dib.2018.11.126)

### OVERVIEW
This project looks at data from two different hotels as well as compares the changes in pricing over the year. It unveils interesting insights from the dataset, providing a comprehensive understanding of booking dynamics within these hotels. The dataset, published for educational purposes, offers access to real business data, making it an excellent addition to this portfolio.

### PROJECT MOTIVATION
The motivation behind this project is to illustrate the fundamental economics of the hotel industry using the Hotel Booking Demand dataset.

### OBJECTIVES
The main objectives of the project are:
- To conduct a comparative analysis of the two hotels using Python.
- To show a simple binary classification program to predict why a booking might get canceled.
- To visualize the data and findings in Tableau.

### METHODS
The methodology for this project includes the utilization of Python for the comparative analysis. Additionally, Tableau will be employed for the visualization of the booking data of the Resort Hotel. The project will also incorporate a binary classification program, developed in Python to predict Cancelations given certain variables.

### DATA SOURCE
This data article describes two datasets with hotel demand data. One of the hotels (H1) is a resort hotel and the other (H2) is a city hotel. Both datasets share the same structure, with 31 variables describing 40,060 observations of H1 and 79,330 observations of H2. Each observation represents a hotel booking. The datasets include bookings due to arrive between July 1, 2015, and August 31, 2017, encompassing both arrived and canceled bookings. As this is real hotel data, all data elements pertaining to hotel or customer identification have been removed.

### Results
In the scripts "Analysis", "Map.ipynb" and "Time series.ipynb" I conducted some basic analysis in juyter notebooks. The script "logistic regression.py" tries to forecast data that have a binary label - in this case the "IsCanceled" column. Can we forecast if a booking is going to be canceled based on the other variables we have? The program uses a classification algorithm, that is founded on a function called logistic function.

I also visualized the data of the "Resort Hotel" in Tableau, creating some interesting insights: [Resort Hotel Analysis](https://public.tableau.com/app/profile/hf.mb/viz/ResortHotelBookingAnalysis/)
