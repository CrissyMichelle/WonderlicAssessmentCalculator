# WonderlicAssessmentCalculator
Assistant for determining which questions the Beh Health Spec should ask based on psychometric scores.
## Setting up the app for a local host server
1. Create a new directory for the Wonderlic files and copy and paste them as is.
2. Open Terminal and navigate to your new directory *for example: % cd Desktop/WonderlicFiles*
3. Create a virtual environment for imports *python -m venv venv*
4. Activate the venv before importing all the required modules *source venv/bin/activate*
5. Now that you're in a virtual environment you can import the tech necessary for the app and listed in requirements copy.txt
6. *pip install -r requirements\ copy.txt* (I should've renamed the text file as simply 'requirements.txt' jeez!)
7. Now that the required libraries are downloaded and installed into your venv folder you can run the app local host.
8. Run the app in development mode for easy debugging *FLASK_ENV=development flask run* and navigate to the listed url from your web browser.
9. You can stop hosting the app by typing control + c in your terminal and then exit the venv with *deactivate*
