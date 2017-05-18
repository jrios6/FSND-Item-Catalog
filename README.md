# Item Catalog

The goal of this project is to develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Requirements
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)
- [Python ~2.7](https://www.python.org/)

# Setting up authentication services
To run this project, you are also required to provide client_secrets.json and fb_client_secrets.json with your Google and Facebook App IDs in the main folder.

## Setting up the project
1. Download or clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).
2. [Clone](https://github.com/jrios6/FSND-Item-Catalog.git) this repo.
3. Launch the Vagrant VM from inside the *vagrant* folder with:
`vagrant up`
`vagrant ssh`
4. Move this repo inside the *vagrant* folder:
5. `cd /vagrant/item-catalog`
6. Initialize the database with `python catalog_initializer.py`
7. Start Flask Server with `python project.py`
8. Navigate to http://localhost:5000



# API Endpoints
1. /catalog/JSON - List of catalog categories in JSON
2. /catalog/<int:catalog_id>/JSON - List of items in category requested in JSON
