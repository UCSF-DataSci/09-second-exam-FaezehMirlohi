#!/bin/zsh

# Generate the ms_data_dirty.csv
python3 generate_dirty_data.py

# Clean the data
# Remove comment lines
# Remove empty lines
# Remove extra commas
# Extract patient_id, visit_date, age, education_level, walking_speed columns (columns 1 tp 5)
# Save the output in the ms_data.csv file
cat ms_data_dirty.csv | grep -v '^#' | sed '/^$/d' | sed 's/,,*/,/g' | cut -d ',' -f1,2,4,5,6 > ms_data.csv 

# Create insurance.lst with unique insurance types
echo -e "Basic\nPremium\nPlatinum" > insurance.lst

# Generate summary
echo "# **Summary**" > readme.md
echo "## **Question 1**" >> readme.md
echo "**Total number of visits:**" >> readme.md
tail -n +2 ms_data.csv | wc -l >> readme.md
echo "" >> readme.md
echo -e "**First few records of ms_data.csv file:**" >> readme.md
echo "" >> readme.md
# Make a table with first 5 rows of the csv file
head -n 1 ms_data.csv | sed 's/^/| /g' | sed 's/$/ |/g' | sed 's/,/ | /g' >> readme.md
echo "|------------|------------|-----|-----------------|---------------|" >> readme.md
head -n 6 ms_data.csv | tail -n +2 | sed 's/^/| /g' | sed 's/$/ |/g' | sed 's/,/ | /g' >> readme.md
