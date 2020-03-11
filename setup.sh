
gsutil cp 'gs://zachf632_senior_project/data.zip' .;
apt get unzip;
unzip data.zip;
rm -r data.zip;
cd data
gsutil cp 'gs://zachf632_senior_project/concat.zip' .;
unzip concat.zip;
rm concat.zip;
cd '../../';
git clone 'https://github.com/zacharyfrederick/Janet.git';
cd 'lib';


#this is a comment you better get this you idiot