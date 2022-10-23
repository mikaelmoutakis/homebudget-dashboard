# homebudget-dashboard
A web dashboard for data from the "HomeBudget" expense tracker. 

HomeBudget is a set of expense management software for the home. Its available for Mac, Windows, iOS and Android. 

I was unsatisfied with the built in visualization in the iOS app, so I decided to make a web dashboard. You export the data using wifi, and the dashboard server will import it. 


## Installation using docker
I assume that you already have docker installed. 

1. Clone the repo and switch to it

```
  git clone "https://github.com/mikaelmoutakis/homebudget-dashboard"
  cd homebudget-dashboard
```

2. Create a configuration file by using the config.ini.example as template

``
  cp app/data/config.ini.example app/data/config.ini
``

3. Edit the configuration file with your favorite text editor. Homebudget lets you assign categories and subcategories to each cost item. With homebudget-dashboard you can assign custom priorites to each subcategory. The section "subcategories" in the configuration file contains examples (in Swedish). If you don't know which subcategories you have, you'll find them in an export of your expenses from the iOS app. 

4. Create a docker image and run it as a container. Open "http://localhost:8501" in your webbrowser. 

``
  docker compose up -d
``
