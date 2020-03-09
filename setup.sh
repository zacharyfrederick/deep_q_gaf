gsutil cp 'gs://zachf632_senior_project/data.zip' .;
apt get unzip;
unzip data.zip;
rm -r data.zip;
cd unzip;
gsutil cp 'gs://zachf632_senior_project/concat.zip' .;
unzip concat.zip;
rm concat.zip;
sudo apt install python3;
pip install 'requirements.txt'
cd 'lib';


#this is a comment you better get this you idiot